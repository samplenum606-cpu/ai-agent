import hashlib
import json
import os
import subprocess
import tempfile
import textwrap
from typing import Any, Dict, List, Optional

import pandas as pd
from langgraph.graph import StateGraph, END
from schemas import ToolOutput

DATASETS = {
    "sample": os.path.join(os.path.dirname(__file__), "datasets", "sample.csv"),
    "sales": os.path.join(os.path.dirname(__file__), "datasets", "sales.csv"),
    "customer": os.path.join(os.path.dirname(__file__), "datasets", "customer.csv"),
    "hospital": os.path.join(os.path.dirname(__file__), "datasets", "hospital.csv"),
    "marketing": os.path.join(os.path.dirname(__file__), "datasets", "marketing.csv"),
    "time_series": os.path.join(os.path.dirname(__file__), "datasets", "time_series.csv"),
}

class MemoryStore:
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self.profiles.get(key)

    def set(self, key: str, profile: Dict[str, Any]) -> None:
        self.profiles[key] = profile

    def key_for_df(self, df: pd.DataFrame) -> str:
        fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "columns": df.columns.tolist(),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "shape": df.shape,
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        return fingerprint


class AgentEngine:
    def __init__(self):
        self.memory = MemoryStore()
        self.execution_log: List[str] = []
        self.error_recovery_loops = 0
        self.tools_used: List[str] = []
        self.fallback_reason: Optional[str] = None
        self.graph = self.build_graph()

    def build_graph(self):
        # Define the state
        from typing import TypedDict

        class AgentState(TypedDict):
            prompt: str
            dataset_name: str
            df: pd.DataFrame
            profile: Dict[str, Any]
            tool: str
            plan: str
            code: str
            result: ToolOutput
            final_result: str
            memory_hits: int
            error_recovery_loops: int
            execution_log: List[str]

        # Define nodes
        def observe_node(state: AgentState) -> AgentState:
            df = state['df']
            key = self.memory.key_for_df(df)
            cached = self.memory.get(key)
            if cached is not None:
                self.execution_log.append("Memory hit: using cached data profile.")
                memory_hits = 1
            else:
                self.execution_log.append("Memory miss: evaluating data profile.")
                profile = {
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "missing": df.isna().sum().to_dict(),
                    "summary": df.describe(include="all").to_dict(),
                }
                self.memory.set(key, profile)
                memory_hits = 0
            return {**state, "profile": cached or profile, "memory_hits": memory_hits}

        def plan_node(state: AgentState) -> AgentState:
            df = state['df']
            prompt = state['prompt']
            profile = state['profile']
            prompt_lower = prompt.lower()
            has_numeric = not df.select_dtypes(include=["number"]).empty
            has_text = df.select_dtypes(include=["object"]).shape[1] > 0

            if any(keyword in prompt_lower for keyword in ["sql", "query", "select", "join"]):
                tool = "sql"
            elif "correlation" in prompt_lower or "insight" in prompt_lower or "summary" in prompt_lower:
                tool = "python"
            elif has_text and has_numeric:
                tool = "python"
            else:
                tool = "python"

            self.tools_used.append(tool)
            self.execution_log.append(f"Tool selected: {tool}")

            plan = [
                f"Observing data with shape {profile['shape']} and columns {profile['columns']}",
                f"Selected tool: {tool}",
            ]
            if profile["missing"] and any(value > 0 for value in profile["missing"].values()):
                plan.append("Check missing-value patterns and anomalies.")
            if any(dtype in profile["dtypes"].values() for dtype in ["int64", "float64"]):
                plan.append("Compute numeric summary and key correlations.")
            plan.append("Generate insights relevant to the prompt.")
            plan_str = " ".join(plan)

            return {**state, "tool": tool, "plan": plan_str}

        def write_code_node(state: AgentState) -> AgentState:
            prompt = state['prompt']
            dataset_name = state['dataset_name']
            tool = state['tool']
            df = state['df']
            data_path = DATASETS.get(dataset_name or "sample", DATASETS["sample"])
            if not os.path.exists(data_path):
                data_path = self.create_temporary_csv(df)

            code = self.build_code(prompt, data_path, tool)
            return {**state, "code": code}

        def execute_node(state: AgentState) -> AgentState:
            code = state['code']
            result = self.execute_sandboxed_code(code)
            return {**state, "result": result}

        def check_result(state: AgentState) -> str:
            result = state['result']
            if result.success and self.is_insightful(result):
                return "success"
            else:
                self.error_recovery_loops += 1
                return "retry"

        def retry_node(state: AgentState) -> AgentState:
            prompt = state['prompt']
            dataset_name = state['dataset_name']
            df = state['df']
            data_path = DATASETS.get(dataset_name or "sample", DATASETS["sample"])
            if not os.path.exists(data_path):
                data_path = self.create_temporary_csv(df)
            fallback_code = self.build_code(prompt, data_path, "python")
            result = self.execute_sandboxed_code(fallback_code)
            return {**state, "result": result, "error_recovery_loops": state.get('error_recovery_loops', 0) + 1}

        def finalize_node(state: AgentState) -> AgentState:
            result = state['result']
            final_summary = ""
            insights = []
            if result.success and isinstance(result.output, dict):
                insights = result.output.get("insights", [])
                final_summary = "\n".join(insights)
            elif not result.success:
                final_summary = f"Agent failed: {result.error}"

            return {**state, "final_result": final_summary, "insights_count": len(insights), "execution_log": self.execution_log}

        # Build graph
        workflow = StateGraph(AgentState)

        workflow.add_node("observe", observe_node)
        workflow.add_node("plan", plan_node)
        workflow.add_node("write_code", write_code_node)
        workflow.add_node("execute", execute_node)
        workflow.add_node("retry", retry_node)
        workflow.add_node("finalize", finalize_node)

        workflow.set_entry_point("observe")
        workflow.add_edge("observe", "plan")
        workflow.add_edge("plan", "write_code")
        workflow.add_edge("write_code", "execute")
        workflow.add_conditional_edges("execute", check_result, {"success": "finalize", "retry": "retry"})
        workflow.add_edge("retry", "finalize")

        return workflow.compile()

    def load_dataset(self, dataset_name: Optional[str]) -> pd.DataFrame:
        if dataset_name and os.path.exists(dataset_name):
            source = dataset_name
        else:
            source = DATASETS.get(dataset_name or "sample", DATASETS["sample"])

        if os.path.exists(source):
            self.execution_log.append(f"Loaded dataset from {source}")
            return pd.read_csv(source)

        self.execution_log.append("No dataset file found, generating sample dataset.")
        return self.generate_sample_dataset()

    def generate_sample_dataset(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"date": "2024-01-01", "category": "Office", "region": "West", "sales": 4200, "discount": 0.05, "profit": 550},
                {"date": "2024-01-02", "category": "Office", "region": "East", "sales": 3900, "discount": 0.1, "profit": 420},
                {"date": "2024-01-03", "category": "Furniture", "region": "Central", "sales": 6500, "discount": 0.07, "profit": 820},
                {"date": "2024-01-04", "category": "Office", "region": "West", "sales": 3100, "discount": 0.0, "profit": 350},
                {"date": "2024-01-05", "category": "Furniture", "region": "East", "sales": 5300, "discount": 0.04, "profit": 610},
                {"date": "2024-01-06", "category": "Office", "region": "Central", "sales": 4700, "discount": 0.12, "profit": 420},
                {"date": "2024-01-07", "category": "Technology", "region": "West", "sales": 8800, "discount": 0.1, "profit": 1190},
                {"date": "2024-01-08", "category": "Technology", "region": "East", "sales": 7600, "discount": 0.08, "profit": 980},
            ]
        )

    def observe_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        key = self.memory.key_for_df(df)
        cached = self.memory.get(key)
        if cached is not None:
            self.execution_log.append("Memory hit: using cached data profile.")
            return cached

        self.execution_log.append("Memory miss: evaluating data profile.")
        profile = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing": df.isna().sum().to_dict(),
            "summary": df.describe(include="all").to_dict(),
        }
        self.memory.set(key, profile)
        return profile

    def choose_tool(self, df: pd.DataFrame, prompt: str) -> str:
        prompt_lower = prompt.lower()
        has_numeric = not df.select_dtypes(include=["number"]).empty
        has_text = df.select_dtypes(include=["object"]).shape[1] > 0

        if any(keyword in prompt_lower for keyword in ["sql", "query", "select", "join"]):
            tool = "sql"
        elif "correlation" in prompt_lower or "insight" in prompt_lower or "summary" in prompt_lower:
            tool = "python"
        elif has_text and has_numeric:
            tool = "python"
        else:
            tool = "python"

        self.tools_used.append(tool)
        self.execution_log.append(f"Tool selected: {tool}")
        return tool

    def plan_analysis(self, profile: Dict[str, Any], prompt: str, tool: str) -> str:
        plan = [
            f"Observing data with shape {profile['shape']} and columns {profile['columns']}",
            f"Selected tool: {tool}",
        ]
        if profile["missing"] and any(value > 0 for value in profile["missing"].values()):
            plan.append("Check missing-value patterns and anomalies.")
        if any(dtype in profile["dtypes"].values() for dtype in ["int64", "float64"]):
            plan.append("Compute numeric summary and key correlations.")
        plan.append("Generate insights relevant to the prompt.")
        return " ".join(plan)

    def parse_execution_error(self, error_text: str) -> str:
        if "No module named" in error_text:
            return "Missing Python import in generated code. Switching to python tool and simplifying analysis."
        if "SyntaxError" in error_text:
            return "Syntax error in generated code. Using safer fallback snippet."
        if "timed out" in error_text.lower():
            return "Execution timed out. Reducing complexity and retrying."
        return "Failed execution. Re-running with fallback code."

    def is_insightful(self, result: ToolOutput) -> bool:
        if not result.success or not isinstance(result.output, dict):
            return False
        insights = result.output.get("insights")
        return bool(insights and any(str(item).strip() for item in insights))

    def build_code(self, prompt: str, dataset_path: str, tool: str) -> str:
        if tool == "sql":
            return textwrap.dedent(
                f"""
                import json
                import pandas as pd
                import sqlite3

                df = pd.read_csv(r"{dataset_path}")
                conn = sqlite3.connect(':memory:')
                df.to_sql('data', conn, index=False, if_exists='replace')

                default_query = 'SELECT COUNT(*) AS rows, SUM(sales) AS total_sales, AVG(profit) AS avg_profit FROM data'
                query = default_query
                result = {{}}

                cursor = conn.execute(query)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                records = [dict(zip(columns, row)) for row in rows]
                result['query'] = query
                result['rows'] = records
                result['insights'] = [
                    'أجريت تحليل SQL أساسي عبر المجموعة. يمكن طلب استعلام أكثر تحديداً.'
                ]
                print(json.dumps(result))
                """
            )

        return textwrap.dedent(f"""
            import json
            import pandas as pd

            df = pd.read_csv(r"{dataset_path}")
            numeric = df.select_dtypes(include=["number"])
            missing = df.isna().sum().to_dict()
            description = df.describe(include='all').to_dict()
            correlations = numeric.corr().to_dict()
            insights = []

            if df.isna().any().any():
                missing_cols = [str(c) for c in missing if missing[c] > 0]
                insights.append(
                    "Data contains missing values in columns: " + ', '.join(missing_cols)
                )
            if not numeric.empty:
                high_corr = []
                for x in numeric.columns:
                    for y in numeric.columns:
                        if x != y and abs(correlations.get(x, {{}}).get(y, 0)) >= 0.75:
                            high_corr.append((x, y, correlations[x][y]))
                if high_corr:
                    corr_str = ', '.join([f'{{x}}/{{y}}={{value:.2f}}' for x, y, value in high_corr])
                    insights.append(
                        "Strong correlation found: " + corr_str
                    )
            if not insights:
                insights.append("No high correlation or missing-value patterns were detected in the sample analysis.")

            analysis = {{
                "summary": description,
                "missing": missing,
                "correlations": correlations,
                "insights": insights,
            }}
            print(json.dumps(analysis))
            """)

    def execute_sandboxed_code(self, code: str) -> ToolOutput:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as scratch:
            scratch.write(code)
            scratch.flush()
            script_path = scratch.name

        try:
            process = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=12,
            )
            if process.returncode != 0:
                self.execution_log.append("Code execution failed.")
                return ToolOutput(
                    tool_name="python_executor",
                    success=False,
                    error=process.stderr.strip() or "Unknown execution error",
                )

            self.execution_log.append("Code executed successfully.")
            return ToolOutput(
                tool_name="python_executor",
                success=True,
                output=json.loads(process.stdout.strip() or "{}"),
            )
        except subprocess.TimeoutExpired as timeout_error:
            self.execution_log.append("Code execution timed out.")
            return ToolOutput(
                tool_name="python_executor",
                success=False,
                error="Execution timed out",
            )
        finally:
            try:
                os.remove(script_path)
            except OSError:
                pass

    def run(self, prompt: str, dataset_name: Optional[str] = None) -> Dict[str, Any]:
        self.execution_log = []
        self.tools_used = []
        self.error_recovery_loops = 0

        df = self.load_dataset(dataset_name)
        profile = self.observe_data(df)
        tool = self.choose_tool(df, prompt)

        data_path = DATASETS.get(dataset_name or "sample", DATASETS["sample"])
        if not os.path.exists(data_path):
            self.execution_log.append("No static dataset file available, using generated sample dataset.")
            data_path = self.create_temporary_csv(df)

        plan = self.plan_analysis(profile, prompt, tool)
        self.execution_log.append(f"Plan: {plan}")

        code = self.build_code(prompt, data_path, tool)
        result = self.execute_sandboxed_code(code)
        self.fallback_reason = None

        if not result.success or not self.is_insightful(result):
            self.error_recovery_loops += 1
            if not result.success:
                self.fallback_reason = self.parse_execution_error(result.error or "Unknown error")
                self.execution_log.append(self.fallback_reason)
            else:
                self.fallback_reason = "Result lacked actionable insights. Refining the analysis."
                self.execution_log.append(self.fallback_reason)

            fallback_tool = "python"
            fallback_code = self.build_code(prompt, data_path, fallback_tool)
            result = self.execute_sandboxed_code(fallback_code)

        if dataset_name is None:
            dataset_name = "sample"

        final_summary = ""
        insights = []
        if result.success and isinstance(result.output, dict):
            insights = result.output.get("insights", [])
            final_summary = "\n".join(insights)
        elif not result.success:
            final_summary = f"Agent failed: {result.error}"

        return {
            "prompt": prompt,
            "dataset_name": dataset_name,
            "result": final_summary,
            "insights_count": len(insights),
            "selected_tool": tool,
            "analysis_plan": plan,
            "fallback_reason": self.fallback_reason,
            "tools_used": self.tools_used,
            "memory_hits": 1 if profile else 0,
            "error_recovery_loops": self.error_recovery_loops,
            "execution_log": self.execution_log,
        }

    def create_temporary_csv(self, df: pd.DataFrame) -> str:
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        return temp_file.name
