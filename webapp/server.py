"""FastAPI server for the 'Crazy-Busy Itd.' service desk demo.

Serves a single HTML page and one JSON endpoint that runs the triage agent, so
attendees can see what gets sent to the model and what comes back.

    uv run python webapp/server.py        # then open http://localhost:8000
                                          # interactive API docs at /docs
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
sys.path.insert(0, str(HERE.parent))  # make the project root importable

from triage.agent import classify_summary  # noqa: E402

app = FastAPI(title="Crazy-Busy Itd. Service Desk")


class ClassifyRequest(BaseModel):
    """Only the ticket text is needed; subject/tags/etc. from the form are ignored."""

    text: str = ""


@app.get("/")
def index() -> FileResponse:
    return FileResponse(INDEX)


@app.post("/api/classify")
def classify(req: ClassifyRequest) -> JSONResponse:
    text = req.text.strip()
    if not text:
        return JSONResponse(status_code=400, content={"error": "empty ticket"})
    try:
        started = time.time()
        result = classify_summary(text)
        result["elapsed_s"] = round(time.time() - started, 2)
        return JSONResponse(content=result)
    except Exception as exc:  # surface model/endpoint errors to the page
        return JSONResponse(status_code=500, content={"error": str(exc)})


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    print(f"Crazy-Busy Itd. service desk running at http://localhost:{port}  (Ctrl+C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
