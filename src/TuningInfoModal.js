import React from 'react';
import ReactDOM from 'react-dom';
import './TuningInfoModal.css';

const TuningInfoModal = ({ mappedNotes, midiToPianoKeys, getKeyboardLabel, midiToFrequency, onClose, buttonRef }) => {
  const [modalStyle, setModalStyle] = React.useState({});

  const updatePosition = () => {
    if (buttonRef?.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      
      // Calculate if modal would overflow right side of viewport
      const modalWidth = 400; // width of modal
      const rightEdge = rect.right;
      const wouldOverflowRight = rightEdge + modalWidth > viewportWidth;
      
      setModalStyle({
        position: 'fixed',
        top: `${rect.bottom + 10}px`,
        left: wouldOverflowRight 
          ? `${viewportWidth - modalWidth - 20}px` 
          : `${rect.left}px`,
      });
    }
  };

  React.useEffect(() => {
    updatePosition();
    
    window.addEventListener('scroll', updatePosition);
    window.addEventListener('resize', updatePosition);
    
    return () => {
      window.removeEventListener('scroll', updatePosition);
      window.removeEventListener('resize', updatePosition);
    };
  }, [buttonRef]);

  // Helper function to adjust the octave number down by 1
  const adjustOctave = (noteStr) => {
    const match = noteStr.match(/([A-G]#?)(\d)/);
    if (match) {
      const [_, note, octave] = match;
      return `${note}${parseInt(octave) - 1}`;
    }
    return noteStr;
  };

  return ReactDOM.createPortal(
    <div className="modal-overlay">
      <div className="modal-content tuning-modal" style={modalStyle} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Keyboard Tuning Details</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body tuning-info">
          <div className="peak-list">
            {Array.from(mappedNotes.entries())
              .sort(([midi1], [midi2]) => midi1 - midi2)
              .filter(([_, note]) => note.isMapped)
              .map(([midi, note]) => {
                const label = adjustOctave(midiToPianoKeys[midi]);
                const keyLabel = getKeyboardLabel(midi);
                return (
                  <div key={midi} className="peak-item">
                    <div className="peak-item-header">
                      Key '{keyLabel}' ({label})
                      {note.isDirectPeakMatch && (
                        <span className="peak-match-indicator">• Peak Match</span>
                      )}
                    </div>
                    <div className="peak-item-details">
                      <div className="tuning-row">
                        <span className="tuning-label">Western tuning:</span>
                        <span className="tuning-value">
                          {Math.round(midiToFrequency(midi))}Hz ({Math.round(note.westernCents)}¢)
                        </span>
                      </div>
                      <div className="tuning-row">
                        <span className="tuning-label">Makam tuning:</span>
                        <span className="tuning-value">
                          {Math.round(note.mappedHz)}Hz ({Math.round(note.mappedCents)}¢)
                        </span>
                      </div>
                      <div className="tuning-row">
                        <span className="tuning-label">Adjustment:</span>
                        <span className={`tuning-value ${note.centDiff > 15 ? 'sharp' : note.centDiff < -15 ? 'flat' : ''}`}>
                          {note.centDiff > 0 ? '+' : ''}{Math.round(note.centDiff)}¢
                          {Math.abs(note.centDiff) > 15 ? 
                            ` (${note.centDiff > 0 ? 'sharp' : 'flat'})` : 
                            ' (in tune)'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default TuningInfoModal; 