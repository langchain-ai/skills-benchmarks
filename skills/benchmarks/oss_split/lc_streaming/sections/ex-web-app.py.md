FastAPI endpoint with SSE streaming:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
import json

app = FastAPI()

agent = create_agent(
    model="gpt-4.1",
    tools=[search_tool],
)

@app.post("/api/chat")
async def chat(messages: list):
    async def generate():
        try:
            async for mode, chunk in agent.astream(
                {"messages": messages},
                stream_mode=["messages", "updates"],
            ):
                if mode == "messages":
                    token, metadata = chunk
                    if token.content:
                        # Send token to client
                        yield f"data: {json.dumps({'type': 'token', 'content': token.content})}\n\n"
                elif mode == "updates":
                    # Send step update to client
                    yield f"data: {json.dumps({'type': 'step', 'data': str(chunk)})}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as error:
            yield f"data: {json.dumps({'type': 'error', 'message': str(error)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```
