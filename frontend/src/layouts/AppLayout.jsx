import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import InsightAIAssistant from '../components/InsightAIAssistant';

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [analysisContext, setAnalysisContext] = useState(null);
  const location = useLocation();

  const getPageTitle = (pathname) => {
    if (pathname.includes('/model-insights')) return 'Model Insights';
    return 'Student Analysis';
  };

  return (
    <div className="min-h-screen bg-[#030712] text-[#F8FAFC] flex">
      {/* Sidebar */}
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      {/* Main Workspace Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <Navbar 
          setMobileOpen={setMobileOpen} 
          onOpenAssistant={() => setAssistantOpen(true)}
          pageTitle={getPageTitle(location.pathname)}
        />

        <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet context={{ openAssistant: () => setAssistantOpen(true), setAnalysisContext }} />
        </main>
      </div>

      {/* Persistent Insight AI Chatbot Drawer */}
      <InsightAIAssistant 
        isOpen={assistantOpen} 
        setIsOpen={setAssistantOpen}
        analysisContext={analysisContext}
      />
    </div>
  );
}
