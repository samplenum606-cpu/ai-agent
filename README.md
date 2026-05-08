# Autonomous EDA Agent

واجهة تفاعلية لتجربة وكيل تحليل البيانات الذاتية (EDA Agent).

## محتويات المشروع

- `backend/` - الخادم الخلفي المكتوب بـ Python وFastAPI.
- `frontend/ai-agent/` - واجهة المستخدم المكتوبة بـ React.

## هل المشروع جاهز؟

نعم، المشروع يعمل حالياً ويمكن تشغيله محلياً.
- الخلفية تستقبل طلبات إلى `/api/agent` و`/api/evaluate`.
- الواجهة تتصل بالخلفية عبر البروكسي إلى `http://localhost:5000`.

## متطلبات التشغيل

- Python 3.12.x
- Node.js و npm

## خطوات التثبيت والتشغيل

### 1. تثبيت الخلفية

افتح ترمنال في مجلد `backend`:

```powershell
cd d:\project-s\ai-agent\backend
python -m pip install -r requirements.txt
```

### 2. تشغيل الخلفية

من نفس المجلد:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

إذا نجح، ستجد الخلفية تعمل على:

```
http://127.0.0.1:5000
```

### 3. تثبيت الواجهة

افتح ترمنال جديد في مجلد `frontend/ai-agent`:

```powershell
cd d:\project-s\ai-agent\frontend\ai-agent
npm install
```

### 4. تشغيل الواجهة

من نفس المجلد:

```powershell
npm start
```

ثم افتح المتصفح على:

```
http://localhost:3000
```

## ملاحظات

- إذا كان منفذ `3000` محجوزاً، ستطلب React اختيار منفذ آخر.
- إذا واجهت أي خطأ في الاتصال، تأكد أن الخلفية تعمل على `127.0.0.1:5000` قبل فتح الواجهة.
- يمكنك تشغيل تقييم الأداء من الواجهة عبر زر `تشغيل تقييم الأداء` أو من الخلفية باستخدام:

```powershell
cd d:\project-s\ai-agent\backend
python -c "from evaluation import run_evaluation; from agent_engine import AgentEngine; engine=AgentEngine(); print(run_evaluation(engine).to_dict())"
```

## دليل تثبيت وتشغيل بالعربية

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

### كيف تتأكد أن كل شيء يعمل

1. افتح المتصفح على `http://localhost:3000`.
2. يجب أن تكون الواجهة قادرة على الاتصال بالخلفية على `http://127.0.0.1:5000`.
3. إذا كنت تريد التحقق من الخلفية فقط، افتح:

```text
http://127.0.0.1:5000/api/health
```

## كيفية استخدام المشروع بعد التشغيل

1. افتح الواجهة على `http://localhost:3000`.
2. في مربع النص الرئيسي، اكتب سؤالاً واضحاً عن تحليل البيانات، مثل:
   - `Summarize sales trends in the sample dataset`
   - `Find correlation between profit and sales`
   - `Analyze missing values and correlations in the marketing dataset`
3. اضغط زر `تشغيل التحليل`.
4. ستعرض الواجهة نتيجة التحليل تحت عنوان `النتيجة`.
5. لتشغيل تقييم الأداء للأمثلة المدمجة، اضغط زر `تشغيل تقييم الأداء`.

### نصائح لاستخدام أفضل

- إذا أردت اختبار مجموعة بيانات محددة، اذكر اسم `dataset_name` في الطلب أو حدد اسم الملف في الكود الخلفي.
  - مثال: `Analyze the sample dataset and summarize the main insights. dataset_name=sample`
  - أو في الطلب البرمجي المباشر إلى API:

```json
{
  "prompt": "Analyze the sample dataset and summarize the main insights.",
  "dataset_name": "sample"
}
```
- إذا كنت تريد تحليلًا عامًّا، استخدم:
  - `Perform an exploratory data analysis and summarize the main insights.`
- إذا كانت النتائج تظهر ما يشبه `Strong correlation found...` فهذا يعني أن الوكيل وجد علاقات قوية بين الأرقام.

## بنية المشروع

- `backend/main.py` - نقطة دخول FastAPI.
- `backend/agent_engine.py` - منطق الوكيل وتحليل البيانات.
- `backend/schemas.py` - نماذج Pydantic للطلب والاستجابة.
- `frontend/ai-agent/src/App.js` - واجهة المستخدم.

## إذا أردت تحسينًا إضافياً

يمكن تحسين العرض في الواجهة ليصبح أكثر وضوحاً بدلاً من عرض JSON خام.
