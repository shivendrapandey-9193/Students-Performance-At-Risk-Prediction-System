import React from 'react';
import { AlertTriangle, CheckCircle2, AlertCircle } from 'lucide-react';

export default function RiskBadge({ flagged, probability, threshold = 0.2457, size = 'md' }) {
  const isHighRisk = flagged || (probability !== undefined && probability >= threshold);
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-sm px-3 py-1 gap-1.5',
    lg: 'text-base px-4 py-1.5 gap-2 font-medium'
  };

  if (isHighRisk) {
    return (
      <span className={`inline-flex items-center rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 font-medium ${sizeClasses[size]}`}>
        <AlertTriangle className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />
        <span>Review Recommended</span>
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-medium ${sizeClasses[size]}`}>
      <CheckCircle2 className={size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />
      <span>Below Threshold (Safe)</span>
    </span>
  );
}
