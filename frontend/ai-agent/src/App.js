import { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('اكتب وصفاً أو رابط ملف البيانات ثم اضغط "تشغيل"');
  const [loading, setLoading] = useState(false);
  const [evaluationLoading, setEvaluationLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setOutput('جارٍ الإرسال إلى الخادم...');

    try {
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setOutput(data.result ?? JSON.stringify(data, null, 2));
    } catch (error) {
      setOutput(
        `الخادم غير متوفّر حالياً. تأكد من تشغيل backend في مجلد backend.\nالخطأ: ${error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluate = async () => {
    setEvaluationLoading(true);
    setOutput('جارٍ تشغيل تقييم الأداء...');

    try {
      const response = await fetch('/api/evaluate');
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setOutput(JSON.stringify(data, null, 2));
    } catch (error) {
      setOutput(
        `فشل تقييم الأداء. تأكد من تشغيل backend وتشغيل نقطة /api/evaluate.\nالخطأ: ${error.message}`
      );
    } finally {
      setEvaluationLoading(false);
    }
  };

  return (
    <div className="App">
      <main className="App-shell">
        <section className="App-card">
          <h1>Autonomous EDA Agent</h1>
          <p>واجهة تفاعلية لتجربة وكيل تحليل البيانات الذاتية.</p>

          <label htmlFor="agentPrompt">ما هو المطلوب من الوكيل؟</label>
          <textarea
            id="agentPrompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="مثال: Summarize sales trends in the sample dataset"
          />
          <div className="App-help">
            <p>مثال آخر: <strong>Analyze missing values and correlations in the marketing dataset</strong></p>
            <p>يمكنك أيضاً إضافة <code>dataset_name=sample</code> في الطلب أو تمرير الاسم عبر JSON عند استخدام API مباشرة.</p>
          </div>

          <button onClick={handleSubmit} disabled={loading || prompt.trim().length === 0}>
            {loading ? 'جارٍ التنفيذ...' : 'تشغيل التحليل'}
          </button>
          <button
            className="evaluation-button"
            onClick={handleEvaluate}
            disabled={evaluationLoading}
          >
            {evaluationLoading ? 'جارٍ التقييم...' : 'تشغيل تقييم الأداء'}
          </button>

          <div className="App-result">
            <h2>النتيجة</h2>
            <pre>{output}</pre>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
