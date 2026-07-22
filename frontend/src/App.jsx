import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
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
          <div className="flex items-center gap-2 font-headline-md text-headline-md hover:bg-surface-container-high p-2 rounded-lg cursor-pointer active:scale-95 transition-transform duration-150">
            <span className="material-symbols-outlined text-[40px]">thermostat</span>
            72°F
          </div>
        </div>
      </header>
      
      <Dashboard />
    </>
  );
}

export default App;
