# indream-client

Official Python client for the Indream Open API.

- API docs: https://docs.indream.ai
- Supports Python 3.10+

## Installation

```bash
pip install indream-client
```

## Quick Start

```python
from indream import IndreamClient

client = IndreamClient(api_key="YOUR_INDREAM_API_KEY")

created = client.exports.create(
    {
        "editorState": editor_state,
        "ratio": "9:16",
        "scale": 0.6,
        "fps": 30,
        "format": "mp4",
    }
)

task = client.exports.wait(created.task_id)
print(task.status, task.output_url, task.duration_seconds, task.billed_standard_seconds)
```

## Editor State Checks

`client.editor.validate(...)` and `client.exports.create(...)` run local editor-state schema checks before request dispatch.
If `editorState` is invalid, the SDK raises `ValidationError` immediately.
