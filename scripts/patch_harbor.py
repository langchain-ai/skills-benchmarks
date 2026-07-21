"""Apply local fixes to the installed Harbor package.

Harbor is pinned to 0.18.0 (see LANGSMITH_SANDBOX_PLAN.md). A few fixes needed for
our runs are not yet in a Harbor release, so this script patches the installed
package in place. It is idempotent and safe to re-run.

  Fix #1: size the snapshot builder from the task's cpu/memory config (the default
          builder is too small to build large images).
  Fix #3: boot the run sandbox by snapshot id (dockerfile-built snapshots are
          stored untagged, so name lookup 404s). Already fixed on upstream main.
  Fix #4: wire a custom OpenAI base URL (the LangSmith LLM Gateway) as a named
          codex provider with supports_websockets=false, so codex uses the HTTP
          Responses transport instead of the WebSocket one the gateway does not
          allow-list (501).
  Fix #5: forward ANTHROPIC_BASE_URL / OPENAI_BASE_URL into the langgraph
          (deepagents) container so the graph's LLM calls route through the
          gateway instead of calling the provider directly (401).

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

# Each patch: (relative-file, name, marker-if-already-applied, original, replacement).
PATCHES: list[tuple[str, str, str, str, str]] = [
    (
        "environments/langsmith.py",
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
        "environments/langsmith.py",
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
        "environments/langsmith.py",
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
    (
        "agents/installed/codex.py",
        "fix#4 codex gateway provider (no websockets)",
        "supports_websockets",
        """        # codex 0.118.0 only honors openai_base_url from config.toml, not the env var.
        config_toml_block = ""
        if openai_base_url:
            config_toml_block = (
                '\\ncat >>"$CODEX_HOME/config.toml" <<TOML\\n'
                'openai_base_url = "${OPENAI_BASE_URL}"\\n'
                "TOML"
            )""",
        """        # A custom base URL (e.g. the LangSmith LLM Gateway) is configured as a
        # named provider so we can also set supports_websockets=false: codex
        # defaults to the Responses API WebSocket transport, which the gateway
        # does not allow-list (501), so we pin it to HTTP/SSE. codex only honors
        # provider config from config.toml, not env vars.
        config_toml_block = ""
        if openai_base_url:
            config_toml_block = (
                '\\ncat >>"$CODEX_HOME/config.toml" <<TOML\\n'
                'model_provider = "gateway"\\n'
                "[model_providers.gateway]\\n"
                'name = "Gateway"\\n'
                'base_url = "${OPENAI_BASE_URL}"\\n'
                'env_key = "OPENAI_API_KEY"\\n'
                'wire_api = "responses"\\n'
                'supports_websockets = false\\n'
                "TOML"
            )""",
    ),
    (
        "agents/installed/langgraph.py",
        "fix#5 langgraph forward base URLs",
        "ANTHROPIC_BASE_URL",
        """_FORWARDED_ENV_VARS = (
    # Model provider keys
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",""",
        """_FORWARDED_ENV_VARS = (
    # Model provider base URLs (e.g. the LangSmith LLM Gateway)
    "ANTHROPIC_BASE_URL",
    "OPENAI_BASE_URL",
    # Model provider keys
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",""",
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

    rel_files = sorted({rel for rel, *_ in PATCHES})
    any_written = False
    for rel in rel_files:
        target = pkg_dir / rel
        text = target.read_text()
        original = text
        for _rel, name, marker, old, new in PATCHES:
            if _rel != rel:
                continue
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
            any_written = True

    if not any_written:
        print("Nothing to do; all patches already present.")


if __name__ == "__main__":
    main()
