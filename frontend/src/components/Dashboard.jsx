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
  
  // State for legend tooltip
  const [showLegend, setShowLegend] = useState(false);

  // State for 5s UI toggle
  const [showDecagon, setShowDecagon] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const toggleTimer = setInterval(() => {
      setShowDecagon(prev => !prev);
    }, 5000);
    return () => clearInterval(toggleTimer);
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

  const isDispensing = status?.is_dispense_window_active;
  const activeSlot = isDispensing ? status?.active_compartment_id : null;

  return (
    <div className="flex-grow flex flex-row p-2 gap-2 overflow-hidden">
      
      {/* Left Pane (60%): Interactive Dispenser View */}
      <section className="w-[60%] h-full flex flex-col items-center justify-center bg-surface-container-lowest rounded-xl border-2 border-surface-variant relative shadow-sm p-2">
        
        {/* Legend Button */}
        {!isDispensing && (
          <div className="absolute top-2 left-2 z-10">
            <button 
              onClick={() => setShowLegend(!showLegend)}
              className="flex items-center gap-1 bg-surface-container px-2 py-1 rounded-full border border-surface-variant hover:bg-surface-variant transition-colors"
            >
              <span className="material-symbols-outlined text-[18px] text-on-surface-variant">help</span>
              <span className="text-xs text-on-surface">Legend</span>
            </button>
            
            {/* Legend Tooltip */}
            {showLegend && (
              <div className="absolute top-14 left-0 bg-surface-container-highest border-2 border-surface-variant rounded-xl p-4 shadow-xl w-64 flex flex-col gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-md bg-surface-container border-2 border-surface-dim"></div>
                  <span className="font-body-md text-on-surface">Empty Slot</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-md bg-secondary-fixed border-2 border-secondary-fixed-dim"></div>
                  <span className="font-body-md text-on-surface">Scheduled Slot</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-md bg-tertiary-fixed border-2 border-tertiary-fixed-dim animate-pulse"></div>
                  <span className="font-body-md text-on-surface">Active (Time to Take!)</span>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex-grow flex items-center justify-center w-full max-h-[95%]">
          {(showDecagon || isDispensing) ? (
             <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
          ) : (
             <div className="w-full h-full overflow-y-auto bg-surface rounded-lg p-2 flex flex-col gap-2">
                <h2 className="text-center font-bold text-on-surface mb-1">Current Schedules</h2>
                {schedules.length === 0 && <p className="text-center text-xs text-on-surface-variant">No schedules set.</p>}
                {schedules.map(sch => (
                   <div key={sch.compartment_id} className="bg-surface-container p-2 rounded-md border border-surface-variant flex justify-between items-center cursor-pointer" onClick={() => handleSlotClick(sch.compartment_id)}>
                      <div className="flex flex-col">
                         <span className="font-bold text-xs text-on-surface">Slot {sch.compartment_id}: {sch.medicine_name}</span>
                         <span className="text-[10px] text-on-surface-variant">{sch.frequency.replace('_', ' ')}</span>
                      </div>
                      <div className="flex flex-col items-end">
                         {sch.time_slots.split(',').map((t, idx) => (
                            <span key={idx} className="text-[10px] font-mono text-primary">{t}</span>
                         ))}
                      </div>
                   </div>
                ))}
             </div>
          )}
        </div>
      </section>

      {/* Right Pane (40%): Action Area */}
      <section className="w-[40%] h-full flex flex-col gap-2">
        
        {isDispensing ? (
          <div className="bg-error-container border-2 border-error text-on-error-container rounded-xl flex-[1] flex flex-col items-center justify-center text-center shadow-md p-2">
             <span className="material-symbols-outlined text-[48px] mb-1 animate-pulse">warning</span>
             <h2 className="text-xs font-bold mb-1">TIME TO TAKE MEDICATION</h2>
             <div className="text-4xl font-bold font-mono tracking-wider animate-pulse">
                {formatCountdown(status?.dispense_countdown_seconds)}
             </div>
          </div>
        ) : (
          <div className="bg-surface-container-lowest rounded-xl border-2 border-surface-variant p-2 flex flex-col items-center justify-center text-center shadow-sm flex-[1]">
            <h2 className="text-sm font-bold text-on-background mb-1">Next Dose:</h2>
            <div className="text-xl text-primary font-bold mb-1 line-clamp-1">
              {status?.next_dose_time || "None"}
            </div>
            <div className="text-xs text-on-surface-variant bg-surface-container px-2 py-1 rounded inline-block line-clamp-2">
              {status?.next_dose_med || "No medication scheduled"}
            </div>
          </div>
        )}

        {/* Primary Action Button */}
        <button 
          onClick={handleMedicineTaken}
          className={`w-full rounded-xl flex flex-col items-center justify-center shadow-sm transition-all p-2 flex-[1] group border-2 ${isDispensing ? 'bg-tertiary-container text-on-tertiary-container border-tertiary hover:brightness-105 active:bg-tertiary' : 'bg-surface-container text-on-surface-variant border-surface-variant opacity-50 cursor-not-allowed'}`}
        >
          <span className="material-symbols-outlined text-[40px] mb-1 group-active:scale-90 transition-transform">touch_app</span>
          <span className="text-sm font-bold">{isDispensing ? "DISPENSE" : "LOCKED"}</span>
        </button>
        
        {/* Secondary Action/Status */}
        <div className="flex items-center justify-center h-8">
          <div className="flex items-center gap-2 bg-surface-container-low px-3 py-1 rounded-full border border-surface-variant shadow-sm">
            <span className="material-symbols-outlined text-on-surface-variant text-[16px]">schedule</span>
            <span className="text-xs text-on-surface-variant">System Active</span>
          </div>
        </div>

      </section>

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
