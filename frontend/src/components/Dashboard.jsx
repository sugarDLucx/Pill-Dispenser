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
  
  // State for 5s UI toggle
  const [showDecagonView, setShowDecagonView] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const toggleTimer = setInterval(() => {
      setShowDecagonView(prev => !prev);
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

  // View A: The Decagon & Permanent Legend
  const renderDecagonView = () => (
    <div className="w-full h-full relative bg-surface-container-lowest flex items-center justify-center p-0 m-0">
      
      {/* Absolute Legend */}
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-2 bg-surface-container-highest/90 backdrop-blur rounded-lg p-3 border-2 border-surface-variant shadow-md">
        <h3 className="font-bold text-on-surface text-sm text-center border-b border-surface-variant pb-1">Legend</h3>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-surface-container border-2 border-surface-dim"></div>
          <span className="font-bold text-on-surface text-sm">Empty</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-secondary-fixed border-2 border-secondary-fixed-dim"></div>
          <span className="font-bold text-on-surface text-sm">Scheduled</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-tertiary-fixed border-2 border-tertiary-fixed-dim"></div>
          <span className="font-bold text-on-surface text-sm">Active</span>
        </div>
      </div>

      <div className="w-full h-full flex justify-center items-center">
        <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
      </div>
    </div>
  );

  // View B: Schedule List & Next Dose
  const renderScheduleView = () => (
    <div className="w-full h-full flex flex-row p-2 gap-4">
      <div className="w-[60%] h-full overflow-y-auto bg-surface-container-lowest rounded-xl border-2 border-surface-variant shadow-sm p-4 flex flex-col gap-3">
        <h2 className="text-center font-bold text-on-surface text-xl border-b border-surface-variant pb-2">Current Schedules</h2>
        {schedules.length === 0 && <p className="text-center text-on-surface-variant text-lg mt-4">No schedules set.</p>}
        {schedules.map(sch => (
            <div key={sch.compartment_id} className="bg-surface-container p-3 rounded-lg border-2 border-surface-variant flex justify-between items-center cursor-pointer hover:bg-surface-variant transition-colors" onClick={() => handleSlotClick(sch.compartment_id)}>
              <div className="flex flex-col">
                  <span className="font-bold text-lg text-on-surface">Slot {sch.compartment_id}: {sch.medicine_name.toUpperCase()}</span>
                  <span className="text-sm text-on-surface-variant font-medium">{sch.frequency.replace('_', ' ').toUpperCase()}</span>
              </div>
              <div className="flex flex-col items-end">
                  {sch.time_slots.split(',').map((t, idx) => (
                    <span key={idx} className="text-sm font-mono font-bold text-primary">{formatTime12Hour(t)}</span>
                  ))}
              </div>
            </div>
        ))}
      </div>
      <div className="w-[40%] h-full flex flex-col gap-4">
        <div className="bg-surface-container-lowest rounded-xl border-2 border-surface-variant p-4 flex flex-col items-center justify-center text-center shadow-sm flex-grow">
          <h2 className="text-lg font-bold text-on-background mb-2">Next Dose:</h2>
          <div className="text-3xl text-primary font-black mb-2">
            {status?.next_dose_time || "None"}
          </div>
          <div className="text-lg font-bold text-on-surface-variant bg-surface-container px-4 py-2 rounded-lg">
            {status?.next_dose_med?.toUpperCase() || "NO MEDICATION"}
          </div>
        </div>
        <div className="flex items-center justify-center bg-surface-container-low p-4 rounded-xl border-2 border-surface-variant shadow-sm">
          <span className="material-symbols-outlined text-on-surface-variant text-[24px] mr-2">schedule</span>
          <span className="text-lg font-bold text-on-surface-variant">System Active & Locked</span>
        </div>
      </div>
    </div>
  );

  // View C: Dispensing Mode (Full Screen Takeover)
  const renderDispenseView = () => (
    <div className="w-full h-full flex flex-row p-2 gap-4">
      <div className="w-[45%] h-full bg-surface-container-lowest rounded-xl border-2 border-surface-variant shadow-sm p-2 flex flex-col items-center justify-center">
         <h2 className="text-lg font-bold text-on-surface mb-2">Dispensing Slot:</h2>
         <div className="w-full h-[80%] flex justify-center items-center">
            <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
         </div>
      </div>
      <div className="w-[55%] h-full flex flex-col gap-4">
         <div className="bg-error-container border-4 border-error text-on-error-container rounded-xl flex-[2] flex flex-col items-center justify-center text-center shadow-lg p-4">
            <span className="material-symbols-outlined text-[64px] mb-2 animate-pulse">warning</span>
            <h2 className="text-xl font-black mb-2 uppercase">Time To Take Medication</h2>
            <div className="text-6xl font-black font-mono tracking-widest animate-pulse">
               {formatCountdown(status?.dispense_countdown_seconds)}
            </div>
         </div>
         <button 
          onClick={handleMedicineTaken}
          className="w-full rounded-xl flex flex-row items-center justify-center shadow-lg transition-all p-4 flex-[1] group border-4 bg-tertiary-container text-on-tertiary-container border-tertiary hover:brightness-110 active:scale-95"
         >
          <span className="material-symbols-outlined text-[48px] mr-4 group-active:scale-90 transition-transform">touch_app</span>
          <span className="text-2xl font-black tracking-wider">DISPENSE NOW</span>
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex-grow w-full h-full overflow-hidden">
      {isDispensing 
        ? renderDispenseView() 
        : (showDecagonView ? renderDecagonView() : renderScheduleView())
      }
      
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
