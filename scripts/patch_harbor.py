"""Apply local LangSmith-sandbox fixes to the installed Harbor package.

Harbor is pinned to 0.18.0 (see LANGSMITH_SANDBOX_PLAN.md). Two fixes needed for
LangSmith sandbox runs are not yet in a Harbor release, so this script patches the
installed package in place. It is idempotent and safe to re-run.

  Fix #1: size the snapshot builder from the task's cpu/memory config (the default
          builder is too small to build large images).
  Fix #3: boot the run sandbox by snapshot id (dockerfile-built snapshots are
          stored untagged, so name lookup 404s). Already fixed on upstream main.

Run after installing/upgrading Harbor:

    uv tool install 'harbor[langsmith]' --python 3.13
    uv run python scripts/patch_harbor.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

EXPECTED_VERSION = "0.18.0"

# Each patch: (name, marker-if-already-applied, original text, replacement text).
PATCHES: list[tuple[str, str, str, str]] = [
    (
        "fix#1 builder cpu/memory",
        "vcpus=self._effective_cpus,",
        """                on_build_log=self._log_dockerfile_build_line,
                timeout=max(1, int(self.task_env_config.build_timeout_sec)),
                headers=self._langsmith_client_headers(),
            )""",
        """                on_build_log=self._log_dockerfile_build_line,
                timeout=max(1, int(self.task_env_config.build_timeout_sec)),
                # Size the builder from the task's cpu/memory config; the default
                # builder is too small for large images (matches run-sandbox sizing).
                vcpus=self._effective_cpus,
                mem_bytes=(
                    self._effective_memory_mb * _ONE_MIB
                    if self._effective_memory_mb is not None
                    else None
                ),
                headers=self._langsmith_client_headers(),
            )""",
    ),
    (
        "fix#3a snapshot_id in payload",
        'payload["snapshot_id"] = self._active_snapshot_id',
        """        if snapshot_name:
            payload["snapshot_name"] = snapshot_name
        if (cpus := self._effective_cpus) is not None:""",
        """        # Boot by snapshot id: dockerfile-built snapshots are stored untagged,
        # but create_sandbox resolves a bare name to "<name>:latest" and 404s.
        # (Backport of the upstream-main fix to the 0.18.0 release.)
        if self._active_snapshot_id:
            payload["snapshot_id"] = self._active_snapshot_id
        elif snapshot_name:
            payload["snapshot_name"] = snapshot_name
        if (cpus := self._effective_cpus) is not None:""",
    ),
    (
        "fix#3b snapshot_id in create_sandbox",
        "snapshot_id=payload.get(\"snapshot_id\"),",
        """            return client.create_sandbox(
                snapshot_name=payload.get("snapshot_name"),
                name=payload["name"],""",
        """            return client.create_sandbox(
                snapshot_id=payload.get("snapshot_id"),
                snapshot_name=payload.get("snapshot_name"),
                name=payload["name"],""",
    ),
]


def _locate_harbor() -> tuple[Path, str]:
    exe = shutil.which("harbor")
    if not exe:
        sys.exit("harbor executable not found on PATH. Install it first.")
    interp = sys.executable
    try:
        first = Path(exe).read_text().splitlines()[0]
        if first.startswith("#!"):
            interp = first[2:].strip()
    except (UnicodeDecodeError, OSError):
        pass
    probe = (
        "import harbor, os, importlib.metadata as m; "
        "print(os.path.dirname(harbor.__file__)); print(m.version('harbor'))"
    )
    out = subprocess.run(
        [interp, "-c", probe], capture_output=True, text=True
    )
    if out.returncode != 0:
        sys.exit(f"Could not import harbor via {interp}:\n{out.stderr.strip()}")
    pkg_dir, version = out.stdout.split()
    return Path(pkg_dir), version


def main() -> None:
    pkg_dir, version = _locate_harbor()
    if version != EXPECTED_VERSION:
        sys.exit(
            f"Harbor {version} installed, but these patches target {EXPECTED_VERSION}. "
            f"Pin it: uv tool install 'harbor[langsmith]=={EXPECTED_VERSION}' --python 3.13"
        )

    target = pkg_dir / "environments" / "langsmith.py"
    text = target.read_text()
    original = text
    for name, marker, old, new in PATCHES:
        if marker in text:
            print(f"  skip  {name} (already applied)")
        elif old in text:
            text = text.replace(old, new, 1)
            print(f"  apply {name}")
        else:
            sys.exit(
                f"  ERROR {name}: anchor not found in {target}. "
                "The file may have changed; update scripts/patch_harbor.py."
            )

    if text != original:
        target.write_text(text)
        print(f"Patched {target}")
    else:
        print("Nothing to do; all patches already present.")


if __name__ == "__main__":
    main()
