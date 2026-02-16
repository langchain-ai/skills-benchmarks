"""Real LangSmith API data fixtures for testing.

This data was captured from real LangSmith API responses to ensure
our mocks accurately reflect actual API behavior.

Data captured on 2026-02-16 from project "skills".
"""

from datetime import datetime

# ============================================================================
# TRACE DATA - Captured from real API responses
# ============================================================================

# Sample trace list output (from `traces list --limit 3 --format json`)
SAMPLE_TRACES_LIST = [
    {
        "run_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
        "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
        "name": "LangGraph",
        "run_type": "chain",
        "parent_run_id": None,
        "start_time": "2026-02-15T19:16:43.144899",
        "end_time": "2026-02-15T19:16:46.686558",
    },
    {
        "run_id": "019c62bb-92cc-71b0-97e7-8e2b283a432c",
        "trace_id": "019c62bb-92cc-71b0-97e7-8e2b283a432c",
        "name": "LangGraph",
        "run_type": "chain",
        "parent_run_id": None,
        "start_time": "2026-02-15T19:16:25.932649",
        "end_time": "2026-02-15T19:16:29.558129",
    },
    {
        "run_id": "019c62bb-695f-70e2-a62a-e8fec7118137",
        "trace_id": "019c62bb-695f-70e2-a62a-e8fec7118137",
        "name": "LangGraph",
        "run_type": "chain",
        "parent_run_id": None,
        "start_time": "2026-02-15T19:16:15.327190",
        "end_time": "2026-02-15T19:16:15.554152",
    },
]


# Full trace hierarchy (from `traces get <trace-id> --format json`)
SAMPLE_TRACE_GET = {
    "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
    "run_count": 7,
    "runs": [
        {
            "run_id": "019c62bb-de6a-7f61-a2a4-97366b55cc8d",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "ChatAnthropic",
            "run_type": "llm",
            "parent_run_id": "019c62bb-de69-7120-9c06-4e570c78062f",
            "start_time": "2026-02-15T19:16:45.290780",
            "end_time": "2026-02-15T19:16:46.683732",
        },
        {
            "run_id": "019c62bb-de69-7120-9c06-4e570c78062f",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "model",
            "run_type": "chain",
            "parent_run_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "start_time": "2026-02-15T19:16:45.289146",
            "end_time": "2026-02-15T19:16:46.685606",
        },
        {
            "run_id": "019c62bb-de67-76a1-aabf-136119aa18a6",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "calculator",
            "run_type": "tool",
            "parent_run_id": "019c62bb-de66-7fe1-92e0-d45d12b5bf69",
            "start_time": "2026-02-15T19:16:45.287767",
            "end_time": "2026-02-15T19:16:45.288323",
        },
        {
            "run_id": "019c62bb-de66-7fe1-92e0-d45d12b5bf69",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "tools",
            "run_type": "chain",
            "parent_run_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "start_time": "2026-02-15T19:16:45.286820",
            "end_time": "2026-02-15T19:16:45.288848",
        },
        {
            "run_id": "019c62bb-d650-7a42-be20-fd0b7e97ccc2",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "ChatAnthropic",
            "run_type": "llm",
            "parent_run_id": "019c62bb-d60c-78e0-acdc-0bd71a1bf4d0",
            "start_time": "2026-02-15T19:16:43.216157",
            "end_time": "2026-02-15T19:16:45.284788",
        },
        {
            "run_id": "019c62bb-d60c-78e0-acdc-0bd71a1bf4d0",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "model",
            "run_type": "chain",
            "parent_run_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "start_time": "2026-02-15T19:16:43.148540",
            "end_time": "2026-02-15T19:16:45.286248",
        },
        {
            "run_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
            "name": "LangGraph",
            "run_type": "chain",
            "parent_run_id": None,
            "start_time": "2026-02-15T19:16:43.144899",
            "end_time": "2026-02-15T19:16:46.686558",
        },
    ],
}


# ============================================================================
# RUNS DATA - Captured from real API responses with full metadata
# ============================================================================

