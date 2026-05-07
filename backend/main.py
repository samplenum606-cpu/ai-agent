from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from schemas import AgentRequest, AgentResponse, EvaluationResponse
from agent_engine import AgentEngine
from evaluation import run_evaluation

app = FastAPI(title="Autonomous EDA Agent Backend", version="0.1.0")
engine = AgentEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Autonomous EDA Agent backend is running"}

@app.post("/api/agent", response_model=AgentResponse)
def agent_endpoint(request: AgentRequest):
    try:
        agent_response = engine.run(request.prompt, request.dataset_name)
        return AgentResponse(**agent_response)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/evaluate", response_model=EvaluationResponse)
def evaluate(prompt: str = Query(
    "Perform an exploratory data analysis and summarize the main insights.",
    description="Instruction prompt used for each evaluation dataset.")
):
    try:
        evaluation = run_evaluation(engine, prompt)
        return EvaluationResponse(**evaluation.to_dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
