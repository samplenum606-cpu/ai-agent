# Autonomous EDA Agent

This project is a locally runnable autonomous exploratory data analysis agent.

> Documentation in this README has been written manually for this project.

## Project structure

- `backend/` - Python backend using FastAPI.
- `frontend/ai-agent/` - React frontend.

## What this project does

- The backend accepts requests at `/api/agent` and `/api/evaluate`.
- The frontend connects to the backend via proxy at `http://localhost:5000`.

## Requirements

- Python 3.12.x
- Node.js and npm

## Installation and running (English)

### 1. Install backend dependencies

Open a terminal in the `backend` folder:

```cmd
cd /d d:\project-s\ai-agent\backend
python -m pip install -r requirements.txt
```

### 2. Run backend

From the same folder:

```cmd
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

If the backend starts successfully, it will be available at:

```text
http://127.0.0.1:5000
```

### 3. Install frontend dependencies

Open a new terminal in `frontend/ai-agent`:

```cmd
cd /d d:\project-s\ai-agent\frontend\ai-agent
npm install
```

### 4. Run frontend

From the same folder:

```cmd
npm start
```

Then open your browser at:

```text
http://localhost:3000
```

## Notes

- If port `3000` is already used, React will prompt to use another available port.
- If you experience connection errors, make sure the backend is running at `127.0.0.1:5000`.
- To run evaluation from the backend directly:

```cmd
cd /d d:\project-s\ai-agent\backend
python -c "from evaluation import run_evaluation; from agent_engine import AgentEngine; engine = AgentEngine(); print(run_evaluation(engine).to_dict())"
```

## Guide in Arabic

### تشغيل الخلفية باستخدام PowerShell

```powershell
cd d:\project-s\ai-agent\backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

### تشغيل الخلفية باستخدام cmd

```cmd
cd /d d:\project-s\ai-agent\backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

### تشغيل الواجهة باستخدام PowerShell

```powershell
cd d:\project-s\ai-agent\frontend\ai-agent
npm install
npm start
```

### تشغيل الواجهة باستخدام cmd

```cmd
cd /d d:\project-s\ai-agent\frontend\ai-agent
npm install
npm start
```

### How to verify everything is working

1. Open the browser at `http://localhost:3000`.
2. The frontend should connect to the backend at `http://127.0.0.1:5000`.
3. To check the backend alone, open:

```text
http://127.0.0.1:5000/api/health
```

## How to use the project after startup

1. Open the frontend at `http://localhost:3000`.
2. In the main input box, type a clear data analysis question, such as:
   - `Summarize sales trends in the sample dataset`
   - `Find correlation between profit and sales`
   - `Analyze missing values and correlations in the marketing dataset`
3. Press `Run Analysis`.
4. The result will appear under the `Result` section.
5. To run the built-in evaluation, press `Run Evaluation`.

### Better usage tips

- To test a specific dataset, include `dataset_name` in the prompt or set it in backend code.
  - Example: `Analyze the sample dataset and summarize the main insights. dataset_name=sample`
  - Or use the direct API request:

```json
{
  "prompt": "Analyze the sample dataset and summarize the main insights.",
  "dataset_name": "sample"
}
```
- For a generic analysis prompt, use:
  - `Perform an exploratory data analysis and summarize the main insights.`
- If the result contains `Strong correlation found...`, the agent identified strong numeric relationships.

## Project files

- `backend/main.py` - FastAPI entry point.
- `backend/agent_engine.py` - Agent logic and data analysis.
- `backend/schemas.py` - Pydantic request and response models.
- `frontend/ai-agent/src/App.js` - React app.

## Optional improvement

The frontend can be improved to present results in a more user-friendly layout instead of raw JSON.
