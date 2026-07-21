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

  // Simulate active slot based on status
  // In a real app, backend status might return the active slot ID directly.
  const activeSlot = null; // Placeholder for now

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
    const poll = setInterval(loadData, 5000);
    return () => clearInterval(poll);
  }, []);

  const handleMedicineTaken = async () => {
    await markMedicineTaken();
    alert("Medicine marked as taken.");
  };

  const handleSlotClick = (id) => {
    setModalSlot(id);
  };

  return (
    <div className="flex-grow flex flex-row p-2 gap-2 overflow-hidden">
      
      {/* Left Pane (60%): Interactive Dispenser View */}
      <section className="w-[60%] h-full flex flex-col items-center justify-center bg-surface-container-lowest rounded-xl border-2 border-surface-variant relative shadow-sm p-2">
        
        {/* Legend Button */}
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

        <div className="flex-grow flex items-center justify-center w-full max-h-[85%]">
          <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
        </div>
      </section>

      {/* Right Pane (40%): Action Area */}
      <section className="w-[40%] h-full flex flex-col gap-2">
        
        {/* Next Dose Info Panel */}
        <div className="bg-surface-container-lowest rounded-xl border-2 border-surface-variant p-2 flex flex-col items-center justify-center text-center shadow-sm flex-[1]">
          <h2 className="text-sm font-bold text-on-background mb-1">Next Dose:</h2>
          <div className="text-xl text-primary font-bold mb-1 line-clamp-1">
            {status?.next_dose_time || "None"}
          </div>
          <div className="text-xs text-on-surface-variant bg-surface-container px-2 py-1 rounded inline-block line-clamp-2">
            {status?.next_dose_med || "No medication scheduled"}
          </div>
        </div>

        {/* Primary Action Button */}
        <button 
          onClick={handleMedicineTaken}
          className="w-full bg-primary-container text-on-primary-container rounded-xl flex flex-col items-center justify-center shadow-sm active:bg-primary transition-all p-2 flex-[1] group border-2 border-primary"
        >
          <span className="material-symbols-outlined text-[40px] mb-1 group-active:scale-90 transition-transform">check_circle</span>
          <span className="text-sm font-bold">MEDICINE TAKEN</span>
        </button>
        
        {/* Secondary Action/Status */}
        <div className="flex items-center justify-center h-8">
          <div className="flex items-center gap-2 bg-surface-container-low px-3 py-1 rounded-full border border-surface-variant shadow-sm">
            <span className="material-symbols-outlined text-on-surface-variant text-[16px]">schedule</span>
            <span className="text-xs text-on-surface-variant">System Active</span>
          </div>
        </div>

      </section>

      {modalSlot !== null && (
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
