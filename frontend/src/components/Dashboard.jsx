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
    <div className="flex-grow flex flex-col md:flex-row px-margin-page py-gutter gap-margin-page overflow-hidden">
      
      {/* Left Pane (60%): Interactive Dispenser View */}
      <section className="w-full md:w-[60%] flex flex-col items-center justify-center bg-surface-container-lowest rounded-xl border-2 border-surface-variant relative shadow-lg p-8">
        
        {/* Legend Button */}
        <div className="absolute top-4 left-4 z-10">
          <button 
            onClick={() => setShowLegend(!showLegend)}
            className="flex items-center gap-2 bg-surface-container px-4 py-2 rounded-full border-2 border-surface-variant hover:bg-surface-variant transition-colors"
          >
            <span className="material-symbols-outlined text-[24px] text-on-surface-variant">help</span>
            <span className="font-label-lg text-on-surface">Legend</span>
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

        <Decagon schedules={schedules} activeSlot={activeSlot} onSlotClick={handleSlotClick} />
        
        <div className="mt-12 text-center">
          <h2 className="font-headline-lg text-headline-lg text-on-background mb-2">Dispenser Ready</h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant">Please take the medication from the highlighted yellow slot when active.</p>
        </div>
      </section>

      {/* Right Pane (40%): Action Area */}
      <section className="w-full md:w-[40%] flex flex-col gap-margin-page">
        
        {/* Next Dose Info Panel */}
        <div className="bg-surface-container-lowest rounded-xl border-2 border-surface-variant p-8 flex flex-col items-center justify-center text-center shadow-lg">
          <span className="material-symbols-outlined text-primary text-[64px] mb-4">info</span>
          <h2 className="font-display-lg text-display-lg text-on-background mb-4">Next Dose:</h2>
          <div className="font-display-lg text-display-lg text-primary font-bold mb-4">
            {status?.next_dose_time || "None"}
          </div>
          <div className="font-headline-lg text-headline-lg text-on-surface-variant bg-surface-container px-6 py-4 rounded-lg inline-block">
            {status?.next_dose_med || "No medication scheduled"}
          </div>
        </div>

        {/* Primary Action Button */}
        <button 
          onClick={handleMedicineTaken}
          className="w-full h-auto min-h-[140px] bg-primary-container text-on-primary-container rounded-xl flex flex-col items-center justify-center shadow-lg transition-all active:bg-primary hover:brightness-105 group border-2 border-primary"
        >
          <span className="material-symbols-outlined text-[64px] mb-2 group-active:scale-90 transition-transform">check_circle</span>
          <span className="font-display-lg text-display-lg font-bold">MEDICINE TAKEN</span>
        </button>
        
        {/* Secondary Action/Status */}
        <div className="flex-grow flex items-end justify-center pb-4">
          <div className="flex items-center gap-4 bg-surface-container-low px-6 py-4 rounded-full border-2 border-surface-variant shadow-sm">
            <span className="material-symbols-outlined text-on-surface-variant text-[32px]">schedule</span>
            <span className="font-body-lg text-body-lg text-on-surface-variant">System Active</span>
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
