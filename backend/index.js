import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json({ limit: '2mb' }));

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Autonomous EDA Agent backend is running' });
});

app.post('/api/agent', async (req, res) => {
  const { prompt } = req.body;
  if (!prompt || typeof prompt !== 'string') {
    return res.status(400).json({ error: 'prompt is required and must be a string' });
  }

  // TODO: connect this endpoint to the actual EDA agent engine.
  const result = {
    prompt,
    result: 'هذه استجابة تجريبية. سيتم تنفيذ تحليل البيانات هنا لاحقاً.',
    note: 'البنية الأساسية جاهزة. أضف منطق الوكيل هنا.'
  };

  res.json(result);
});

app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
