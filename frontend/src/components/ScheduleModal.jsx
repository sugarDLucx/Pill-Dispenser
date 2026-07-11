import React, { useState, useEffect } from 'react';
import { updateSchedule } from '../api';

const ScheduleModal = ({ slotId, initialData, onClose, onSave }) => {
  const [medicineName, setMedicineName] = useState('');
  const [frequency, setFrequency] = useState('daily');
  const [timeSlots, setTimeSlots] = useState([]);

  useEffect(() => {
    if (initialData) {
      setMedicineName(initialData.medicine_name || '');
      setFrequency(initialData.frequency || 'daily');
      if (initialData.time_slots) {
        setTimeSlots(initialData.time_slots.split(','));
      }
    }
  }, [initialData]);

  const handleAddTime = () => {
    // Add a default time, in a real app this would open a time picker
    setTimeSlots([...timeSlots, '08:00']);
  };

  const handleRemoveTime = (index) => {
    const newTimes = [...timeSlots];
    newTimes.splice(index, 1);
    setTimeSlots(newTimes);
  };

  const handleSave = async () => {
    const today = new Date().toISOString().split('T')[0];
    // Defaulting end_date to 1 year from now for simplicity
    const nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);
    const endDate = nextYear.toISOString().split('T')[0];

    const data = {
      compartment_id: slotId,
      medicine_name: medicineName,
      frequency: frequency,
      time_slots: timeSlots.join(','),
      start_date: today,
      end_date: endDate
    };
    
    await updateSchedule(data);
    onSave();
    onClose();
  };

  return (
    <>
      <div className="absolute inset-0 bg-on-background/60 z-40 backdrop-blur-sm" onClick={onClose}></div>
      <div 
        role="dialog" 
        className="absolute z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface-container-lowest rounded-xl shadow-[0_24px_48px_-12px_rgba(0,0,0,0.25)] w-full max-w-[800px] flex flex-col max-h-[90vh] overflow-hidden"
      >
        <div className="bg-surface-container flex items-center justify-between px-gutter py-stack-gap border-b-2 border-surface-variant">
          <h2 className="font-headline-lg text-headline-lg text-on-surface m-0 flex items-center gap-unit">
            <span className="material-symbols-outlined text-[40px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>calendar_month</span>
            Schedule Medication - Slot {slotId}
          </h2>
          <button onClick={onClose} aria-label="Close modal" className="h-touch-target-min w-touch-target-min flex items-center justify-center rounded-full hover:bg-surface-container-highest transition-colors focus:outline-none focus:ring-4 focus:ring-primary/50">
            <span className="material-symbols-outlined text-[32px] text-on-surface-variant">close</span>
          </button>
        </div>

        <div className="overflow-y-auto p-gutter flex flex-col gap-stack-gap">
          <div className="flex flex-col gap-unit">
            <label className="font-label-lg text-label-lg text-on-surface" htmlFor="medName">Medicine Name</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant text-[32px]">pill</span>
              <input 
                id="medName" 
                type="text" 
                placeholder="e.g., Metformin" 
                value={medicineName}
                onChange={(e) => setMedicineName(e.target.value)}
                className="w-full h-[80px] pl-16 pr-4 rounded-lg border-2 border-outline-variant bg-surface-container-lowest font-body-lg text-body-lg text-on-surface focus:border-primary focus:ring-4 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/50" 
              />
            </div>
          </div>

          <div className="flex flex-col gap-unit">
            <label className="font-label-lg text-label-lg text-on-surface" htmlFor="freqSelect">Frequency</label>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant text-[32px]">update</span>
              <select 
                id="freqSelect"
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                className="w-full h-[80px] pl-16 pr-12 rounded-lg border-2 border-outline-variant bg-surface-container-lowest font-body-lg text-body-lg text-on-surface appearance-none focus:border-primary focus:ring-4 focus:ring-primary/20 transition-all cursor-pointer"
              >
                <option value="daily">Daily</option>
                <option value="twice_daily">Twice Daily</option>
                <option value="weekly">Weekly</option>
              </select>
              <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-on-surface-variant text-[32px] pointer-events-none">arrow_drop_down</span>
            </div>
          </div>

          <div className="flex flex-col gap-unit mt-stack-gap">
            <label className="font-label-lg text-label-lg text-on-surface">Scheduled Times</label>
            
            {timeSlots.map((time, index) => (
              <div key={index} className="bg-surface flex items-center justify-between p-4 rounded-lg border-2 border-surface-variant mt-2">
                <div className="flex items-center gap-unit">
                  <span className="material-symbols-outlined text-[32px] text-secondary">schedule</span>
                  {/* Using a time input for editing */}
                  <input 
                    type="time" 
                    value={time} 
                    onChange={(e) => {
                      const newTimes = [...timeSlots];
                      newTimes[index] = e.target.value;
                      setTimeSlots(newTimes);
                    }}
                    className="font-headline-md text-headline-md text-on-surface bg-transparent border-none focus:ring-0"
                  />
                </div>
                <button onClick={() => handleRemoveTime(index)} aria-label="Remove time" className="h-[64px] w-[64px] flex items-center justify-center rounded-lg border-2 border-error text-error hover:bg-error-container focus:outline-none focus:ring-4 focus:ring-error/50 transition-colors">
                  <span className="material-symbols-outlined text-[28px]">delete</span>
                </button>
              </div>
            ))}

            <button onClick={handleAddTime} className="w-full min-h-[80px] flex items-center justify-center gap-unit rounded-lg border-4 border-dashed border-primary/50 text-primary hover:bg-primary/5 focus:outline-none focus:ring-4 focus:ring-primary/20 transition-all mt-unit shadow-sm bg-surface-container-lowest">
              <span className="material-symbols-outlined text-[36px]" style={{ fontVariationSettings: "'FILL' 1" }}>add_circle</span>
              <span className="font-headline-md text-headline-md m-0">+ Add Time</span>
            </button>
          </div>
        </div>

        <div className="bg-surface-container flex flex-col md:flex-row justify-end gap-stack-gap p-gutter border-t-2 border-surface-variant mt-auto">
          <button onClick={onClose} className="min-h-touch-target-min px-8 rounded-lg font-headline-md text-headline-md text-on-surface bg-surface-variant hover:bg-surface-dim focus:outline-none focus:ring-4 focus:ring-on-surface/20 transition-all w-full md:w-auto flex-1 md:flex-none">
            Cancel
          </button>
          <button onClick={handleSave} className="min-h-touch-target-min px-8 rounded-lg font-headline-md text-headline-md text-on-primary bg-primary hover:bg-on-primary-container focus:outline-none focus:ring-4 focus:ring-primary/50 transition-all shadow-md w-full md:w-auto flex-[2] md:flex-none flex items-center justify-center gap-unit">
            <span className="material-symbols-outlined text-[28px]" style={{ fontVariationSettings: "'FILL' 1" }}>save</span>
            Save Schedule
          </button>
        </div>
      </div>
    </>
  );
};

export default ScheduleModal;
