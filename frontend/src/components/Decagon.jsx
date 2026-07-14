import React from 'react';

const Decagon = ({ schedules, activeSlot, onSlotClick }) => {
  // 10 points for the decagon centered at 200,200 with radius 180 (for 400x400 viewBox)
  // To match the original SVG exactly, we can use the same path coordinates or calculate them dynamically.
  // Based on the provided code.html:
  // Points: (200,20), (305.8,54.4), (371.2,144.4), (371.2,255.6), (305.8,345.6), (200,380), (94.2,345.6), (28.8,255.6), (28.8,144.4), (94.2,54.4)
  const wedges = [
    { id: 1, path: "M 200 200 L 200 20 L 305.8 54.4 Z" },
    { id: 2, path: "M 200 200 L 305.8 54.4 L 371.2 144.4 Z" },
    { id: 3, path: "M 200 200 L 371.2 144.4 L 371.2 255.6 Z" },
    { id: 4, path: "M 200 200 L 371.2 255.6 L 305.8 345.6 Z" },
    { id: 5, path: "M 200 200 L 305.8 345.6 L 200 380 Z" },
    { id: 6, path: "M 200 200 L 200 380 L 94.2 345.6 Z" },
    { id: 7, path: "M 200 200 L 94.2 345.6 L 28.8 255.6 Z" },
    { id: 8, path: "M 200 200 L 28.8 255.6 L 28.8 144.4 Z" },
    { id: 9, path: "M 200 200 L 28.8 144.4 L 94.2 54.4 Z" },
    { id: 10, path: "M 200 200 L 94.2 54.4 L 200 20 Z" }
  ];

  const formatTime12hr = (timeStr) => {
    if (!timeStr) return '';
    const [h, m] = timeStr.split(':');
    let hour = parseInt(h, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    hour = hour % 12;
    hour = hour || 12; // 0 becomes 12
    return `${hour}:${m} ${ampm}`;
  };

  const getSlotStyle = (id) => {
    if (activeSlot === id) {
      return "fill-tertiary-fixed stroke-tertiary-fixed-dim stroke-2 cursor-pointer hover:brightness-110 animate-pulse";
    }
    const isScheduled = schedules.some(s => s.compartment_id === id);
    if (isScheduled) {
      return "fill-secondary-fixed stroke-secondary-fixed-dim stroke-2 cursor-pointer hover:brightness-105";
    }
    return "fill-surface-container stroke-surface-dim stroke-2 cursor-pointer hover:brightness-95";
  };

  const getCenterText = () => {
    if (activeSlot) return `Slot ${activeSlot}`;
    return "Ready";
  };

  return (
    <div className="relative w-[400px] h-[400px] flex items-center justify-center">
      <svg viewBox="0 0 400 400" className="w-full h-full drop-shadow-lg">
        <defs>
          <filter id="inner-shadow">
            <feOffset dx="0" dy="2" />
            <feGaussianBlur stdDeviation="2" result="offset-blur" />
            <feComposite operator="out" in="SourceGraphic" in2="offset-blur" result="inverse" />
            <feFlood floodColor="black" floodOpacity="0.2" result="color" />
            <feComposite operator="in" in="color" in2="inverse" result="shadow" />
            <feComposite operator="over" in="shadow" in2="SourceGraphic" />
          </filter>
        </defs>
        
        {wedges.map((wedge) => {
          const schedule = schedules.find(s => s.compartment_id === wedge.id);
          const angleDeg = -90 + 18 + (wedge.id - 1) * 36;
          const angleRad = angleDeg * Math.PI / 180;
          const r = 140; 
          const pos = {
            x: 200 + r * Math.cos(angleRad),
            y: 200 + r * Math.sin(angleRad)
          };
          
          return (
            <g key={wedge.id} className="cursor-pointer" onClick={() => onSlotClick(wedge.id)}>
              <path 
                d={wedge.path} 
                className={`transition-all ${getSlotStyle(wedge.id)} pointer-events-none`}
              />
              {schedule ? (
                <>
                  <text x={pos.x} y={pos.y - 10} textAnchor="middle" fontSize="11" fontWeight="bold" fill="#1c1b1b" className="pointer-events-none">{schedule.medicine_name.length > 10 ? schedule.medicine_name.substring(0,8)+'...' : schedule.medicine_name}</text>
                  <text x={pos.x} y={pos.y + 2} textAnchor="middle" fontSize="9" fill="#3d4a3d" className="pointer-events-none">{schedule.frequency === 'twice_daily' ? '2x Daily' : schedule.frequency.charAt(0).toUpperCase() + schedule.frequency.slice(1)}</text>
                  <text x={pos.x} y={pos.y + 14} textAnchor="middle" fontSize="9" fill="#3d4a3d" className="pointer-events-none">{formatTime12hr(schedule.time_slots.split(',')[0])}</text>
                </>
              ) : (
                <text x={pos.x} y={pos.y + 4} textAnchor="middle" fontSize="12" fill="#6d7b6c" className="pointer-events-none">Empty</text>
              )}
            </g>
          );
        })}

        <circle cx="200" cy="200" r="80" className="fill-surface stroke-surface-container-high stroke-[4px] pointer-events-none" filter="url(#inner-shadow)" />
      </svg>
      
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <span className="font-headline-md text-headline-md text-on-surface">{getCenterText()}</span>
        {activeSlot && <span className="font-label-lg text-label-lg text-on-surface-variant">Active</span>}
      </div>
    </div>
  );
};

export default Decagon;
