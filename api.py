import json
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent import run_agent

app = FastAPI()


class InvestigationRequest(BaseModel):
    device_id: Optional[str] = None
    question: str
    previous_response_id: Optional[str] = None


@app.post("/investigate")
def investigate(request: InvestigationRequest):
    if request.device_id:
        prompt = (
            f"Device: {request.device_id}\n"
            f"Question: {request.question}"
        )
    else:
        prompt = request.question

    def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'status', 'message': 'Investigation complete. Preparing response...'})}\n\n"

            for event in run_agent(
                prompt,
                previous_response_id=request.previous_response_id,
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except Exception:
            yield f"data: {json.dumps({'type': 'error', 'message': 'The investigation failed. Please try again.'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
