import React from 'react';
import instrumentManager from '../InstrumentManager';

const InstrumentSelector = () => {
    const [currentInstrument, setCurrentInstrument] = React.useState('flute');
    const [isChanging, setIsChanging] = React.useState(false);

    const handleChange = async (event) => {
        const newInstrument = event.target.value;
        setIsChanging(true);
        try {
            await instrumentManager.changeInstrument(newInstrument);
            setCurrentInstrument(newInstrument);
        } catch (error) {
            console.error('Failed to change instrument:', error);
        } finally {
            setIsChanging(false);
        }
    };

    return (
        <div className="instrument-selector">
            <label htmlFor="instrument-select">Instrument:</label>
            <select 
                id="instrument-select"
                value={currentInstrument}
                onChange={handleChange}
                disabled={isChanging}
                className="instrument-select"
            >
                <option value="flute">Flute</option>
                <option value="guitar-acoustic">Guitar</option>
            </select>
            {isChanging && <span className="loading-text">Loading instrument...</span>}
            
            <style jsx>{`
                .instrument-selector {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                }
                
                label {
                    color: rgba(255, 255, 255, 0.8);
                    font-size: 0.9rem;
                    font-weight: 500;
                    white-space: nowrap;
                }
                
                .instrument-select {
                    padding: 0.5rem;
                    border-radius: 4px;
                    border: 1px solid #ccc;
                    background-color: white;
                    font-size: 1rem;
                    min-width: 200px;
                }
                
                .loading-text {
                    color: #666;
                    font-size: 0.9rem;
                    font-style: italic;
                }
            `}</style>
        </div>
    );
};

export default InstrumentSelector; 