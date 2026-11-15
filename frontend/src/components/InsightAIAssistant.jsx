import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  X, 
  Send, 
  Trash2, 
  Bot, 
  User, 
  Loader2, 
  Maximize2, 
  Minimize2,
  HelpCircle,
  ChevronRight
} from 'lucide-react';
import { askInsightAI } from '../services/api';

const SUGGESTED_QUESTIONS = [
  "Explain This Project",
  "Explain the ML Architecture",
  "What Challenges Did We Solve?",
  "Explain Model Performance",
  "Prepare Me for Interviews",
  "How Does Student Prediction Work?"
];

export default function InsightAIAssistant({ isOpen, setIsOpen, analysisContext }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I am **Insight AI Assistant**, your technical and domain expert for this platform.\n\nI have complete knowledge of our architecture, the **OULAD dataset**, our **Random Forest** model, and our **74.32% accuracy / 63.52% recall** benchmark.\n\nHow can I help you today? You can choose a quick topic below or type your own question.`
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || input.trim();
    if (!query || loading) return;

    const userMessage = { role: 'user', content: query };
    const updatedHistory = [...messages, userMessage];
    setMessages(updatedHistory);
    setInput('');
    setLoading(true);

    try {
      const assistantReply = await askInsightAI(updatedHistory, analysisContext);
      setMessages([...updatedHistory, { role: 'assistant', content: assistantReply }]);
    } catch (error) {
      console.error('Chat error:', error);
      const errMsg = error.message || 'Error connecting to AI service.';
      setMessages([
        ...updatedHistory, 
        { role: 'assistant', content: `⚠️ **Notice:** ${errMsg}\n\nPlease check the backend service configuration and try again.` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: `Chat history cleared. How can I assist you with the Student Insight AI project?`
      }
    ]);
  };

  return (
    <>
      {/* Floating Trigger Button (Bottom Right) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-sky-500 to-indigo-600 text-white font-semibold text-sm shadow-xl shadow-sky-500/25 hover:shadow-sky-500/40 hover:scale-105 active:scale-95 transition-all group"
          title="Open Insight AI Assistant"
        >
          <div className="relative">
            <Sparkles className="w-5 h-5 text-white animate-spin-slow" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 border-2 border-slate-900 rounded-full" />
          </div>
          <span className="pr-1">Insight AI Assistant</span>
        </button>
      )}

      {/* Slide-out Drawer */}
      <div
        className={`fixed top-0 bottom-0 right-0 z-50 bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 shadow-2xl flex flex-col transition-all duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        } ${expanded ? 'w-full sm:w-[650px]' : 'w-full sm:w-[460px]'}`}
      >
        {/* Drawer Header */}
        <div className="h-16 px-5 border-b border-slate-800 flex items-center justify-between shrink-0 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500/20 to-indigo-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-white text-sm">Insight AI Assistant</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  Groq LLM
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Project-Aware Academic Intelligence</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg hidden sm:block transition"
              title={expanded ? "Shrink drawer" : "Expand drawer"}
            >
              {expanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={handleClearChat}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
              title="Clear chat history"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
              title="Close drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Suggested Quick Question Chips */}
        <div className="px-4 py-2.5 bg-slate-950/30 border-b border-slate-800/60 overflow-x-auto whitespace-nowrap scrollbar-none flex items-center gap-2">
          <span className="text-[10px] uppercase font-semibold text-slate-400 flex items-center gap-1 shrink-0">
            <HelpCircle className="w-3 h-3 text-sky-400" /> Prompts:
          </span>
          {SUGGESTED_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q)}
              disabled={loading}
              className="text-[11px] px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/60 hover:border-sky-500/40 transition shrink-0 flex items-center gap-1 disabled:opacity-50"
            >
              <span>{q}</span>
              <ChevronRight className="w-3 h-3 text-slate-400" />
            </button>
          ))}
        </div>

        {/* Message History Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={index}
                className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
              >
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                    isUser
                      ? 'bg-indigo-600 text-white'
                      : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed ${
                    isUser
                      ? 'bg-indigo-600 text-white rounded-tr-none'
                      : 'bg-slate-800/90 text-slate-200 border border-slate-700/70 rounded-tl-none'
                  }`}
                >
                  <div className="prose prose-invert prose-xs max-w-none space-y-2 whitespace-pre-wrap break-words">
                    {msg.content}
                  </div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex gap-3 items-center text-slate-400 text-xs pl-2">
              <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
              <span>Insight AI is thinking...</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-slate-950/70 border-t border-slate-800">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about the model, metrics, code, or architecture..."
              disabled={loading}
              className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500 focus:border-sky-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 disabled:opacity-40 disabled:hover:bg-sky-500 font-semibold transition active:scale-95"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="mt-2 text-[10px] text-slate-400 text-center flex items-center justify-center gap-1">
            <span>Ground truth validated on OULAD 2014J cohort</span>
            <span>•</span>
            <span className="text-sky-400">Advisory Support Only</span>
          </div>
        </div>
      </div>
    </>
  );
}
