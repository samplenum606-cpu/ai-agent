from typing import Dict, List

from agent_engine import AgentEngine

EVALUATION_DATASETS = [
    "sales",
    "customer",
    "hospital",
    "marketing",
    "time_series",
]

class DatasetEvaluation:
    def __init__(self, dataset_name: str, response: Dict[str, any]):
        self.dataset_name = dataset_name
        self.prompt = response["prompt"]
        self.tools_used = response["tools_used"]
        self.memory_hits = response["memory_hits"]
        self.error_recovery_loops = response["error_recovery_loops"]
        self.execution_log = response["execution_log"]
        self.result = response["result"]
        self.success = not response["result"].startswith("Agent failed")
        self.insights = [line for line in self.result.split("\n") if line.strip()]
        self.task_completed = len(self.insights) > 0 and self.success

    def to_dict(self) -> Dict[str, any]:
        return {
            "dataset_name": self.dataset_name,
            "prompt": self.prompt,
            "tools_used": self.tools_used,
            "memory_hits": self.memory_hits,
            "error_recovery_loops": self.error_recovery_loops,
            "success": self.success,
            "task_completed": self.task_completed,
            "insights_count": len(self.insights),
            "result": self.result,
        }

class EvaluationResult:
    def __init__(self, dataset_results: List[DatasetEvaluation]):
        self.dataset_results = dataset_results
        self.total = len(dataset_results)
        self.task_completion_rate = sum(1 for r in dataset_results if r.task_completed) / self.total
        self.code_execution_accuracy = sum(1 for r in dataset_results if r.success) / self.total
        self.average_error_recovery_loops = sum(r.error_recovery_loops for r in dataset_results) / self.total
        self.average_memory_hits = sum(r.memory_hits for r in dataset_results) / self.total

    def to_dict(self) -> Dict[str, any]:
        return {
            "datasets": [r.to_dict() for r in self.dataset_results],
            "total_datasets": self.total,
            "task_completion_rate": round(self.task_completion_rate, 3),
            "code_execution_accuracy": round(self.code_execution_accuracy, 3),
            "average_error_recovery_loops": round(self.average_error_recovery_loops, 3),
            "average_memory_hits": round(self.average_memory_hits, 3),
            "note": "Evaluation uses the agent core across 5 representative datasets."
        }


def run_evaluation(engine: AgentEngine, prompt: str = "Perform an exploratory data analysis and summarize the main insights.") -> EvaluationResult:
    results = []
    for dataset_name in EVALUATION_DATASETS:
        response = engine.run(prompt, dataset_name)
        results.append(DatasetEvaluation(dataset_name, response))
    return EvaluationResult(results)
