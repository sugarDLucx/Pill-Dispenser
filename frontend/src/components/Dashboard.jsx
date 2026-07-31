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
      <div className="w-[55%] h-full relative flex items-center justify-center p-2">
        <div className="absolute top-0 left-0 z-10 flex flex-col gap-1 bg-surface-container-highest/90 backdrop-blur rounded-lg p-2 border border-surface-variant shadow-md">
          <h3 className="font-bold text-on-surface text-xs text-center border-b border-surface-variant pb-1">Legend</h3>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-surface-container border border-surface-dim"></div>
            <span className="font-bold text-on-surface text-xs">Empty</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-secondary-fixed border border-secondary-fixed-dim"></div>
            <span className="font-bold text-on-surface text-xs">Scheduled</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-tertiary-fixed border border-tertiary-fixed-dim"></div>
            <span className="font-bold text-on-surface text-xs">Active</span>
          </div>
        </div>
        <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
      </div>

      {/* RIGHT COLUMN: Schedules and Next Dose */}
      <div className="w-[45%] h-full flex flex-col gap-2">
        
        {/* Next Dose Header */}
        <div className="bg-surface-container rounded-xl border border-surface-variant p-2 flex flex-col items-center justify-center text-center shadow-sm shrink-0">
          <h2 className="text-sm font-bold text-on-background">Next Dose:</h2>
          <div className="text-xl text-primary font-black">
            {status?.next_dose_time || "None"}
          </div>
          <div className="text-xs font-bold text-on-surface-variant bg-surface-container-high px-2 py-1 rounded mt-1">
            {status?.next_dose_med?.toUpperCase() || "NO MEDICATION"}
          </div>
        </div>

        {/* Schedules List */}
        <div className="flex-grow overflow-y-auto bg-surface-container-low rounded-xl border border-surface-variant shadow-sm p-2 flex flex-col gap-2 no-scrollbar">
          <h2 className="text-center font-bold text-on-surface text-sm border-b border-surface-variant pb-1">Schedules</h2>
          {schedules.length === 0 && <p className="text-center text-on-surface-variant text-sm mt-2">No schedules.</p>}
          {schedules.map(sch => (
              <div key={sch.compartment_id} className="bg-surface-container p-2 rounded-lg border border-surface-variant flex justify-between items-center cursor-pointer hover:bg-surface-variant transition-colors" onClick={() => handleSlotClick(sch.compartment_id)}>
                <div className="flex flex-col">
                    <span className="font-bold text-sm text-on-surface">Slot {sch.compartment_id}: {sch.medicine_name.toUpperCase()}</span>
                    <span className="text-xs text-on-surface-variant font-medium">{sch.frequency.replace('_', ' ').toUpperCase()}</span>
                </div>
                <div className="flex flex-col items-end">
                    {sch.time_slots.split(',').map((t, idx) => (
                      <span key={idx} className="text-xs font-mono font-bold text-primary">{formatTime12Hour(t)}</span>
                    ))}
                </div>
              </div>
          ))}
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
