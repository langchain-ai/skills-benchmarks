"""Unit tests for scaffold/python/tasks.py module.

Tests task loading, TOML parsing, and template rendering.
These tests use fixtures to verify behavior that should have parity with TypeScript.
"""

import pytest

from scaffold.python.tasks import list_tasks, load_task

# =============================================================================
# FIXTURES - Mock task data for consistent testing
# =============================================================================

BASIC_TASK_TOML = """
[metadata]
name = "test-basic"
description = "A basic test task"
difficulty = "easy"
category = "testing"
tags = ["test", "basic"]
default_treatments = ["CONTROL", "TREATMENT_A"]

[template]
required = []

[environment]
description = "Test environment"
dockerfile = "Dockerfile"
timeout_sec = 300

[validation]
validators = ["test_validator"]
"""

TASK_WITH_SETUP_TOML = """
[metadata]
name = "test-setup"
description = "A task with setup config"
difficulty = "medium"
category = "testing"
tags = ["test", "setup"]
default_treatments = ["CONTROL"]

[template]
required = ["dataset_name", "run_id"]

[environment]
description = "Test environment with setup"

[setup.template_vars]
dataset_name = "bench-test-{run_id}"
other_var = "static-value"

[[setup.data]]
pattern = "*_dataset.json"
handler = "upload_datasets"

[[setup.data]]
pattern = "trace_*.jsonl"
handler = "upload_traces"
"""

BASIC_INSTRUCTION = "This is a basic task instruction."
SETUP_INSTRUCTION = "Dataset: {dataset_name}, Run: {run_id}"


@pytest.fixture
def mock_tasks_dir(tmp_path):
    """Create a mock tasks directory with test tasks."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    # Create basic task
    basic_task = tasks_dir / "test-basic"
    basic_task.mkdir()
    (basic_task / "task.toml").write_text(BASIC_TASK_TOML)
    (basic_task / "instruction.md").write_text(BASIC_INSTRUCTION)

    # Create task with setup
    setup_task = tasks_dir / "test-setup"
    setup_task.mkdir()
    (setup_task / "task.toml").write_text(TASK_WITH_SETUP_TOML)
    (setup_task / "instruction.md").write_text(SETUP_INSTRUCTION)

    return tasks_dir


# =============================================================================
# TESTS
# =============================================================================


class TestListTasks:
    """Tests for list_tasks function."""

    def test_returns_list(self, mock_tasks_dir):
        """list_tasks returns a list."""
        tasks = list_tasks(mock_tasks_dir)
        assert isinstance(tasks, list)

    def test_returns_sorted_names(self, mock_tasks_dir):
        """Task names are sorted alphabetically."""
        tasks = list_tasks(mock_tasks_dir)
        assert tasks == sorted(tasks)

    def test_finds_valid_tasks(self, mock_tasks_dir):
        """list_tasks finds tasks with task.toml and instruction.md."""
        tasks = list_tasks(mock_tasks_dir)
        assert "test-basic" in tasks
        assert "test-setup" in tasks

    def test_ignores_invalid_dirs(self, mock_tasks_dir):
        """list_tasks ignores directories without required files."""
        # Create invalid task (missing instruction.md)
        invalid = mock_tasks_dir / "invalid-task"
        invalid.mkdir()
        (invalid / "task.toml").write_text("[metadata]\nname = 'invalid'")

        tasks = list_tasks(mock_tasks_dir)
        assert "invalid-task" not in tasks

    def test_nonexistent_dir_returns_empty(self, tmp_path):
        """Non-existent directory returns empty list."""
        tasks = list_tasks(tmp_path / "nonexistent")
        assert tasks == []


class TestLoadTask:
    """Tests for load_task function."""

    def test_load_basic_task(self, mock_tasks_dir):
        """Load a basic task with minimal config."""
        task = load_task("test-basic", mock_tasks_dir)
        assert task.name == "test-basic"
        assert task.config.category == "testing"
        assert task.config.difficulty == "easy"
        assert "CONTROL" in task.default_treatments
        assert "TREATMENT_A" in task.default_treatments

    def test_load_task_with_setup(self, mock_tasks_dir):
        """Load a task with setup config (template_vars, data_handlers)."""
        task = load_task("test-setup", mock_tasks_dir)
        assert task.name == "test-setup"

        # Check template vars
        template_vars = task.config.setup.template_vars
        assert "dataset_name" in template_vars
        assert template_vars["dataset_name"] == "bench-test-{run_id}"
        assert template_vars["other_var"] == "static-value"

        # Check data handlers
        handlers = task.config.setup.data_handlers
        assert len(handlers) == 2
        assert handlers[0].pattern == "*_dataset.json"
        assert handlers[0].handler == "upload_datasets"
        assert handlers[1].pattern == "trace_*.jsonl"
        assert handlers[1].handler == "upload_traces"

    def test_task_not_found(self, mock_tasks_dir):
        """Load non-existent task raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Task not found"):
            load_task("nonexistent-task", mock_tasks_dir)

    def test_task_path_set(self, mock_tasks_dir):
        """Task path is correctly set."""
        task = load_task("test-basic", mock_tasks_dir)
        assert task.path == mock_tasks_dir / "test-basic"


