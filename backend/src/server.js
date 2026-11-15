require('dotenv').config();
const express = require('express');
const cors = require('cors');
const apiRoutes = require('./routes/api');

const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS for frontend clients
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Body parser
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Mount API router
app.use('/api', apiRoutes);

// Serve React production build if available
const distPath = path.join(__dirname, '../../frontend/dist');
if (fs.existsSync(distPath)) {
  console.log(`📦 Serving React frontend from ${distPath}`);
  app.use(express.static(distPath));
  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/api')) return next();
    res.sendFile(path.join(distPath, 'index.html'));
  });
} else {
  // Health / Welcome endpoint if frontend dist not built
  app.get('/', (req, res) => {
    res.json({
      service: 'Student Insight AI — Node.js Backend Gateway',
      version: '1.0.0',
      status: 'online',
      endpoints: {
        health: '/api/health',
        predict_single: 'POST /api/predict',
        predict_batch: 'POST /api/predict/batch',
        metrics: 'GET /api/model/metrics',
        feature_importance: 'GET /api/model/feature-importance',
        config: 'GET /api/model/config',
        chat: 'POST /api/chat/message',
        sample_csv: 'GET /api/sample-csv'
      }
    });
  });
}

// Global Error Handler
app.use((err, req, res, next) => {
  console.error('[Global Error]', err.stack || err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message || 'An unexpected error occurred'
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`=================================================`);
  console.log(`🚀 Student Insight AI Backend running on port ${PORT}`);
  console.log(`🔗 Local: http://localhost:${PORT}`);
  console.log(`🤖 Python ML Service: ${process.env.PYTHON_ML_SERVICE_URL || 'http://127.0.0.1:8000'}`);
  console.log(`☁️ Python Fallback: ${process.env.PYTHON_ML_FALLBACK_URL}`);
  console.log(`✨ Groq LLM Model: ${process.env.GROQ_MODEL || 'qwen/qwen3.8-27b'}`);
  console.log(`=================================================`);
});
