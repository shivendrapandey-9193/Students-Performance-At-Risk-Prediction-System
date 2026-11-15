import axios from 'axios';
import { PROJECT_KNOWLEDGE } from './projectKnowledge';

// Resolve base URL from environment variable or fallback to live Render backend
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://students-performance-at-risk-prediction.onrender.com';
export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

// Create configured Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 1. Health Probe
 * Calls GET /health on the Render FastAPI backend
 */
export async function checkBackendHealth() {
  try {
    const response = await apiClient.get('/health');
    return {
      status: response.data?.status === 'healthy' ? 'online' : 'degraded',
      data: response.data,
      url: API_BASE_URL
    };
  } catch (error) {
    console.warn(`[API] Health check failed for ${API_BASE_URL}:`, error.message);
    return {
      status: 'offline',
      error: error.message,
      url: API_BASE_URL
    };
  }
}

/**
 * 2. Individual Student Prediction
 * Calls POST /predict on the Render FastAPI backend
 */
export async function predictIndividualStudent(features) {
  // Format and validate numerical constraints
  const payload = {
    code_module: String(features.code_module || 'BBB').toUpperCase(),
    code_presentation: String(features.code_presentation || '2014J'),
    target_assessment_type: String(features.target_assessment_type || 'TMA').toUpperCase(),
    target_date: parseFloat(features.target_date ?? 54.0),
    total_clicks: parseFloat(features.total_clicks ?? 100.0),
    activity_records: parseFloat(features.activity_records ?? 20.0),
    active_days: parseFloat(features.active_days ?? 10.0),
    active_days_last_30_days: parseFloat(features.active_days_last_30_days ?? 5.0),
    clicks_last_7_days: parseFloat(features.clicks_last_7_days ?? 10.0),
    clicks_last_14_days: parseFloat(features.clicks_last_14_days ?? 20.0),
    clicks_last_30_days: parseFloat(features.clicks_last_30_days ?? 40.0),
    average_clicks_per_active_day: parseFloat(features.average_clicks_per_active_day ?? 10.0),
  };

  const response = await apiClient.post('/predict', payload);
  return response.data;
}

/**
 * 3. Batch Student Prediction
 * Calls POST /predict/batch on the Render FastAPI backend
 */
export async function predictBatchStudents(studentRows) {
  if (!Array.isArray(studentRows) || studentRows.length === 0) {
    throw new Error('No student records provided for batch evaluation.');
  }

  const formattedStudents = studentRows.map((s, idx) => ({
    code_module: String(s.code_module || 'BBB').toUpperCase(),
    code_presentation: String(s.code_presentation || '2014J'),
    target_assessment_type: String(s.target_assessment_type || 'TMA').toUpperCase(),
    target_date: parseFloat(s.target_date ?? 54.0),
    total_clicks: parseFloat(s.total_clicks ?? 100.0),
    activity_records: parseFloat(s.activity_records ?? 20.0),
    active_days: parseFloat(s.active_days ?? 10.0),
    active_days_last_30_days: parseFloat(s.active_days_last_30_days ?? 5.0),
    clicks_last_7_days: parseFloat(s.clicks_last_7_days ?? 10.0),
    clicks_last_14_days: parseFloat(s.clicks_last_14_days ?? 20.0),
    clicks_last_30_days: parseFloat(s.clicks_last_30_days ?? 40.0),
    average_clicks_per_active_day: parseFloat(s.average_clicks_per_active_day ?? 10.0),
  }));

  const payload = { students: formattedStudents };
  const response = await apiClient.post('/predict/batch', payload);
  const data = response.data;

  // Enrich predictions with original record IDs
  const predictions = data.predictions || [];
  const mergedResults = studentRows.map((orig, i) => {
    const pred = predictions[i] || {};
    return {
      id: orig.id || orig.id_student || `STU-${1000 + i}`,
      code_module: orig.code_module || 'BBB',
      code_presentation: orig.code_presentation || '2014J',
      target_assessment_type: orig.target_assessment_type || 'TMA',
      target_date: orig.target_date,
      total_clicks: orig.total_clicks,
      active_days_last_30_days: orig.active_days_last_30_days,
      predicted_probability: pred.predicted_probability ?? 0,
      flagged_for_review: pred.flagged_for_review ?? false,
      risk_band: pred.risk_band ?? 'Unknown',
      status: pred.status ?? 'Processed'
    };
  });

  const flaggedCount = data.flagged_count ?? mergedResults.filter(r => r.flagged_for_review).length;
  const safeCount = data.safe_count ?? (mergedResults.length - flaggedCount);
  const riskRate = ((flaggedCount / mergedResults.length) * 100).toFixed(1);

  return {
    total_processed: data.total_processed ?? mergedResults.length,
    flagged_count: flaggedCount,
    safe_count: safeCount,
    risk_rate_percent: parseFloat(riskRate),
    threshold: data.threshold ?? 0.24567,
    results: mergedResults
  };
}

