const express = require('express');
const router = express.Router();
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const { PROJECT_KNOWLEDGE_BASE } = require('../config/knowledgeBase');

const os = require('os');

// Setup multer for temporary CSV uploads in OS temp directory
const upload = multer({ dest: os.tmpdir() });

const PYTHON_LOCAL_URL = process.env.PYTHON_ML_SERVICE_URL || 'http://127.0.0.1:8000';
const PYTHON_FALLBACK_URL = process.env.PYTHON_ML_FALLBACK_URL || 'https://students-performance-at-risk-prediction.onrender.com';
const GROQ_API_KEY = process.env.GROQ_API_KEY || '';
const GROQ_MODEL = process.env.GROQ_MODEL || 'qwen/qwen3.8-27b';

// Helper to query Python ML service with fallback
async function callPythonML(endpoint, data = null, method = 'GET') {
  try {
    const localRes = await axios({
      method,
      url: `${PYTHON_LOCAL_URL}${endpoint}`,
      data,
      timeout: 3000
    });
    return { data: localRes.data, source: 'local' };
  } catch (localErr) {
    console.warn(`[Node API] Local Python service at ${PYTHON_LOCAL_URL} unreachable (${localErr.message}). Attempting fallback to ${PYTHON_FALLBACK_URL}...`);
    try {
      const fallbackRes = await axios({
        method,
        url: `${PYTHON_FALLBACK_URL}${endpoint}`,
        data,
        timeout: 45000
      });
      return { data: fallbackRes.data, source: 'cloud_fallback' };
    } catch (fallbackErr) {
      console.error(`[Node API] Both local and fallback ML service failed: ${fallbackErr.message}`);
      throw new Error(`ML Service unavailable: Local (${localErr.message}), Fallback (${fallbackErr.message})`);
    }
  }
}

// -----------------------------------------------------------------------------
// 1. Health Probe
// -----------------------------------------------------------------------------
router.get('/health', async (req, res) => {
  let pythonStatus = 'unreachable';
  let pythonDetails = null;
  let source = 'none';

  try {
    const mlHealth = await callPythonML('/health');
    pythonStatus = mlHealth.data.status || 'healthy';
    pythonDetails = mlHealth.data;
    source = mlHealth.source;
  } catch (err) {
    pythonStatus = 'offline';
  }

  res.json({
    status: 'healthy',
    backend: 'Node.js Express',
    port: process.env.PORT || 5000,
    groq_configured: Boolean(GROQ_API_KEY),
    groq_model: GROQ_MODEL,
    python_ml_status: pythonStatus,
    python_ml_source: source,
    python_ml_details: pythonDetails,
    timestamp: new Date().toISOString()
  });
});

// -----------------------------------------------------------------------------
// 2. Model Metrics & Metadata
// -----------------------------------------------------------------------------
router.get('/model/metrics', (req, res) => {
  res.json({
    champion_model: PROJECT_KNOWLEDGE_BASE.champion_model_metrics.algorithm,
    threshold: PROJECT_KNOWLEDGE_BASE.champion_model_metrics.decision_threshold,
    metrics: PROJECT_KNOWLEDGE_BASE.champion_model_metrics.verified_test_metrics_2014J,
    split_info: PROJECT_KNOWLEDGE_BASE.dataset_and_split.chronological_split
  });
});

router.get('/model/feature-importance', (req, res) => {
  res.json({
    features: PROJECT_KNOWLEDGE_BASE.features
  });
});

router.get('/model/config', (req, res) => {
  res.json({
    overview: PROJECT_KNOWLEDGE_BASE.project_overview,
    model: PROJECT_KNOWLEDGE_BASE.champion_model_metrics,
    dataset: PROJECT_KNOWLEDGE_BASE.dataset_and_split,
    ethics: PROJECT_KNOWLEDGE_BASE.ethical_principles
  });
});

