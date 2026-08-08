import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import { fetchStatus } from './api';

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [sysStatus, setSysStatus] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fix Kiosk Memory Leaks: Force a hard refresh every 30 minutes
  useEffect(() => {
    const reloadTimer = setTimeout(() => {
      window.location.reload();
    }, 1800000); // 30 minutes
    return () => clearTimeout(reloadTimer);
  }, []);

  useEffect(() => {
    const loadTemp = async () => {
      const st = await fetchStatus();
      if (st) setSysStatus(st);
    };
    loadTemp();
    const poll = setInterval(loadTemp, 5000);
    return () => clearInterval(poll);
  }, []);

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
  };
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      <header className="bg-surface border-b border-surface-variant flex justify-between items-center w-full px-8 h-[60px] top-0 z-40 shrink-0">
        <div className="text-3xl font-black text-on-surface flex items-center gap-2">
          {formatTime(currentTime)} &bull; {formatDate(currentTime)}
        </div>
        <div className="flex items-center gap-6 text-on-surface-variant">
          <div className="flex items-center gap-2 bg-surface-container-low border border-surface-variant p-2 px-3 rounded-lg shadow-sm">
            {sysStatus?.cooling_active && (
              <span className="material-symbols-outlined text-[24px] text-primary animate-pulse" title="Cooling Active">
                ac_unit
              </span>
            )}
            <span className="material-symbols-outlined text-[28px]">thermostat</span>
            <div className="flex flex-col text-sm font-bold leading-none">
              <span>{sysStatus?.temperature !== undefined ? `${sysStatus.temperature}°C` : '--°C'}</span>
              <span className="text-xs text-on-surface-variant font-medium">
                {sysStatus?.humidity !== undefined ? `${sysStatus.humidity}% Hum` : '--%'}
              </span>
            </div>
          </div>
          <div className="flex flex-col items-center hover:bg-surface-container-high p-1 rounded-lg cursor-pointer active:scale-95 transition-transform duration-150">
            <span className="material-symbols-outlined text-[28px]">bluetooth</span>
          </div>
        </div>
      </header>
      
      <Dashboard />
    </>
  );
}

export default App;
