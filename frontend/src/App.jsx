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
      <header className="bg-surface border-b-2 border-surface-variant flex justify-between items-center w-full px-margin-page h-[120px] top-0 z-40">
        <div className="font-headline-lg text-headline-lg font-bold text-on-surface flex items-center gap-4">
          {formatTime(currentTime)} &bull; {formatDate(currentTime)}
        </div>
        <div className="flex items-center gap-gutter text-on-surface-variant">
          <div className="flex flex-col items-center hover:bg-surface-container-high p-2 rounded-lg cursor-pointer active:scale-95 transition-transform duration-150">
            <span className="material-symbols-outlined text-[40px]">bluetooth</span>
          </div>
          <div className="flex items-center gap-2 font-headline-md text-headline-md bg-surface-container-low border-2 border-surface-variant p-2 rounded-lg shadow-sm">
            {sysStatus?.cooling_active && (
              <span className="material-symbols-outlined text-[32px] text-primary animate-pulse mr-1" title="Cooling Active">
                ac_unit
              </span>
            )}
            <span className="material-symbols-outlined text-[40px]">thermostat</span>
            <div className="flex flex-col">
              <span>{sysStatus?.temperature !== undefined ? `${sysStatus.temperature}°C` : '--°C'}</span>
              <span className="text-sm text-on-surface-variant font-medium leading-tight">
                {sysStatus?.humidity !== undefined ? `${sysStatus.humidity}% Hum` : '--% Hum'}
              </span>
            </div>
          </div>
        </div>
      </header>
      
      <Dashboard />
    </>
  );
}

export default App;