// -----------------------------------------------------------------------------
// 3. Single Student Prediction Proxy
// -----------------------------------------------------------------------------
router.post('/predict', async (req, res) => {
  try {
    const studentData = req.body;

    // Numerical field conversion and basic validation
    const formatted = {
      code_module: String(studentData.code_module || 'BBB').toUpperCase(),
      code_presentation: String(studentData.code_presentation || '2014J'),
      target_assessment_type: String(studentData.target_assessment_type || 'TMA').toUpperCase(),
      target_date: parseFloat(studentData.target_date ?? 50),
      total_clicks: parseFloat(studentData.total_clicks ?? 100),
      activity_records: parseFloat(studentData.activity_records ?? 20),
      active_days: parseFloat(studentData.active_days ?? 10),
      active_days_last_30_days: parseFloat(studentData.active_days_last_30_days ?? 5),
      clicks_last_7_days: parseFloat(studentData.clicks_last_7_days ?? 10),
      clicks_last_14_days: parseFloat(studentData.clicks_last_14_days ?? 20),
      clicks_last_30_days: parseFloat(studentData.clicks_last_30_days ?? 40),
      average_clicks_per_active_day: parseFloat(studentData.average_clicks_per_active_day ?? 10)
    };

    // Forward to Python microservice
    const result = await callPythonML('/predict', formatted, 'POST');
    res.json({
      ...result.data,
      ml_source: result.source
    });
  } catch (error) {
    console.error('[Node API /predict] Error:', error.message);
    res.status(500).json({
      error: 'Prediction failed',
      details: error.message
    });
  }
});

// -----------------------------------------------------------------------------
// 4. Batch Student Prediction (JSON or CSV Upload)
// -----------------------------------------------------------------------------
router.post('/predict/batch', upload.single('file'), async (req, res) => {
  try {
    let studentRows = [];

    if (req.file) {
      // Process uploaded CSV file
      const filePath = req.file.path;
      const parsedRows = await new Promise((resolve, reject) => {
        const rows = [];
        fs.createReadStream(filePath)
          .pipe(csv())
          .on('data', (data) => rows.push(data))
          .on('end', () => resolve(rows))
          .on('error', (err) => reject(err));
      });

      // Remove temp file
      fs.unlink(filePath, () => {});

      studentRows = parsedRows.map((row, index) => {
        return {
          id: row.id || row.id_student || `STU-${1000 + index}`,
          code_module: String(row.code_module || 'BBB').toUpperCase(),
          code_presentation: String(row.code_presentation || '2014J'),
          target_assessment_type: String(row.target_assessment_type || 'TMA').toUpperCase(),
          target_date: parseFloat(row.target_date ?? 50),
          total_clicks: parseFloat(row.total_clicks ?? 100),
          activity_records: parseFloat(row.activity_records ?? 20),
          active_days: parseFloat(row.active_days ?? 10),
          active_days_last_30_days: parseFloat(row.active_days_last_30_days ?? 5),
          clicks_last_7_days: parseFloat(row.clicks_last_7_days ?? 10),
          clicks_last_14_days: parseFloat(row.clicks_last_14_days ?? 20),
          clicks_last_30_days: parseFloat(row.clicks_last_30_days ?? 40),
          average_clicks_per_active_day: parseFloat(row.average_clicks_per_active_day ?? 10)
        };
      });
    } else if (Array.isArray(req.body.students)) {
      studentRows = req.body.students;
    } else {
      return res.status(400).json({ error: 'Please upload a CSV file or provide a students array.' });
    }

    if (studentRows.length === 0) {
      return res.status(400).json({ error: 'No student records found to analyze.' });
    }

    // Call Python batch endpoint
    const batchPayload = {
      students: studentRows.map(s => ({
        code_module: s.code_module,
        code_presentation: s.code_presentation,
        target_assessment_type: s.target_assessment_type,
        target_date: s.target_date,
        total_clicks: s.total_clicks,
        activity_records: s.activity_records,
        active_days: s.active_days,
        active_days_last_30_days: s.active_days_last_30_days,
        clicks_last_7_days: s.clicks_last_7_days,
        clicks_last_14_days: s.clicks_last_14_days,
        clicks_last_30_days: s.clicks_last_30_days,
        average_clicks_per_active_day: s.average_clicks_per_active_day
      }))
    };

    const result = await callPythonML('/predict/batch', batchPayload, 'POST');
    const predictions = result.data.predictions || [];

    // Combine student input metadata with model prediction
    const mergedResults = studentRows.map((orig, i) => {
      const pred = predictions[i] || {};
      return {
        id: orig.id,
        code_module: orig.code_module,
        code_presentation: orig.code_presentation,
        target_assessment_type: orig.target_assessment_type,
        target_date: orig.target_date,
        total_clicks: orig.total_clicks,
        active_days_last_30_days: orig.active_days_last_30_days,
        predicted_probability: pred.predicted_probability ?? 0,
        flagged_for_review: pred.flagged_for_review ?? false,
        risk_band: pred.risk_band ?? 'Unknown',
        status: pred.status ?? 'Processed'
      };
    });

    const flaggedCount = mergedResults.filter(r => r.flagged_for_review).length;
    const safeCount = mergedResults.length - flaggedCount;
    const riskRate = ((flaggedCount / mergedResults.length) * 100).toFixed(1);

    res.json({
      total_processed: mergedResults.length,
      flagged_count: flaggedCount,
      safe_count: safeCount,
      risk_rate_percent: parseFloat(riskRate),
      threshold: result.data.threshold || 0.24567,
      results: mergedResults,
      ml_source: result.source
    });

  } catch (error) {
    console.error('[Node API /predict/batch] Error:', error.message);
    res.status(500).json({
      error: 'Batch prediction failed',
      details: error.message
    });
  }
});