# Sample runs with metadata (from `runs list --include-metadata`)
SAMPLE_RUNS_WITH_METADATA = [
    {
        "run_id": "019c62bb-de6a-7f61-a2a4-97366b55cc8d",
        "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
        "name": "ChatAnthropic",
        "run_type": "llm",
        "parent_run_id": "019c62bb-de69-7120-9c06-4e570c78062f",
        "start_time": "2026-02-15T19:16:45.290780",
        "end_time": "2026-02-15T19:16:46.683732",
        "status": "success",
        "duration_ms": 1392,
        "custom_metadata": {
            "LANGSMITH_ENDPOINT": "https://api.smith.langchain.com",
            "LANGSMITH_PROJECT": "skills",
            "LANGSMITH_TRACING": "true",
            "checkpoint_ns": "model:d812b23f-f416-c89c-52cb-7c61bb2d2c35",
            "langgraph_checkpoint_ns": "model:d812b23f-f416-c89c-52cb-7c61bb2d2c35",
            "langgraph_node": "model",
            "langgraph_path": ["__pregel_pull", "model"],
            "langgraph_step": 3,
            "langgraph_triggers": ["branch:to:model"],
            "ls_max_tokens": 8192,
            "ls_model_name": "claude-3-5-haiku-20241022",
            "ls_model_type": "chat",
            "ls_provider": "anthropic",
            "ls_run_depth": 2,
            "ls_temperature": 0.0,
        },
        "token_usage": {
            "prompt_tokens": 516,
            "completion_tokens": 61,
            "total_tokens": 577,
        },
        "costs": {
            "prompt_cost": "0.0004128",
            "completion_cost": "0.000244",
            "total_cost": "0.0006568",
        },
    },
    {
        "run_id": "019c62bb-de69-7120-9c06-4e570c78062f",
        "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
        "name": "model",
        "run_type": "chain",
        "parent_run_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
        "start_time": "2026-02-15T19:16:45.289146",
        "end_time": "2026-02-15T19:16:46.685606",
        "status": "success",
        "duration_ms": 1396,
        "custom_metadata": {
            "LANGSMITH_ENDPOINT": "https://api.smith.langchain.com",
            "LANGSMITH_PROJECT": "skills",
            "LANGSMITH_TRACING": "true",
            "langgraph_checkpoint_ns": "model:d812b23f-f416-c89c-52cb-7c61bb2d2c35",
            "langgraph_node": "model",
            "langgraph_path": ["__pregel_pull", "model"],
            "langgraph_step": 3,
            "langgraph_triggers": ["branch:to:model"],
            "ls_run_depth": 1,
        },
        "token_usage": {
            "prompt_tokens": 516,
            "completion_tokens": 61,
            "total_tokens": 577,
        },
        "costs": {
            "prompt_cost": "0.0004128",
            "completion_cost": "0.000244",
            "total_cost": "0.0006568",
        },
    },
    {
        "run_id": "019c62bb-de67-76a1-aabf-136119aa18a6",
        "trace_id": "019c62bb-d608-74c3-88bd-54d51db3d4a7",
        "name": "calculator",
        "run_type": "tool",
        "parent_run_id": "019c62bb-de66-7fe1-92e0-d45d12b5bf69",
        "start_time": "2026-02-15T19:16:45.287767",
        "end_time": "2026-02-15T19:16:45.288323",
        "status": "success",
        "duration_ms": 0,
        "custom_metadata": {
            "LANGSMITH_ENDPOINT": "https://api.smith.langchain.com",
            "LANGSMITH_PROJECT": "skills",
            "LANGSMITH_TRACING": "true",
            "checkpoint_ns": "tools:6fc554f8-5014-28cf-65f8-6e518652722a",
            "langgraph_checkpoint_ns": "tools:6fc554f8-5014-28cf-65f8-6e518652722a",
            "langgraph_node": "tools",
            "langgraph_path": ["__pregel_push", 0, False],
            "langgraph_step": 2,
            "langgraph_triggers": ["__pregel_push"],
            "ls_run_depth": 2,
        },
        "token_usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
        "costs": {
            "prompt_cost": None,
            "completion_cost": None,
            "total_cost": None,
        },
    },
]


# ============================================================================
# DATASET DATA - Captured from real API responses
# ============================================================================

# Sample datasets list (from `list-datasets`)
SAMPLE_DATASETS = [
    {
        "id": "7951866e-3433-49xx-xxxx-xxxxxxxxxxxx",
        "name": "shipping-support-golden",
        "description": "Test queries exposing context confusion patterns w",
        "example_count": 10,
    },
    {
        "id": "29b5bdde-60d7-41xx-xxxx-xxxxxxxxxxxx",
        "name": "Email Agent Notebook: Trajectory",
        "description": "",
        "example_count": 5,
    },
    {
        "id": "13fc661f-2a09-4axx-xxxx-xxxxxxxxxxxx",
        "name": "Email Agent: Trajectory",
        "description": "",
        "example_count": 16,
    },
    {
        "id": "d448c458-c63e-47xx-xxxx-xxxxxxxxxxxx",
        "name": "kb-agent-golden-set",
        "description": "Golden dataset for KB retrieval agent evaluation w",
        "example_count": 15,
    },
]


# Sample dataset examples (from `show "Email Agent: Trajectory"`)
SAMPLE_DATASET_EXAMPLES = [
    {
        "inputs": {
            "email_input": {
                "to": "Robert Xu <Robert@company.com>",
                "author": "Marketing Team <marketing@openai.com>",
                "subject": "Newsletter: New Model from OpenAI",
                "email_thread": "Hi Robert,\n\nWe're excited to announce...",
            }
        },
        "outputs": {"trajectory": []},
    },
    {
        "inputs": {
            "email_input": {
                "to": "Robert Xu <Robert@company.com>",
                "author": "Project Team <project@company.com>",
                "subject": "Joint presentation next month",
                "email_thread": "Hi Robert,\n\nThe leadership team has asked us...",
            }
        },
        "outputs": {
            "trajectory": [
                "check_calendar_availability",
                "schedule_meeting",
                "write_email",
                "done",
            ]
        },
    },
]


