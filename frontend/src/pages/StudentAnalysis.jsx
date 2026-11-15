import React, { useState } from 'react';
import { 
  Users, 
  FileSpreadsheet, 
  Upload, 
  Download, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Search, 
  Sparkles,
  Info,
  Eye,
  X
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import RiskBadge from '../components/RiskBadge';
import axios from 'axios';

const PRESETS = {
  custom: {
    label: "Custom Input",
    data: {
      code_module: "BBB",
      code_presentation: "2014J",
      target_assessment_type: "TMA",
      target_date: 54,
      total_clicks: 180,
      activity_records: 45,
      active_days: 14,
      active_days_last_30_days: 6,
      clicks_last_7_days: 10,
      clicks_last_14_days: 28,
      clicks_last_30_days: 65,
      average_clicks_per_active_day: 12.8
    }
  },
  high_risk: {
    label: "High Risk Student (Struggling/Disengaged)",
    data: {
      code_module: "BBB",
      code_presentation: "2014J",
      target_assessment_type: "TMA",
      target_date: 54,
      total_clicks: 35,
      activity_records: 8,
      active_days: 4,
      active_days_last_30_days: 1,
      clicks_last_7_days: 0,
      clicks_last_14_days: 2,
      clicks_last_30_days: 8,
      average_clicks_per_active_day: 8.75
    }
  },
  borderline: {
    label: "Borderline Student (Moderate, Recency Drop)",
    data: {
      code_module: "BBB",
      code_presentation: "2014J",
      target_assessment_type: "TMA",
      target_date: 54,
      total_clicks: 220,
      activity_records: 55,
      active_days: 16,
      active_days_last_30_days: 5,
      clicks_last_7_days: 8,
      clicks_last_14_days: 22,
      clicks_last_30_days: 55,
      average_clicks_per_active_day: 13.75
    }
  },
  high_achieving: {
    label: "High Achieving Student (Active & Consistent)",
    data: {
      code_module: "AAA",
      code_presentation: "2014J",
      target_assessment_type: "TMA",
      target_date: 54,
      total_clicks: 980,
      activity_records: 240,
      active_days: 45,
      active_days_last_30_days: 22,
      clicks_last_7_days: 95,
      clicks_last_14_days: 220,
      clicks_last_30_days: 450,
      average_clicks_per_active_day: 21.7
    }
  }
};

export default function StudentAnalysis() {
  const [activeTab, setActiveTab] = useState('individual'); // 'individual' or 'batch'

  // ---------------------------------------------------------------------------
  // INDIVIDUAL STATE
  // ---------------------------------------------------------------------------
  const [selectedPreset, setSelectedPreset] = useState('custom');
  const [formValues, setFormValues] = useState(PRESETS.custom.data);
  const [predictionResult, setPredictionResult] = useState(null);
  const [individualLoading, setIndividualLoading] = useState(false);
  const [individualError, setIndividualError] = useState(null);

  const handlePresetChange = (presetKey) => {
    setSelectedPreset(presetKey);
    setFormValues(PRESETS[presetKey].data);
    setPredictionResult(null);
    setIndividualError(null);
  };

  const handleInputChange = (field, value) => {
    setFormValues(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleIndividualSubmit = async (e) => {
    e.preventDefault();
    setIndividualLoading(true);
    setIndividualError(null);

    // Validate monotonicity
    if (formValues.clicks_last_7_days > formValues.clicks_last_14_days ||
        formValues.clicks_last_14_days > formValues.clicks_last_30_days ||
        formValues.clicks_last_30_days > formValues.total_clicks) {
      setIndividualError("Logical click consistency violation: clicks must satisfy 7-day <= 14-day <= 30-day <= total clicks.");
      setIndividualLoading(false);
      return;
    }

    if (formValues.active_days_last_30_days > formValues.active_days) {
      setIndividualError("Active days in last 30 days cannot exceed total active days.");
      setIndividualLoading(false);
      return;
    }

    try {
      const response = await axios.post('/api/predict', formValues);
      setPredictionResult(response.data);
    } catch (err) {
      console.error(err);
      setIndividualError(err.response?.data?.details || err.message || "Failed to calculate prediction.");
    } finally {
      setIndividualLoading(false);
    }
  };

  // ---------------------------------------------------------------------------
  // BATCH STATE
  // ---------------------------------------------------------------------------
  const [batchFile, setBatchFile] = useState(null);
  const [batchPreview, setBatchPreview] = useState([]);
  const [batchResults, setBatchResults] = useState(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchError, setBatchError] = useState(null);
  const [filterRisk, setFilterRisk] = useState('all'); // 'all', 'flagged', 'safe'
  const [searchQuery, setSearchQuery] = useState('');
  const [inspectedStudent, setInspectedStudent] = useState(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setBatchFile(file);
    setBatchError(null);
    setBatchResults(null);
    setInspectedStudent(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n').filter(l => l.trim().length > 0);
      const headers = lines[0].split(',').map(h => h.trim());
      const previewRows = lines.slice(1, 6).map(row => {
        const values = row.split(',').map(v => v.trim());
        const obj = {};
        headers.forEach((h, i) => { obj[h] = values[i]; });
        return obj;
      });
      setBatchPreview(previewRows);
    };
    reader.readAsText(file);
  };

  const handleBatchSubmit = async () => {
    if (!batchFile) return;
    setBatchLoading(true);
    setBatchError(null);

    const formData = new FormData();
    formData.append('file', batchFile);

    try {
      const response = await axios.post('/api/predict/batch', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setBatchResults(response.data);
    } catch (err) {
      console.error(err);
      setBatchError(err.response?.data?.details || err.message || "Batch evaluation failed.");
    } finally {
      setBatchLoading(false);
    }
  };

  const exportResultsCSV = () => {
    if (!batchResults || !batchResults.results) return;
    const headers = ["id", "code_module", "code_presentation", "target_assessment_type", "total_clicks", "active_days_30d", "predicted_probability", "flagged_for_review", "status"];
    const rows = batchResults.results.map(r => [
      r.id,
      r.code_module,
      r.code_presentation,
      r.target_assessment_type,
      r.total_clicks,
      r.active_days_last_30_days,
      r.predicted_probability,
      r.flagged_for_review ? 'YES' : 'NO',
      `"${r.status}"`
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `student_cohort_risk_analysis_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredBatchRows = batchResults?.results?.filter(row => {
    const matchesFilter = filterRisk === 'all' 
      ? true 
      : filterRisk === 'flagged' ? row.flagged_for_review : !row.flagged_for_review;
    const matchesSearch = searchQuery === '' 
      ? true 
      : (row.id?.toLowerCase().includes(searchQuery.toLowerCase()) || 
         row.code_module?.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Top Segmented Control Switch */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Student Analysis</h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Primary operational screening: score individual student profiles or process cohort rosters.
          </p>
        </div>

        <div className="inline-flex p-1 rounded-xl bg-slate-900 border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('individual')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'individual'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Individual Analysis</span>
          </button>
          <button
            onClick={() => setActiveTab('batch')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
              activeTab === 'batch'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Batch Student Screening</span>
          </button>
        </div>
      </div>

      {/* ======================================================================= */}
      {/* 1. INDIVIDUAL ANALYSIS VIEW */}
      {/* ======================================================================= */}
      {activeTab === 'individual' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Form: 12 Features */}
          <div className="lg:col-span-7 space-y-6">
            <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 space-y-5">
              {/* Presets Selector */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div>
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-wider block">Profile Preset</span>
                  <span className="text-xs text-slate-400">Load sample student profiles or configure manually</span>
                </div>
                <select
                  value={selectedPreset}
                  onChange={(e) => handlePresetChange(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="custom">Custom Input</option>
                  <option value="high_risk">High Risk Student (Struggling)</option>
                  <option value="borderline">Borderline Student (Moderate)</option>
                  <option value="high_achieving">High Achieving Student</option>
                </select>
              </div>

              {individualError && (
                <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span>{individualError}</span>
                </div>
              )}

              <form onSubmit={handleIndividualSubmit} className="space-y-6">
                {/* Group 1: Academic Context */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400">
                    1. Academic & Assessment Information
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Course Module (AAA-GGG)</label>
                      <select
                        value={formValues.code_module}
                        onChange={(e) => handleInputChange('code_module', e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      >
                        {['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG'].map(m => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Course Presentation</label>
                      <input
                        type="text"
                        value={formValues.code_presentation}
                        onChange={(e) => handleInputChange('code_presentation', e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Assessment Type</label>
                      <select
                        value={formValues.target_assessment_type}
                        onChange={(e) => handleInputChange('target_assessment_type', e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      >
                        <option value="TMA">TMA (Tutor-Marked)</option>
                        <option value="CMA">CMA (Computer-Marked)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Target Assessment Date (Days)</label>
                      <input
                        type="number"
                        min="1"
                        value={formValues.target_date}
                        onChange={(e) => handleInputChange('target_date', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Group 2: Cumulative Semester Activity */}
                <div className="space-y-3 pt-2 border-t border-slate-800/80">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400">
                    2. Cumulative Student Engagement
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Platform Clicks (Total)</label>
                      <input
                        type="number"
                        min="0"
                        value={formValues.total_clicks}
                        onChange={(e) => handleInputChange('total_clicks', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Interaction Records (Total)</label>
                      <input
                        type="number"
                        min="0"
                        value={formValues.activity_records}
                        onChange={(e) => handleInputChange('activity_records', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Active Calendar Days</label>
                      <input
                        type="number"
                        min="0"
                        value={formValues.active_days}
                        onChange={(e) => handleInputChange('active_days', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Avg Clicks / Active Day</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        value={formValues.average_clicks_per_active_day}
                        onChange={(e) => handleInputChange('average_clicks_per_active_day', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Group 3: Recency Study Windows */}
                <div className="space-y-3 pt-2 border-t border-slate-800/80">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400">
                    3. Activity Recency Windows
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Active Days (Last 30 Days)</label>
                      <input
                        type="number"
                        min="0"
                        max="30"
                        value={formValues.active_days_last_30_days}
                        onChange={(e) => handleInputChange('active_days_last_30_days', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Clicks (Last 30 Days)</label>
                      <input
                        type="number"
                        min="0"
                        value={formValues.clicks_last_30_days}
                        onChange={(e) => handleInputChange('clicks_last_30_days', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Clicks (Last 14 Days)</label>
                      <input
                        type="number"
                        min="0"
                        value={formValues.clicks_last_14_days}
                        onChange={(e) => handleInputChange('clicks_last_14_days', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-[11px] text-slate-400 block mb-1">Clicks (Last 7 Days)</label>
                      <input
                        type="number"
                        min="0"
                        value={formValues.clicks_last_7_days}
                        onChange={(e) => handleInputChange('clicks_last_7_days', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={individualLoading}
                  className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-600/20 active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {individualLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Computing Decision Boundary via ML Service...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Predict Student Risk</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Right Panel: Prediction Results */}
          <div className="lg:col-span-5 space-y-6">
            {predictionResult ? (
              <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 space-y-6 sticky top-24">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                    Risk Classification
                  </span>
                  <RiskBadge 
                    flagged={predictionResult.flagged_for_review} 
                    probability={predictionResult.predicted_probability} 
                    threshold={predictionResult.threshold}
                  />
                </div>

                {/* Risk Probability & Threshold Comparison */}
                <div className="space-y-2">
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-slate-400">Predicted Failure Risk Probability</span>
                    <span className="text-3xl font-extrabold text-white">
                      {(predictionResult.predicted_probability * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden relative">
                    <div
                      className={`h-full transition-all duration-500 rounded-full ${
                        predictionResult.flagged_for_review 
                          ? 'bg-gradient-to-r from-amber-500 to-rose-500' 
                          : 'bg-gradient-to-r from-teal-500 to-emerald-400'
                      }`}
                      style={{ width: `${Math.min(predictionResult.predicted_probability * 100, 100)}%` }}
                    />
                  </div>

                  <div className="flex justify-between text-[11px] text-slate-400 pt-1 font-mono">
                    <span>Safe Baseline (0%)</span>
                    <span className="text-blue-400 font-semibold">Decision Cutoff: {(predictionResult.threshold * 100).toFixed(2)}%</span>
                    <span>High Risk (100%)</span>
                  </div>
                </div>

                {/* Status & Explanation */}
                <div className={`p-4 rounded-xl border space-y-2 ${
                  predictionResult.flagged_for_review
                    ? 'bg-rose-500/10 border-rose-500/25 text-rose-200'
                    : 'bg-emerald-500/10 border-emerald-500/25 text-emerald-200'
                }`}>
                  <div className="font-semibold text-sm flex items-center gap-2">
                    {predictionResult.flagged_for_review ? (
                      <>
                        <AlertTriangle className="w-4 h-4 text-rose-400" />
                        <span>Exceeds Decision Threshold ({((predictionResult.threshold) * 100).toFixed(1)}%)</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        <span>Below Decision Threshold ({((predictionResult.threshold) * 100).toFixed(1)}%)</span>
                      </>
                    )}
                  </div>
                  <p className="text-xs leading-relaxed text-slate-300">
                    {predictionResult.flagged_for_review
                      ? `Student's predicted probability of scoring <40 (${(predictionResult.predicted_probability * 100).toFixed(1)}%) exceeds the recall-focused 0.2457 boundary. Low clicks or recent inactivity match historical at-risk profiles.`
                      : `Student's predicted risk (${(predictionResult.predicted_probability * 100).toFixed(1)}%) falls below the 0.2457 threshold. Interaction levels indicate consistent preparation.`}
                  </p>
                </div>

                {/* Academic Support Suggestions */}
                <div className="space-y-3 pt-2 border-t border-slate-800">
                  <h5 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    Appropriate Academic Support Suggestions
                  </h5>
                  <ul className="text-xs space-y-2 text-slate-400">
                    {predictionResult.flagged_for_review ? (
                      <>
                        <li className="flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                          <span>Initiate a low-stakes check-in email referencing module {formValues.code_module} study materials.</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                          <span>Provide targeted links to TMA submission rubrics and weekly recorded lectures.</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />
                          <span>Offer connection to peer tutoring or teaching assistant virtual office hours.</span>
                        </li>
                      </>
                    ) : (
                      <>
                        <li className="flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                          <span>Standard monitoring; student is on track for timely submission.</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                          <span>Provide regular encouragement and upcoming deadline notifications.</span>
                        </li>
                      </>
                    )}
                  </ul>
                </div>

                {/* Disclaimer */}
                <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
                  <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                  <span>
                    Advisory screening only. Predictions represent statistical probabilities and must never be used to penalize or make automated academic determinations.
                  </span>
                </div>
              </div>
            ) : (
              <div className="p-10 rounded-2xl bg-[#111827]/40 border border-slate-800/80 text-center space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto">
                  <Users className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">Ready for Individual Screening</h4>
                  <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                    Configure the 12 student engagement metrics or select a profile preset on the left, then click "Predict Student Risk".
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================= */}
      {/* 2. BATCH STUDENT SCREENING VIEW */}
      {/* ======================================================================= */}
      {activeTab === 'batch' && (
        <div className="space-y-8">
          {/* Upload & Instructions Card */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">Batch Student Cohort Screening</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Upload an institutional CSV file to evaluate cohort assessment risk via the Python ML microservice.
                </p>
              </div>

              <a
                href="/api/sample-csv"
                download="student_sample_cohort.csv"
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition"
              >
                <Download className="w-3.5 h-3.5 text-blue-400" />
                <span>Download Sample CSV</span>
              </a>
            </div>

            {batchError && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span>{batchError}</span>
              </div>
            )}

            {/* Dropzone */}
            <div className="border-2 border-dashed border-slate-700 hover:border-blue-500/60 rounded-2xl p-8 text-center bg-slate-950/40 transition group">
              <input
                type="file"
                accept=".csv"
                id="csvFileInput"
                onChange={handleFileUpload}
                className="hidden"
              />
              <label htmlFor="csvFileInput" className="cursor-pointer space-y-3 block">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mx-auto group-hover:scale-110 transition">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <span className="text-sm font-semibold text-white group-hover:text-blue-400 transition">
                    {batchFile ? batchFile.name : "Click to select cohort CSV or drag file here"}
                  </span>
                  <span className="block text-xs text-slate-400 mt-1">
                    Accepts comma-separated .csv files formatted with student activity columns
                  </span>
                </div>
              </label>
            </div>

            {/* Preview of Uploaded Rows */}
            {batchPreview.length > 0 && !batchResults && (
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300">File Ingestion Preview (First 5 Rows)</span>
                  <span className="text-slate-400">{batchPreview.length} rows loaded into preview</span>
                </div>
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 font-mono text-[10px] uppercase">
                      <tr>
                        {Object.keys(batchPreview[0] || {}).slice(0, 7).map((col) => (
                          <th key={col} className="px-3 py-2 border-b border-slate-800">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                      {batchPreview.map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40">
                          {Object.values(row).slice(0, 7).map((val, cIdx) => (
                            <td key={cIdx} className="px-3 py-2 font-mono text-[11px] truncate max-w-[120px]">
                              {val}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <button
                  onClick={handleBatchSubmit}
                  disabled={batchLoading}
                  className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-600/20 active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {batchLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Processing Batch Prediction via Python ML Service...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Run Batch Prediction</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Batch Analysis Output */}
          {batchResults && (
            <div className="space-y-6">
              {/* Batch KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-5 rounded-xl bg-[#111827] border border-slate-800">
                  <span className="text-xs text-slate-400 uppercase tracking-wider">Total Students Evaluated</span>
                  <div className="text-2xl font-bold text-white mt-1">{batchResults.total_processed}</div>
                  <span className="text-[11px] text-slate-400">Total cohort records</span>
                </div>
                <div className="p-5 rounded-xl bg-[#111827] border border-slate-800">
                  <span className="text-xs text-rose-400 uppercase tracking-wider font-semibold">At-Risk Count</span>
                  <div className="text-2xl font-bold text-rose-400 mt-1">{batchResults.flagged_count}</div>
                  <span className="text-[11px] text-slate-400">Risk &gt;= 0.2457 cutoff</span>
                </div>
                <div className="p-5 rounded-xl bg-[#111827] border border-slate-800">
                  <span className="text-xs text-emerald-400 uppercase tracking-wider font-semibold">Not-At-Risk Count</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{batchResults.safe_count}</div>
                  <span className="text-[11px] text-slate-400">Below review threshold</span>
                </div>
                <div className="p-5 rounded-xl bg-[#111827] border border-slate-800">
                  <span className="text-xs text-amber-400 uppercase tracking-wider font-semibold">Risk Proportion</span>
                  <div className="text-2xl font-bold text-amber-400 mt-1">{batchResults.risk_rate_percent}%</div>
                  <span className="text-[11px] text-slate-400">Percent flagged for check-in</span>
                </div>
              </div>

              {/* Risk Distribution Chart */}
              <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                <div className="md:col-span-1 h-44 flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Not At Risk', value: batchResults.safe_count },
                          { name: 'At Risk', value: batchResults.flagged_count }
                        ]}
                        innerRadius={45}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        <Cell fill="#10b981" />
                        <Cell fill="#f43f5e" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="md:col-span-2 space-y-2">
                  <h4 className="text-sm font-bold text-white">Cohort Risk Distribution</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Evaluated {batchResults.total_processed} students using the calibrated 0.2457 decision boundary. 
                    {batchResults.flagged_count} students ({batchResults.risk_rate_percent}%) are recommended for proactive educator follow-up.
                  </p>
                  <div className="flex gap-4 pt-1 text-xs">
                    <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      Not At Risk: {batchResults.safe_count}
                    </span>
                    <span className="flex items-center gap-1.5 text-rose-400 font-medium">
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                      At Risk: {batchResults.flagged_count}
                    </span>
                  </div>
                </div>
              </div>

              {/* Results Table with Search, Filter & Individual Record Inspection */}
              <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        placeholder="Search student ID or module..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500 w-48 sm:w-60"
                      />
                    </div>

                    <div className="inline-flex p-0.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                      {['all', 'flagged', 'safe'].map(f => (
                        <button
                          key={f}
                          onClick={() => setFilterRisk(f)}
                          className={`px-2.5 py-1 rounded capitalize font-medium transition ${
                            filterRisk === f
                              ? 'bg-slate-800 text-white'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {f === 'all' ? 'All' : f === 'flagged' ? 'At Risk' : 'Safe'}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={exportResultsCSV}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition border border-slate-700 self-start sm:self-auto"
                  >
                    <Download className="w-3.5 h-3.5 text-blue-400" />
                    <span>Export CSV</span>
                  </button>
                </div>

                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-950 text-slate-400 font-mono text-[10px] uppercase">
                      <tr>
                        <th className="px-4 py-3">Student ID</th>
                        <th className="px-4 py-3">Module</th>
                        <th className="px-4 py-3">Term</th>
                        <th className="px-4 py-3">Type</th>
                        <th className="px-4 py-3">Total Clicks</th>
                        <th className="px-4 py-3">Active (30d)</th>
                        <th className="px-4 py-3">Failure Risk</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3 text-right">Inspect</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                      {filteredBatchRows.map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition">
                          <td className="px-4 py-3 font-mono font-medium text-white">{row.id}</td>
                          <td className="px-4 py-3 font-mono">{row.code_module}</td>
                          <td className="px-4 py-3 font-mono text-slate-400">{row.code_presentation}</td>
                          <td className="px-4 py-3 font-mono text-slate-400">{row.target_assessment_type}</td>
                          <td className="px-4 py-3 font-mono">{row.total_clicks}</td>
                          <td className="px-4 py-3 font-mono">{row.active_days_last_30_days}d</td>
                          <td className="px-4 py-3 font-mono font-bold">
                            <span className={row.flagged_for_review ? 'text-rose-400' : 'text-emerald-400'}>
                              {(row.predicted_probability * 100).toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <RiskBadge
                              flagged={row.flagged_for_review}
                              probability={row.predicted_probability}
                              size="sm"
                            />
                          </td>
                          <td className="px-4 py-3 text-right">
                            <button
                              onClick={() => setInspectedStudent(row)}
                              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-blue-400 transition"
                              title="Inspect Individual Record"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Modal / Inspection Card for Individual Batch Record */}
          {inspectedStudent && (
            <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-[#111827] border border-slate-700 rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span>Record Inspection:</span>
                      <span className="font-mono text-blue-400">{inspectedStudent.id}</span>
                    </h3>
                    <span className="text-xs text-slate-400">Cohort assessment profile details</span>
                  </div>
                  <button
                    onClick={() => setInspectedStudent(null)}
                    className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                    <div>
                      <span className="text-xs text-slate-400 block">Risk Evaluation</span>
                      <span className="text-lg font-bold text-white">
                        {(inspectedStudent.predicted_probability * 100).toFixed(1)}% Risk
                      </span>
                    </div>
                    <RiskBadge
                      flagged={inspectedStudent.flagged_for_review}
                      probability={inspectedStudent.predicted_probability}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80">
                      <span className="text-slate-400 block">Course Module</span>
                      <span className="font-mono font-medium text-white">{inspectedStudent.code_module}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80">
                      <span className="text-slate-400 block">Presentation</span>
                      <span className="font-mono font-medium text-white">{inspectedStudent.code_presentation}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80">
                      <span className="text-slate-400 block">Assessment Type</span>
                      <span className="font-mono font-medium text-white">{inspectedStudent.target_assessment_type}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80">
                      <span className="text-slate-400 block">Total Clicks</span>
                      <span className="font-mono font-medium text-white">{inspectedStudent.total_clicks}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80">
                      <span className="text-slate-400 block">Active Days (Last 30d)</span>
                      <span className="font-mono font-medium text-white">{inspectedStudent.active_days_last_30_days} days</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80">
                      <span className="text-slate-400 block">Threshold Cutoff</span>
                      <span className="font-mono font-medium text-blue-400">0.2457</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-300">
                    <strong>Intervention Guidance:</strong> {inspectedStudent.flagged_for_review
                      ? "Flagged for educator check-in. Review recent login consistency and provide targeted rubric support."
                      : "Sufficient engagement level. Student is on track."}
                  </div>
                </div>

                <div className="pt-2 text-right">
                  <button
                    onClick={() => setInspectedStudent(null)}
                    className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium"
                  >
                    Close Inspection
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
