from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent_core import Agent
from llm_gateway import OllamaClient
from typing import Optional, List, Any, Dict
import os
import tools_fs
import json
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OpenAigent")

app = FastAPI(title="Open-Aigent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str
    model: Optional[str] = "llama3"
    ollama_url: Optional[str] = None
    history: Optional[List[str]] = []
    objective: Optional[str] = None



class ApprovalRequest(BaseModel):
    tool: str
    args: Dict[str, Any]

class WorkspaceRequest(BaseModel):
    path: str

@app.get("/")
def health():
    logger.info("Health check OK")
    return {"status": "online", "project": "Open-Aigent"}

@app.get("/api/models")
def get_models(ollama_url: Optional[str] = None):
    logger.info(f"Fetching models from: {ollama_url or 'default'}")
    models = OllamaClient.fetch_models(ollama_url)
    return {"models": models}

@app.get("/api/files")
def get_files(path: str = "."):
    return {"files": tools_fs.list_files_json(path)}

@app.get("/api/file-content")
def get_file_content(path: str):
    # Pass as keyword argument to match the new flexible tool signature
    content = tools_fs.read_file(path=path)
    return {"content": content}

@app.post("/api/workspace")
def set_workspace(request: WorkspaceRequest):
    abs_path = os.path.abspath(request.path)
    tools_fs.set_workspace_root(abs_path)
    return {"status": "success", "workspace": abs_path}

@app.post("/run-task")
async def run_task(request: TaskRequest):
    logger.info(f"Task: {request.task} | Model: {request.model}")
    agent = Agent(model=request.model, ollama_url=request.ollama_url)
    
    async def stream():
        try:
            for step in agent.run_task_full_loop(request.task, request.history, request.objective):

                yield f"data: {json.dumps(step)}\n\n"
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Stream Error: {e}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")

@app.post("/api/execute-tool")
async def execute_tool(request: ApprovalRequest):
    try:
        if request.tool in tools_fs.TOOLS:
            result = tools_fs.TOOLS[request.tool](**request.args)
            return {"status": "success", "result": result}
        raise HTTPException(status_code=400, detail="Tool not found")
    except Exception as e:
        logger.error(f"Tool Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
