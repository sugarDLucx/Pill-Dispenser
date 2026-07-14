import React, { useState, useEffect, useRef } from 'react';

// A single scrollable column (for hours, minutes, or AM/PM)
const ScrollColumn = ({ items, value, onChange, label }) => {
  const containerRef = useRef(null);
  const itemHeight = 60; // 60px height per item
  const [isScrolling, setIsScrolling] = useState(false);
  const scrollTimeout = useRef(null);

  useEffect(() => {
    const index = items.indexOf(value);
    if (containerRef.current && index !== -1) {
      containerRef.current.scrollTop = index * itemHeight;
    }
  }, []);

  const handleScroll = (e) => {
    setIsScrolling(true);
    clearTimeout(scrollTimeout.current);

    const top = e.target.scrollTop;
    const index = Math.round(top / itemHeight);
    
    // Once scrolling stops for 100ms, update the selected value
    scrollTimeout.current = setTimeout(() => {
      setIsScrolling(false);
      if (items[index] !== undefined && items[index] !== value) {
        onChange(items[index]);
      }
      // Snap to exact position to correct any slight off-by-pixel
      if (containerRef.current) {
        containerRef.current.scrollTo({
          top: index * itemHeight,
          behavior: 'smooth'
        });
      }
    }, 150);
  };

  return (
    <div className="flex flex-col items-center flex-1 relative h-full">
      <div className="font-label-lg text-label-lg text-on-surface-variant mb-2 absolute -top-8">{label}</div>
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="h-[180px] w-full overflow-y-auto snap-y snap-mandatory no-scrollbar relative z-10"
        style={{ scrollBehavior: isScrolling ? 'auto' : 'smooth' }}
      >
        <div style={{ height: '60px' }}></div> {/* Top padding */}
        {items.map((item) => {
          const isSelected = item === value;
          return (
            <div 
              key={item} 
              className={`h-[60px] flex items-center justify-center snap-center font-headline-lg text-3xl transition-all duration-200 select-none ${isSelected ? 'text-primary font-bold scale-110' : 'text-on-surface-variant/40 scale-90'}`}
            >
              {item}
            </div>
          );
        })}
        <div style={{ height: '60px' }}></div> {/* Bottom padding */}
      </div>
      
      {/* Center highlight bar */}
      <div className="absolute top-[60px] left-0 right-0 h-[60px] border-y-2 border-primary/30 bg-primary/5 pointer-events-none z-0 rounded-lg"></div>
    </div>
  );
};

const TouchTimePicker = ({ initialTime = '08:00', onSave, onClose }) => {
  // Parse initial 24h time into 12h format
  const [hour24, minuteStr] = initialTime.split(':');
  let h = parseInt(hour24, 10);
  const initialAmPm = h >= 12 ? 'PM' : 'AM';
  h = h % 12;
  h = h || 12;
  
  const [hour, setHour] = useState(h.toString().padStart(2, '0'));
  const [minute, setMinute] = useState(minuteStr);
  const [ampm, setAmpm] = useState(initialAmPm);

  // Generate options
  const hours = Array.from({ length: 12 }, (_, i) => (i + 1).toString().padStart(2, '0'));
  const minutes = Array.from({ length: 60 }, (_, i) => i.toString().padStart(2, '0'));
  const ampmOptions = ['AM', 'PM'];

  const handleConfirm = () => {
    let h24 = parseInt(hour, 10);
    if (ampm === 'PM' && h24 !== 12) h24 += 12;
    if (ampm === 'AM' && h24 === 12) h24 = 0;
    
    const time24 = `${h24.toString().padStart(2, '0')}:${minute}`;
    onSave(time24);
  };

  return (
    <div className="absolute inset-0 z-[60] flex items-center justify-center backdrop-blur-md bg-on-background/40">
      <div className="bg-surface-container-lowest p-8 rounded-3xl shadow-[0_32px_64px_-16px_rgba(0,0,0,0.4)] w-[90%] max-w-[400px] flex flex-col gap-8 animate-in fade-in zoom-in-95 duration-200">
        
        <div className="text-center">
          <h3 className="font-headline-md text-headline-md text-on-surface">Select Time</h3>
          <p className="font-body-md text-body-md text-on-surface-variant">Swipe up or down to set</p>
        </div>

        {/* Scroll Pickers */}
        <div className="flex items-center justify-between h-[180px] px-4 relative mt-4">
          <ScrollColumn items={hours} value={hour} onChange={setHour} label="Hour" />
          <div className="font-headline-lg text-3xl text-on-surface pb-[60px] mx-2 font-bold z-20">:</div>
          <ScrollColumn items={minutes} value={minute} onChange={setMinute} label="Minute" />
          <div className="w-4"></div> {/* Spacer */}
          <ScrollColumn items={ampmOptions} value={ampm} onChange={setAmpm} label="AM/PM" />
        </div>

        {/* Actions */}
        <div className="flex gap-4 mt-6">
          <button 
            onClick={onClose}
            className="flex-1 h-[64px] rounded-xl font-headline-md text-on-surface bg-surface-variant hover:bg-surface-dim active:scale-95 transition-all"
          >
            Cancel
          </button>
          <button 
            onClick={handleConfirm}
            className="flex-[2] h-[64px] rounded-xl font-headline-md text-on-primary bg-primary shadow-lg shadow-primary/30 hover:bg-on-primary-container active:scale-95 transition-all"
          >
            Confirm Time
          </button>
        </div>
      </div>
    </div>
  );
};

export default TouchTimePicker;