class TestTemplateRendering:
    """Tests for template rendering."""

    def test_render_prompt_no_vars(self, mock_tasks_dir):
        """Render prompt with no required variables."""
        task = load_task("test-basic", mock_tasks_dir)
        prompt = task.render_prompt()
        assert prompt == BASIC_INSTRUCTION

    def test_render_prompt_with_vars(self, mock_tasks_dir):
        """Render prompt with required variables."""
        task = load_task("test-setup", mock_tasks_dir)
        prompt = task.render_prompt(
            dataset_name="bench-test-abc123",
            run_id="abc123",
        )
        assert "bench-test-abc123" in prompt
        assert "abc123" in prompt

    def test_render_prompt_missing_vars(self, mock_tasks_dir):
        """Render prompt with missing required variables raises KeyError."""
        task = load_task("test-setup", mock_tasks_dir)
        with pytest.raises(KeyError, match="Missing required template variables"):
            task.render_prompt()  # Missing dataset_name, run_id


class TestTaskConfig:
    """Tests for TaskConfig parsing."""

    def test_metadata_fields(self, mock_tasks_dir):
        """Metadata fields are parsed correctly."""
        task = load_task("test-basic", mock_tasks_dir)
        assert task.config.name == "test-basic"
        assert task.config.description == "A basic test task"
        assert task.config.difficulty == "easy"
        assert task.config.category == "testing"
        assert "test" in task.config.tags
        assert "basic" in task.config.tags

    def test_default_treatments(self, mock_tasks_dir):
        """Default treatments list is parsed."""
        task = load_task("test-basic", mock_tasks_dir)
        assert isinstance(task.default_treatments, list)
        assert len(task.default_treatments) == 2
        assert all(isinstance(t, str) for t in task.default_treatments)

    def test_template_required(self, mock_tasks_dir):
        """Template required fields are parsed."""
        task = load_task("test-setup", mock_tasks_dir)
        assert "dataset_name" in task.config.template_required
        assert "run_id" in task.config.template_required


class TestSetupConfig:
    """Tests for setup configuration parsing."""

    def test_template_vars_parsed(self, mock_tasks_dir):
        """Template vars are parsed from [setup.template_vars]."""
        task = load_task("test-setup", mock_tasks_dir)
        template_vars = task.config.setup.template_vars

        assert len(template_vars) == 2
        assert template_vars["dataset_name"] == "bench-test-{run_id}"
        assert template_vars["other_var"] == "static-value"

    def test_template_vars_substitution(self, mock_tasks_dir):
        """Template vars can have {run_id} replaced."""
        task = load_task("test-setup", mock_tasks_dir)
        template_vars = task.config.setup.template_vars

        result = template_vars["dataset_name"].replace("{run_id}", "xyz789")
        assert result == "bench-test-xyz789"
        assert "{run_id}" not in result

    def test_data_handlers_parsed(self, mock_tasks_dir):
        """Data handlers are parsed from [[setup.data]]."""
        task = load_task("test-setup", mock_tasks_dir)
        handlers = task.config.setup.data_handlers

        assert len(handlers) == 2
        for handler in handlers:
            assert hasattr(handler, "pattern")
            assert hasattr(handler, "handler")
            assert hasattr(handler, "args")
            assert isinstance(handler.pattern, str)
            assert isinstance(handler.handler, str)

    def test_empty_setup_config(self, mock_tasks_dir):
        """Tasks without setup config have empty defaults."""
        task = load_task("test-basic", mock_tasks_dir)
        assert task.config.setup.template_vars == {}
        assert task.config.setup.data_handlers == []
