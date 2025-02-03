import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import './MakamInfoModal.css';

const makamUrls = {
  rast: 'https://www.maqamworld.com/en/maqam/rast.php',
  husayni: 'https://www.maqamworld.com/en/maqam/husayni.php'
};

const MakamInfoModal = ({ makam, onClose, buttonRef }) => {
  const [modalStyle, setModalStyle] = useState({});
  const [isLoading, setIsLoading] = useState(true);

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

  useEffect(() => {
    updatePosition();
    
    window.addEventListener('scroll', updatePosition);
    window.addEventListener('resize', updatePosition);
    
    return () => {
      window.removeEventListener('scroll', updatePosition);
      window.removeEventListener('resize', updatePosition);
    };
  }, [buttonRef]);

  if (!makam) return null;

  return ReactDOM.createPortal(
    <div className="modal-overlay">
      <div className="modal-content" style={modalStyle} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>About {makam.charAt(0).toUpperCase() + makam.slice(1)} Makam</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {isLoading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading...</p>
            </div>
          )}
          <iframe
            src={makamUrls[makam]}
            title={`About ${makam} makam`}
            width="100%"
            height="100%"
            frameBorder="0"
            onLoad={() => setIsLoading(false)}
            style={{ opacity: isLoading ? 0 : 1 }}
          />
        </div>
      </div>
    </div>,
    document.body
  );
};

export default MakamInfoModal; 