// -----------------------------------------------------------------------------
// 5. Download Sample Batch CSV
// -----------------------------------------------------------------------------
router.get('/sample-csv', (req, res) => {
  const csvContent = `id,code_module,code_presentation,target_assessment_type,target_date,total_clicks,activity_records,active_days,active_days_last_30_days,clicks_last_7_days,clicks_last_14_days,clicks_last_30_days,average_clicks_per_active_day
STU-2001,BBB,2014J,TMA,54,42,12,6,1,0,5,15,7.0
STU-2002,BBB,2014J,TMA,54,210,65,18,8,12,45,95,11.6
STU-2003,AAA,2014J,TMA,54,850,210,42,21,80,190,380,20.2
STU-2004,CCC,2014J,CMA,32,15,5,2,0,0,0,10,7.5
STU-2005,DDD,2014J,TMA,60,620,150,30,15,40,110,240,20.6
STU-2006,EEE,2014J,TMA,45,180,45,14,5,8,30,70,12.8
STU-2007,FFF,2014J,CMA,28,310,95,22,12,35,85,160,14.1
STU-2008,GGG,2014J,TMA,50,90,25,9,2,0,10,35,10.0
`;
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="student_sample_cohort.csv"');
  res.send(csvContent);
});

// -----------------------------------------------------------------------------
// 6. Groq-Powered AI Assistant
// -----------------------------------------------------------------------------
router.post('/chat/message', async (req, res) => {
  try {
    const { messages = [] } = req.body;

    if (!GROQ_API_KEY) {
      return res.status(500).json({
        error: 'Groq API key not configured on server.'
      });
    }

    const systemPrompt = `You are "Insight AI Assistant", the official expert AI companion for Student Insight AI — an academic analytics and student early-warning platform.

You have deep technical and contextual knowledge of this specific project:
${JSON.stringify(PROJECT_KNOWLEDGE_BASE, null, 2)}

Key Guidelines for your responses:
1. Tone: Professional, articulate, encouraging, authoritative yet accessible to both professors, data scientists, and hiring managers.
2. Ground Truth: Always cite verified project metrics when asked:
   - Accuracy: 74.32%
   - Recall: 63.52% (996 out of 1,568 actual positive failing cases flagged)
   - Decision Threshold: 0.24567 (derived strictly on 2014B validation set)
   - ROC-AUC: 77.84%
   - Dataset: OULAD, 41,062 rows in 2014J test split
   - Model: Random Forest Classifier (100 estimators, max_depth=10, balanced_subsample)
3. Accuracy vs Recall Rationale: If asked why accuracy is 74% and not 90%+, explain that in heavily imbalanced failure prediction (~3.8% failure rate), a naive dummy model gets 96.2% accuracy by doing nothing (0% recall). We benchmarked LightGBM which reached 90.88% accuracy, but recall collapsed to 30.93% (missing 1,083 failing students!). Our priority is student retention, so we deliberately optimized for 63.52% recall with 0.2457 threshold.
4. Ethical Standard: Emphasize that predictions are advisory screenings. No automated punishment or course removal. Demographic features (gender, disability, deprivation index) are intentionally excluded to eliminate bias.
5. Formatting: Use clean markdown, bullet points, and concise sections. Keep responses direct and informative.`;

    const formattedMessages = [
      { role: 'system', content: systemPrompt },
      ...messages.slice(-10) // keep last 10 messages for conversational context
    ];

    const groqResponse = await axios.post(
      'https://api.groq.com/openai/v1/chat/completions',
      {
        model: GROQ_MODEL,
        messages: formattedMessages,
        temperature: 0.4,
        max_tokens: 1200
      },
      {
        headers: {
          'Authorization': `Bearer ${GROQ_API_KEY}`,
          'Content-Type': 'application/json'
        },
        timeout: 20000
      }
    );

    const reply = groqResponse.data.choices[0]?.message?.content || "I couldn't generate a response at this moment.";
    res.json({
      reply,
      model: GROQ_MODEL,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('[Node API /chat/message] Error:', error.response?.data || error.message);
    res.status(500).json({
      error: 'AI Chatbot error',
      details: error.response?.data?.error?.message || error.message
    });
  }
});

module.exports = router;
