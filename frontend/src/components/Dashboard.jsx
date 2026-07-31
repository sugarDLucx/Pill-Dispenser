import React, { useState, useEffect } from 'react';
import Decagon from './Decagon';
import ScheduleModal from './ScheduleModal';
import { fetchStatus, fetchSchedules, markMedicineTaken } from '../api';

const Dashboard = () => {
  const [schedules, setSchedules] = useState([]);
  const [status, setStatus] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // State for modal
  const [modalSlot, setModalSlot] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const loadData = async () => {
    const sch = await fetchSchedules();
    if (sch) setSchedules(sch);
    const st = await fetchStatus();
    if (st) setStatus(st);
  };

  useEffect(() => {
    loadData();
    const poll = setInterval(loadData, 1000); // Poll faster to get real-time countdown
    return () => clearInterval(poll);
  }, []);

  const handleMedicineTaken = async () => {
    if (!status?.is_dispense_window_active) {
       alert("Medication is time-locked. You can only dispense when it's time.");
       return;
    }
    await markMedicineTaken();
  };

  const handleSlotClick = (id) => {
    // Disable editing during dispense window
    if (status?.is_dispense_window_active) return;
    setModalSlot(id);
  };

  const formatCountdown = (secs) => {
    if (!secs) return "0:00";
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const formatTime12Hour = (timeStr) => {
    if (!timeStr) return "";
    const [h, m] = timeStr.split(':');
    let hour = parseInt(h, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    hour = hour % 12;
    hour = hour ? hour : 12;
    return `${hour}:${m} ${ampm}`;
  };

  const isDispensing = status?.is_dispense_window_active;
  const activeSlot = isDispensing ? status?.active_compartment_id : null;

  // --- RENDERING VIEWS ---

  return (
    <div className="flex-grow w-full h-full overflow-hidden relative flex flex-row p-2 gap-2 bg-surface-container-lowest">
      
      {/* LEFT COLUMN: Decagon */}
      <div className="w-[50%] h-full relative flex flex-col items-center justify-start p-2">
        {/* Horizontal Legend */}
        <div className="w-full z-10 flex flex-row items-center justify-center gap-4 bg-surface-container-highest/60 backdrop-blur rounded-full px-4 py-1 border border-surface-variant shadow-sm mb-2">
          <span className="font-bold text-on-surface text-xs mr-2">Legend:</span>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-surface-container border border-surface-dim"></div>
            <span className="font-bold text-on-surface text-[10px]">Empty</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-secondary-fixed border border-secondary-fixed-dim"></div>
            <span className="font-bold text-on-surface text-[10px]">Scheduled</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-tertiary-fixed border border-tertiary-fixed-dim"></div>
            <span className="font-bold text-on-surface text-[10px]">Active</span>
          </div>
        </div>
        
        {/* Wrapper to bound the Decagon strictly to its parent height. Added -mt-8 to move it higher. */}
        <div className="w-full h-full max-h-full flex items-start justify-center overflow-hidden -mt-8">
          <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
        </div>
      </div>

      {/* RIGHT COLUMN: Huge Next Dose */}
      {/* Added pr-10 and pb-16 to add even more padding to the right and bottom */}
      <div className="w-[50%] h-full flex flex-col gap-2 p-2 pr-10 pb-16">
        <div className="bg-surface-container-low h-full w-full rounded-2xl border-4 border-surface-variant p-4 flex flex-col items-center justify-center text-center shadow-lg">
          <h2 className="text-3xl font-black text-on-surface-variant mb-4">NEXT DOSE</h2>
          <div className="text-6xl text-primary font-black tracking-tight mb-6">
            {status?.next_dose_time || "None"}
          </div>
          <div className="text-3xl font-black text-on-surface bg-surface-container-high px-6 py-3 rounded-xl shadow-inner border-2 border-surface-variant">
            {status?.next_dose_med?.toUpperCase() || "NO MEDICATION SCHEDULED"}
          </div>
        </div>
      </div>

      {/* DISPENSE OVERLAY MODAL */}
      {isDispensing && (
        <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
           <div className="bg-surface-container-lowest w-[90%] max-w-[600px] h-[90%] rounded-2xl border-4 border-error shadow-2xl flex flex-row overflow-hidden">
             
             {/* Left side: Alert Text */}
             <div className="w-[60%] bg-error-container text-on-error-container flex flex-col items-center justify-center p-4 text-center">
                <span className="material-symbols-outlined text-[64px] mb-2 animate-pulse">warning</span>
                <h2 className="text-2xl font-black mb-2 uppercase">Time To Take Medication</h2>
                <div className="text-7xl font-black font-mono tracking-widest animate-pulse">
                   {formatCountdown(status?.dispense_countdown_seconds)}
                </div>
             </div>

             {/* Right side: Dispense Button */}
             <div className="w-[40%] flex items-center justify-center bg-tertiary-container p-4">
               <button 
                onClick={handleMedicineTaken}
                className="w-full h-full rounded-xl flex flex-col items-center justify-center shadow-lg transition-all border-4 bg-tertiary text-on-tertiary border-tertiary-fixed hover:brightness-110 active:scale-95 group"
               >
                <span className="material-symbols-outlined text-[64px] mb-4 group-active:scale-90 transition-transform">touch_app</span>
                <span className="text-2xl font-black tracking-wider text-center">DISPENSE<br/>NOW</span>
               </button>
             </div>
           </div>
        </div>
      )}

      {/* EDIT SCHEDULE MODAL */}
      {modalSlot !== null && !isDispensing && (
        <ScheduleModal 
          slotId={modalSlot} 
          initialData={schedules.find(s => s.compartment_id === modalSlot) || null}
          onClose={() => setModalSlot(null)}
          onSave={loadData}
        />
      )}
    </div>
  );
};

export default Dashboard;
