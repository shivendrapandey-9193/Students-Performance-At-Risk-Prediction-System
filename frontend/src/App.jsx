import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Welcome from './pages/Welcome';
import AppLayout from './layouts/AppLayout';
import StudentAnalysis from './pages/StudentAnalysis';
import ModelInsights from './pages/ModelInsights';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public SaaS Landing / Welcome page (Strictly no auto-redirect!) */}
        <Route path="/" element={<Welcome />} />

        {/* Operational Workspace Layout */}
        <Route path="/app" element={<AppLayout />}>
          {/* Default /app redirects directly to student-analysis */}
          <Route index element={<Navigate to="/app/student-analysis" replace />} />
          <Route path="student-analysis" element={<StudentAnalysis />} />
          <Route path="model-insights" element={<ModelInsights />} />
        </Route>

        {/* Fallback to Welcome */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
