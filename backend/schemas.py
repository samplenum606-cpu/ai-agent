from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class AgentRequest(BaseModel):
    prompt: str = Field(..., description="Instruction for the EDA agent")
    dataset_name: Optional[str] = Field(
        None,
        description="Optional dataset key or path for analysis. Uses sample data if omitted.",
    )

class ToolOutput(BaseModel):
    tool_name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    prompt: str
    dataset_name: str
    result: str
    insights_count: int
    selected_tool: str
    analysis_plan: str
    fallback_reason: Optional[str] = None
    tools_used: List[str]
    memory_hits: int
    error_recovery_loops: int
    execution_log: List[str]

class DatasetMetrics(BaseModel):
    dataset_name: str
    prompt: str
    tools_used: List[str]
    memory_hits: int
    error_recovery_loops: int
    success: bool
    task_completed: bool
    insights_count: int
    result: str

class EvaluationResponse(BaseModel):
    datasets: List[DatasetMetrics]
    total_datasets: int
    task_completion_rate: float
    code_execution_accuracy: float
    average_error_recovery_loops: float
    average_memory_hits: float
    note: str
