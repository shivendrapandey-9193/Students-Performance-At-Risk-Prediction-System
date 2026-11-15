import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  GraduationCap, 
  ArrowRight, 
  Activity, 
  ShieldCheck, 
  FileSpreadsheet, 
  Sparkles, 
  Menu, 
  X,
  Server,
  Layers,
  Database,
  BarChart,
  Cpu,
  Code2,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

export default function Welcome() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToSection = (e, id) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#030712] text-[#F8FAFC] selection:bg-blue-600 selection:text-white flex flex-col font-sans">
      {/* ===================================================================== */}
      {/* SECTION 1 — Navigation Header */}
      {/* ===================================================================== */}
      <header className="sticky top-0 z-40 bg-[#030712]/80 backdrop-blur-md border-b border-white/[0.08]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Left: Logo & Product Name */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-white tracking-tight text-base sm:text-lg">Student Insight AI</span>
              <span className="hidden sm:inline-block ml-2 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
                AI-Powered Academic Analytics
              </span>
            </div>
          </div>

          {/* Right: Desktop Links */}
          <div className="hidden md:flex items-center gap-6">
            <a
              href="#benchmarks"
              onClick={(e) => scrollToSection(e, 'benchmarks')}
              className="text-xs sm:text-sm text-[#94A3B8] hover:text-white transition"
            >
              Model Benchmarks
            </a>
            <Link
              to="/app/student-analysis"
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs sm:text-sm transition shadow-sm shadow-blue-500/20 active:scale-95"
            >
              <span>Launch Platform</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-400 hover:text-white rounded-lg focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-white/[0.08] bg-[#0F172A] px-4 py-4 space-y-3">
            <a
              href="#benchmarks"
              onClick={(e) => scrollToSection(e, 'benchmarks')}
              className="block text-sm text-[#94A3B8] hover:text-white py-1"
            >
              Model Benchmarks
            </a>
            <Link
              to="/app/student-analysis"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition"
            >
              <span>Launch Platform</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        )}
      </header>

      {/* ===================================================================== */}
      {/* SECTION 2 — Hero Section */}
      {/* ===================================================================== */}
      <section className="pt-12 sm:pt-20 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Headline, Subtitle, CTAs */}
          <div className="lg:col-span-7 space-y-6 text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#111827] border border-white/[0.08] text-xs text-[#94A3B8]">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              <span>Trained on Open University Learning Analytics Dataset (OULAD)</span>
            </div>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#F8FAFC] leading-[1.1]">
              Predict Academic Risk{' '}
              <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-blue-200 bg-clip-text text-transparent">
                Weeks Before Failure
              </span>
            </h1>

            <p className="text-sm sm:text-base text-[#94A3B8] leading-relaxed max-w-xl">
              An advisory early-warning intelligence platform for university educators. Analyzes virtual learning environment (VLE) interaction patterns to identify struggling students before midterm assessments are submitted.
            </p>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
              <Link
                to="/app/student-analysis"
                className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-600/25 active:scale-95"
              >
                <span>Explore Analytics Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/app/student-analysis"
                className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-[#111827] hover:bg-[#1f2937] text-white font-medium text-sm transition border border-white/[0.08]"
              >
                <span>Try Batch & Student Screening</span>
              </Link>
            </div>
          </div>

          {/* Right Column: Hero Visual (Product Preview) */}
          <div className="lg:col-span-5">
            <div className="rounded-2xl border border-white/[0.08] bg-[#111827] shadow-2xl p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 text-[11px] font-mono text-[#94A3B8]">student-insight.app</span>
                </div>
                <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                  Sample Preview
                </span>
              </div>

              {/* Student Risk Gauge Preview */}
              <div className="p-3.5 rounded-xl bg-[#0F172A] border border-white/[0.08] space-y-2">
                <div className="flex justify-between items-baseline text-xs">
                  <span className="text-white font-medium">Student Risk Gauge</span>
                  <span className="text-rose-400 font-bold font-mono">Risk: 68.4%</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-amber-500 to-rose-500 w-[68.4%]" />
                </div>
                <div className="text-[11px] text-rose-300 leading-snug bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
                  ⚠️ Low VLE engagement in last 14 days. Review suggested before TMA cutoff.
                </div>
              </div>

              {/* Cohort Distribution Preview */}
              <div className="p-3.5 rounded-xl bg-[#0F172A] border border-white/[0.08] space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-white font-medium">Cohort Distribution</span>
                  <span className="text-blue-400 font-mono text-[11px]">Cohort 2014J</span>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800 text-center">
                    <span className="text-xs text-[#94A3B8] block">Safe Baseline</span>
                    <span className="text-sm font-bold text-emerald-400 font-mono">73.3%</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800 text-center">
                    <span className="text-xs text-[#94A3B8] block">Early Warning</span>
                    <span className="text-sm font-bold text-rose-400 font-mono">26.7%</span>
                  </div>
                </div>
              </div>

              {/* AI Assistant Guidance Preview */}
              <div className="p-3 rounded-xl bg-gradient-to-r from-blue-950/30 to-indigo-950/30 border border-blue-500/20 text-xs space-y-1">
                <div className="flex items-center gap-1.5 text-blue-400 font-semibold text-[11px]">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>AI Assistant Guidance</span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed italic">
                  "Recommend connecting student with peer study group for module BBB."
                </p>
              </div>

              <div className="text-[10px] text-slate-400 text-center pt-1">
                Illustrative interface composition • Not actual student data
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===================================================================== */}
      {/* SECTION 3 — Model Benchmarks */}
      {/* ===================================================================== */}
      <section id="benchmarks" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-white/[0.08]">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Model Benchmarks
          </h2>
          <p className="text-xs sm:text-sm text-[#94A3B8] mt-1.5">
            Verified performance metrics evaluated on held-out test cohort 2014J.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1 */}
          <div className="p-5 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <span className="text-xs font-medium uppercase tracking-wider text-[#94A3B8] block">Target Recall</span>
            <div className="text-3xl font-extrabold text-emerald-400 mt-2">63.52%</div>
            <p className="text-xs text-[#94A3B8] mt-2">Captures failing students.</p>
          </div>

          {/* Card 2 */}
          <div className="p-5 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <span className="text-xs font-medium uppercase tracking-wider text-[#94A3B8] block">Overall Accuracy</span>
            <div className="text-3xl font-extrabold text-white mt-2">74.32%</div>
            <p className="text-xs text-[#94A3B8] mt-2">Balanced threshold policy.</p>
          </div>

          {/* Card 3 */}
          <div className="p-5 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <span className="text-xs font-medium uppercase tracking-wider text-[#94A3B8] block">Test Population</span>
            <div className="text-3xl font-extrabold text-blue-400 mt-2">41,062</div>
            <p className="text-xs text-[#94A3B8] mt-2">Unseen 2014J blind cohort.</p>
          </div>

          {/* Card 4 */}
          <div className="p-5 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <span className="text-xs font-medium uppercase tracking-wider text-[#94A3B8] block">Decision Threshold</span>
            <div className="text-3xl font-extrabold text-indigo-400 mt-2">0.2457</div>
            <p className="text-xs text-[#94A3B8] mt-2">Validation-tuned cutoff.</p>
          </div>
        </div>
      </section>

      {/* ===================================================================== */}
      {/* SECTION 4 — Product Capabilities */}
      {/* ===================================================================== */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-white/[0.08]">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Engineered for Real-World Academic Interventions
          </h2>
          <p className="text-xs sm:text-sm text-[#94A3B8] mt-2">
            Why traditional grading metrics fail, and how behavioral clickstream modeling succeeds.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Feature 1 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-4">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">12 Behavioral Features</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Ingests pre-assessment interaction records, 7-day, 14-day, and 30-day click recency windows, and login consistency.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Recall-Focused Policy</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Tuned decision cutoff (0.2457) achieves 63.52% recall, prioritizing finding struggling students over empty 90%+ accuracy.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Batch Cohort Triage</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Upload institutional CSV logs with thousands of enrolled students. Instant vectorized inference and risk sorting.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] hover:border-slate-700 transition">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mb-4">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white mb-2">Insight AI Assistant</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Integrated Groq-powered domain AI assistant trained with our complete project context, metric rationale, and ML pipeline.
            </p>
          </div>
        </div>
      </section>

      {/* ===================================================================== */}
      {/* SECTION 5 — How It Works */}
      {/* ===================================================================== */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-white/[0.08]">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            How The Early-Warning Pipeline Operates
          </h2>
          <p className="text-xs sm:text-sm text-[#94A3B8] mt-2">
            Chronological integrity with zero future data leakage.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {/* Step 01 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] space-y-2 relative">
            <span className="text-[11px] font-mono text-blue-400 font-semibold tracking-wider block uppercase">Step 01</span>
            <h3 className="text-base font-bold text-white">VLE Stream Aggregation</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Captures interaction click logs up to the assessment target cutoff date. Eliminates post-cutoff feedback leakage.
            </p>
          </div>

          {/* Step 02 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] space-y-2 relative">
            <span className="text-[11px] font-mono text-indigo-400 font-semibold tracking-wider block uppercase">Step 02</span>
            <h3 className="text-base font-bold text-white">Calibrated Model Inference</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Evaluates students through our Random Forest pipeline utilizing the validation-tuned 0.2457 decision boundary.
            </p>
          </div>

          {/* Step 03 */}
          <div className="p-6 rounded-2xl bg-[#111827] border border-white/[0.08] space-y-2 relative">
            <span className="text-[11px] font-mono text-emerald-400 font-semibold tracking-wider block uppercase">Step 03</span>
            <h3 className="text-base font-bold text-white">Educator Intervention</h3>
            <p className="text-xs text-[#94A3B8] leading-relaxed">
              Advisors receive actionable flags and contact students proactively with personalized tutoring and support.
            </p>
          </div>
        </div>
      </section>

      {/* ===================================================================== */}
      {/* SECTION 6 — Technology Architecture */}
      {/* ===================================================================== */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full border-t border-white/[0.08]">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Full-Stack Production Architecture
          </h2>
          <p className="text-xs sm:text-sm text-[#94A3B8] mt-1.5">
            Enterprise-grade decoupled architecture with zero mock inference.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {[
            { name: "React.js 18 (Vite)", role: "Frontend SPA", icon: Code2 },
            { name: "Tailwind CSS", role: "UI Styling", icon: Layers },
            { name: "Node.js & Express", role: "API Gateway", icon: Server },
            { name: "Python FastAPI", role: "ML Microservice", icon: Cpu },
            { name: "Scikit-Learn Random Forest", role: "Core Classifier", icon: Database },
            { name: "Groq Cloud LLM", role: "Qwen 2.5 27B (qwen3.8-27b)", icon: Sparkles },
            { name: "Recharts", role: "Visualizations", icon: BarChart },
          ].map((tech, i) => (
            <div key={i} className="p-4 rounded-xl bg-[#111827] border border-white/[0.08] flex items-center gap-3">
              <tech.icon className="w-5 h-5 text-blue-400 shrink-0" />
              <div>
                <span className="text-xs font-semibold text-white block">{tech.name}</span>
                <span className="text-[10px] text-[#94A3B8] font-mono">{tech.role}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ===================================================================== */}
      {/* SECTION 7 — Final Call To Action */}
      {/* ===================================================================== */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto w-full text-center">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-b from-[#111827] to-[#030712] border border-white/[0.08] shadow-2xl space-y-6">
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Ready to Explore the Platform?
          </h2>
          <p className="text-xs sm:text-sm text-[#94A3B8] max-w-lg mx-auto leading-relaxed">
            Experience live student risk prediction, upload cohort spreadsheets, inspect feature importances, and interact with the Groq AI companion.
          </p>
          <div className="pt-2">
            <Link
              to="/app/student-analysis"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-600/25 active:scale-95"
            >
              <span>Launch Student Insight AI</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ===================================================================== */}
      {/* SECTION 8 — Footer */}
      {/* ===================================================================== */}
      <footer className="mt-auto border-t border-white/[0.08] bg-[#030712] py-8 px-4 text-xs text-[#94A3B8]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-blue-400" />
            <span className="font-semibold text-white">Student Insight AI</span>
            <span>— Academic Analytics Platform</span>
          </div>

          <div className="flex items-center gap-6">
            <a 
              href="#benchmarks" 
              onClick={(e) => scrollToSection(e, 'benchmarks')}
              className="hover:text-white transition"
            >
              Model Benchmarks
            </a>
            <Link to="/app/student-analysis" className="hover:text-white transition">
              Launch Platform
            </Link>
          </div>
        </div>

        <div className="max-w-7xl mx-auto mt-4 pt-4 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-2">
          <span>© 2026 Student Insight AI. All rights reserved.</span>
          <span>Advisory disclaimer: Predictions are screening estimates intended to support educators and must never replace qualified human judgment.</span>
        </div>
      </footer>
    </div>
  );
}
