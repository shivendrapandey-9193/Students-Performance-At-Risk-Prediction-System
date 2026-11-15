import React, { useState } from 'react';
import { 
  BarChart3, 
  Scale, 
  Layers, 
  ShieldCheck, 
  Calendar,
  CheckCircle2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';
import MetricCard from '../components/MetricCard';

export default function ModelInsights() {
  const [features] = useState([
    { name: "code_module", weight: 9.05, importanceText: "9.05%" },
    { name: "active_days_last_30_days", weight: 3.46, importanceText: "3.46%" },
    { name: "target_date", weight: 3.40, importanceText: "3.40%" },
    { name: "clicks_last_30_days", weight: 2.88, importanceText: "2.88%" },
    { name: "target_assessment_type", weight: 2.77, importanceText: "2.77%" },
    { name: "clicks_last_14_days", weight: 2.33, importanceText: "2.33%" },
    { name: "clicks_last_7_days", weight: 1.25, importanceText: "1.25%" },
    { name: "activity_records", weight: 1.00, importanceText: "1.00%" },
    { name: "total_clicks", weight: 0.36, importanceText: "0.36%" },
    { name: "active_days", weight: 0.21, importanceText: "0.21%" },
    { name: "average_clicks_per_active_day", weight: 0.21, importanceText: "0.21%" },
    { name: "code_presentation", weight: 0.00, importanceText: "0.00%" }
  ]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h2 className="text-2xl font-bold text-white tracking-tight">Model Insights</h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Verified model evaluation metrics, test confusion matrix, feature importance, and deployment configuration.
        </p>
      </div>

      {/* 1. Model Performance */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400">
            1. Model Performance (2014J Test Cohort)
          </h3>
          <span className="text-[11px] font-mono text-slate-400">Blind Evaluation • 41,062 Records</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <MetricCard
            title="Accuracy"
            value="74.32%"
            subtitle="Overall test accuracy"
            color="sky"
          />
          <MetricCard
            title="Recall"
            value="63.52%"
            subtitle="Captures failing students"
            color="emerald"
          />
          <MetricCard
            title="Precision"
            value="9.08%"
            subtitle="Controlled class tradeoff"
            color="amber"
          />
          <MetricCard
            title="F1-Score"
            value="15.89%"
            subtitle="Harmonic mean score"
            color="purple"
          />
          <MetricCard
            title="ROC-AUC"
            value="77.84%"
            subtitle="Discrimination power"
            color="indigo"
          />
          <MetricCard
            title="PR-AUC"
            value="12.90%"
            subtitle="Precision-recall baseline"
            color="rose"
          />
        </div>
      </div>

      {/* 2. Confusion Matrix */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
          <Scale className="w-4 h-4" />
          <span>2. Test Confusion Matrix</span>
        </h3>
        <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* True Negatives */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-emerald-500/20 space-y-1">
              <span className="text-[10px] font-mono uppercase text-emerald-400 tracking-wider">True Negatives (TN)</span>
              <div className="text-2xl font-bold text-white">29,523</div>
              <p className="text-xs text-slate-400 leading-snug">
                Passing students correctly identified as not at risk.
              </p>
            </div>

            {/* False Positives */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-amber-500/20 space-y-1">
              <span className="text-[10px] font-mono uppercase text-amber-400 tracking-wider">False Positives (FP)</span>
              <div className="text-2xl font-bold text-amber-400">9,971</div>
              <p className="text-xs text-slate-400 leading-snug">
                Passing students flagged for advisory check-in (low-cost early triage).
              </p>
            </div>

            {/* False Negatives */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-rose-500/20 space-y-1">
              <span className="text-[10px] font-mono uppercase text-rose-400 tracking-wider">False Negatives (FN)</span>
              <div className="text-2xl font-bold text-rose-400">572</div>
              <p className="text-xs text-slate-400 leading-snug">
                Missed failing students (kept minimal by lowering cutoff to 0.2457).
              </p>
            </div>

            {/* True Positives */}
            <div className="p-4 rounded-xl bg-slate-950/70 border border-blue-500/30 space-y-1">
              <span className="text-[10px] font-mono uppercase text-blue-400 tracking-wider">True Positives (TP)</span>
              <div className="text-2xl font-bold text-blue-400">996</div>
              <p className="text-xs text-slate-400 leading-snug">
                Struggling students successfully caught in advance (63.52% Recall).
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/50 border border-slate-800 text-xs text-slate-400 flex flex-wrap items-center justify-between font-mono gap-2">
            <span>Evaluated Test Records: 41,062</span>
            <span>Actual Failing Students: 1,568 (3.82%)</span>
            <span>Total Flagged for Review: 10,967 (26.7%)</span>
          </div>
        </div>
      </div>

      {/* 3. Feature Importance */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
          <BarChart3 className="w-4 h-4" />
          <span>3. Feature Importance Attribution</span>
        </h3>
        <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 space-y-4">
          <p className="text-xs text-slate-400">
            Permutation importance distribution across the 12 student engagement indicators.
          </p>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={features}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 140, bottom: 5 }}
              >
                <XAxis type="number" unit="%" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis 
                  type="category" 
                  dataKey="name" 
                  tick={{ fill: '#cbd5e1', fontSize: 11 }} 
                  width={130}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val) => [`${val.toFixed(2)}%`, 'Importance']}
                />
                <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
                  {features.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={index === 0 ? '#3b82f6' : index < 4 ? '#2563eb' : '#6366f1'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. Model Configuration & Methodology */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-2">
          <Layers className="w-4 h-4" />
          <span>4. Model Configuration & Methodology</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-blue-400" />
              Dataset & Core Model
            </span>
            <ul className="text-xs space-y-1.5 text-slate-400">
              <li><strong className="text-slate-300">Dataset:</strong> Open University Learning Analytics Dataset (OULAD)</li>
              <li><strong className="text-slate-300">Population:</strong> 32,593 students across 22 module presentations</li>
              <li><strong className="text-slate-300">Model:</strong> Random Forest Classifier (100 estimators, max_depth=10)</li>
              <li><strong className="text-slate-300">Decision Threshold:</strong> 0.2457 (Validation-tuned cutoff)</li>
            </ul>
          </div>

          <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 space-y-2">
            <span className="text-xs font-semibold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Chronological Split Strategy
            </span>
            <ul className="text-xs space-y-1.5 text-slate-400">
              <li><strong className="text-slate-300">Training:</strong> Cohorts 2013B & 2013J (15,907 records)</li>
              <li><strong className="text-slate-300">Validation:</strong> Cohort 2014B (31,171 records) for cutoff tuning</li>
              <li><strong className="text-slate-300">Final Test:</strong> Cohort 2014J (41,062 records) evaluated once</li>
              <li className="text-[11px] text-blue-400 mt-1">Zero future temporal leakage guaranteed.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 5. Responsible AI */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4" />
          <span>5. Responsible AI & Advisory Use</span>
        </h3>
        <div className="p-5 rounded-2xl bg-gradient-to-r from-[#111827] to-[#0f172a] border border-slate-800 space-y-2.5">
          <p className="text-xs text-slate-300 leading-relaxed">
            <strong>Advisory Decision Support:</strong> Predictions generated by this platform are intended solely as early screening signals to assist educators in offering timely pedagogical support. They must never replace qualified human judgment, automate grading deductions, or trigger course disenrollment.
          </p>
          <div className="pt-2 border-t border-slate-800/80 flex flex-wrap gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Protected demographic attributes excluded to prevent algorithmic bias
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              Human-in-the-loop validation required before student outreach
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