/**
 * 4. Client-side CSV Parser
 * Turns raw CSV text into array of student objects
 */
export function parseStudentCsv(csvText) {
  const lines = csvText.split('\n').filter(line => line.trim().length > 0);
  if (lines.length < 2) {
    throw new Error('CSV must contain a header row and at least one student data row.');
  }

  const rawHeaders = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
  const requiredFields = [
    'code_module', 'code_presentation', 'target_assessment_type', 
    'target_date', 'total_clicks', 'activity_records', 'active_days', 
    'active_days_last_30_days', 'clicks_last_7_days', 'clicks_last_14_days', 
    'clicks_last_30_days', 'average_clicks_per_active_day'
  ];

  const missing = requiredFields.filter(f => !rawHeaders.includes(f));
  if (missing.length > 0) {
    throw new Error(`CSV is missing required columns: ${missing.join(', ')}`);
  }

  const students = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim().replace(/['"]/g, ''));
    if (values.length < rawHeaders.length) continue;

    const row = {};
    rawHeaders.forEach((header, idx) => {
      row[header] = values[idx];
    });

    students.push({
      id: row.id || row.id_student || `STU-${1000 + i}`,
      code_module: row.code_module,
      code_presentation: row.code_presentation,
      target_assessment_type: row.target_assessment_type,
      target_date: parseFloat(row.target_date) || 54.0,
      total_clicks: parseFloat(row.total_clicks) || 0.0,
      activity_records: parseFloat(row.activity_records) || 0.0,
      active_days: parseFloat(row.active_days) || 0.0,
      active_days_last_30_days: parseFloat(row.active_days_last_30_days) || 0.0,
      clicks_last_7_days: parseFloat(row.clicks_last_7_days) || 0.0,
      clicks_last_14_days: parseFloat(row.clicks_last_14_days) || 0.0,
      clicks_last_30_days: parseFloat(row.clicks_last_30_days) || 0.0,
      average_clicks_per_active_day: parseFloat(row.average_clicks_per_active_day) || 0.0,
    });
  }

  return students;
}

/**
 * 5. Download Sample CSV
 */
export function downloadSampleCsv() {
  const sampleContent = `id,code_module,code_presentation,target_assessment_type,target_date,total_clicks,activity_records,active_days,active_days_last_30_days,clicks_last_7_days,clicks_last_14_days,clicks_last_30_days,average_clicks_per_active_day
STU-2001,BBB,2014J,TMA,54,42,12,6,1,0,5,15,7.0
STU-2002,BBB,2014J,TMA,54,210,65,18,8,12,45,95,11.6
STU-2003,AAA,2014J,TMA,54,850,210,42,21,80,190,380,20.2
STU-2004,CCC,2014J,CMA,32,15,5,2,0,0,0,10,7.5
STU-2005,DDD,2014J,TMA,60,620,150,30,15,40,110,240,20.6
STU-2006,EEE,2014J,TMA,45,180,45,14,5,8,30,70,12.8
STU-2007,FFF,2014J,CMA,28,310,95,22,12,35,85,160,14.1
STU-2008,GGG,2014J,TMA,50,90,25,9,2,0,10,35,10.0
`;
  const blob = new Blob([sampleContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'student_sample_cohort.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * 6. Groq Cloud AI Assistant Integration
 */
const GROQ_API_KEY = import.meta.env.VITE_GROQ_API_KEY || '';
const GROQ_MODEL = import.meta.env.VITE_GROQ_MODEL || 'qwen/qwen3.8-27b';

export async function askInsightAI(messages) {
  const systemPrompt = `You are Insight AI Assistant, the expert AI companion for Student Insight AI — an academic analytics and student early-warning platform.
Project Knowledge:
${JSON.stringify(PROJECT_KNOWLEDGE, null, 2)}

Guidelines:
- Tone: Professional, encouraging, and authoritative.
- Cite verified facts: Accuracy 74.32%, Recall 63.52%, Threshold 0.2457, Dataset OULAD 2014J (41,062 rows), Random Forest.
- Rationale: Explain that 90%+ accuracy is a deceptive metric in imbalanced data (~3.8% failure rate) where a dummy model gets 96.2% accuracy with 0% recall. Our 0.2457 cutoff optimizes for 63.52% recall to save students from unassisted failure.
- Ethics: Predictions are advisory screening aids; protected demographics are excluded to eliminate bias.`;

  // 1. Try Groq Cloud API if key is present
  if (GROQ_API_KEY && GROQ_API_KEY.startsWith('gsk_')) {
    try {
      const response = await axios.post(
        'https://api.groq.com/openai/v1/chat/completions',
        {
          model: GROQ_MODEL,
          messages: [
            { role: 'system', content: systemPrompt },
            ...messages.slice(-8)
          ],
          temperature: 0.4,
          max_tokens: 1000
        },
        {
          headers: {
            'Authorization': `Bearer ${GROQ_API_KEY}`,
            'Content-Type': 'application/json'
          },
          timeout: 25000
        }
      );
      const reply = response.data?.choices?.[0]?.message?.content;
      if (reply) return reply;
    } catch (groqErr) {
      console.warn('[AI Assistant] Groq API direct call failed, using intelligent domain fallback:', groqErr.message);
    }
  }

  // 2. Intelligent Knowledge Base Fallback if network or key is unavailable
  const lastUserMsg = messages[messages.length - 1]?.content?.toLowerCase() || '';

  if (lastUserMsg.includes('accuracy') || lastUserMsg.includes('performance') || lastUserMsg.includes('metric')) {
    return `### 📊 Model Performance Highlights\n\n- **Accuracy:** **74.32%**\n- **Recall (Sensitivity):** **63.52%** (Catches 996 out of 1,568 struggling students)\n- **Decision Cutoff:** **0.2457**\n- **ROC-AUC:** **77.84%**\n- **PR-AUC:** **12.90%**\n\n**Why not 90% accuracy?**\nIn our dataset of 41,062 assessment submissions, only 3.8% result in failure. A naive model predicting 'safe' for everyone gets 96.2% accuracy but 0% recall! We deliberately optimized for high recall to intercept struggling students early.`;
  }

  if (lastUserMsg.includes('architecture') || lastUserMsg.includes('stack')) {
    return `### 🏗️ Full-Stack Architecture\n\n1. **Frontend:** React.js 18 + Vite + Tailwind CSS + Recharts (Hosted on Vercel)\n2. **ML Backend:** Python FastAPI + Scikit-Learn Random Forest (Hosted on Render: \`https://students-performance-at-risk-prediction.onrender.com\`)\n3. **Decision Policy:** Validation-calibrated cutoff $\\tau = 0.2457$\n4. **Data Hygiene:** Strict chronological split (2013B/J Train, 2014B Val, 2014J Test) with zero temporal leakage.`;
  }

  if (lastUserMsg.includes('interview') || lastUserMsg.includes('explain')) {
    return `### 🎓 Project Explanation for Interviews\n\n**Student Insight AI** is an early-warning academic analytics SaaS. It predicts whether a student will score <40 on upcoming coursework assessments using 12 pre-deadline VLE clickstream features.\n\n**Key Talking Points:**\n- **Temporal Integrity:** We strictly split data chronologically (2013 train $\\rightarrow$ 2014 test) to prevent future data leakage.\n- **Recall Priority:** In student retention, False Negatives (missing a failing student) are far more costly than False Positives (friendly advisor check-in).\n- **Fairness:** Protected demographics were excluded to eliminate bias.`;
  }

  return `I am **Insight AI Assistant**. I can answer any questions about our **Random Forest model**, the **OULAD dataset**, our **74.32% accuracy and 63.52% recall**, or our **FastAPI + React SaaS architecture**. How can I help you today?`;
}