# ============================================================================
# MOCK RUN OBJECTS - For use in unit tests
# ============================================================================


class MockRun:
    """Mock LangSmith Run object matching real API structure."""

    def __init__(
        self,
        id: str,
        trace_id: str,
        name: str,
        run_type: str,
        parent_run_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        inputs: dict | None = None,
        outputs: dict | None = None,
        status: str = "success",
        error: str | None = None,
        extra: dict | None = None,
    ):
        self.id = id
        self.trace_id = trace_id
        self.name = name
        self.run_type = run_type
        self.parent_run_id = parent_run_id
        self.start_time = start_time
        self.end_time = end_time
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.status = status
        self.error = error
        self.extra = extra or {}


class MockDataset:
    """Mock LangSmith Dataset object matching real API structure."""

    def __init__(
        self,
        id: str,
        name: str,
        description: str = "",
        example_count: int = 0,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.example_count = example_count


class MockExample:
    """Mock LangSmith Example object matching real API structure."""

    def __init__(self, inputs: dict, outputs: dict):
        self.inputs = inputs
        self.outputs = outputs


# ============================================================================
# TEST FIXTURES - Pre-built mock objects for common test scenarios
# ============================================================================


def create_mock_runs_from_real_data() -> list[MockRun]:
    """Create MockRun objects from real API data."""
    return [
        MockRun(
            id="019c62bb-d608-74c3-88bd-54d51db3d4a7",
            trace_id="019c62bb-d608-74c3-88bd-54d51db3d4a7",
            name="LangGraph",
            run_type="chain",
            parent_run_id=None,
            start_time=datetime(2026, 2, 15, 19, 16, 43, 144899),
            end_time=datetime(2026, 2, 15, 19, 16, 46, 686558),
            inputs={"messages": [["user", "What is 2 + 2?"]]},
            outputs={"messages": [["ai", "The result of 2 + 2 is 4."]]},
        ),
        MockRun(
            id="019c62bb-de66-7fe1-92e0-d45d12b5bf69",
            trace_id="019c62bb-d608-74c3-88bd-54d51db3d4a7",
            name="tools",
            run_type="chain",
            parent_run_id="019c62bb-d608-74c3-88bd-54d51db3d4a7",
            start_time=datetime(2026, 2, 15, 19, 16, 45, 286820),
            end_time=datetime(2026, 2, 15, 19, 16, 45, 288848),
        ),
        MockRun(
            id="019c62bb-de67-76a1-aabf-136119aa18a6",
            trace_id="019c62bb-d608-74c3-88bd-54d51db3d4a7",
            name="calculator",
            run_type="tool",
            parent_run_id="019c62bb-de66-7fe1-92e0-d45d12b5bf69",
            start_time=datetime(2026, 2, 15, 19, 16, 45, 287767),
            end_time=datetime(2026, 2, 15, 19, 16, 45, 288323),
            inputs={"expression": "2 + 2"},
            outputs={"result": "4"},
        ),
    ]


def create_mock_datasets_from_real_data() -> list[MockDataset]:
    """Create MockDataset objects from real API data."""
    return [
        MockDataset(
            id="7951866e-3433-49xx-xxxx-xxxxxxxxxxxx",
            name="shipping-support-golden",
            description="Test queries exposing context confusion patterns",
            example_count=10,
        ),
        MockDataset(
            id="13fc661f-2a09-4axx-xxxx-xxxxxxxxxxxx",
            name="Email Agent: Trajectory",
            description="",
            example_count=16,
        ),
    ]


def create_mock_examples_from_real_data() -> list[MockExample]:
    """Create MockExample objects from real API data."""
    return [
        MockExample(
            inputs={
                "email_input": {
                    "to": "Robert Xu <Robert@company.com>",
                    "author": "Marketing Team <marketing@openai.com>",
                    "subject": "Newsletter: New Model from OpenAI",
                    "email_thread": "Hi Robert,\n\nWe're excited to announce...",
                }
            },
            outputs={"trajectory": []},
        ),
        MockExample(
            inputs={
                "email_input": {
                    "to": "Robert Xu <Robert@company.com>",
                    "author": "Project Team <project@company.com>",
                    "subject": "Joint presentation next month",
                    "email_thread": "Hi Robert,\n\nThe leadership team has asked...",
                }
            },
            outputs={
                "trajectory": [
                    "check_calendar_availability",
                    "schedule_meeting",
                    "write_email",
                    "done",
                ]
            },
        ),
    ]
