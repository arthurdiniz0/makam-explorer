import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import PianoVisualizer from './PianoVisualizer';
import MakamInfoModal from './MakamInfoModal';
import PitchHistogram from './PitchHistogram';
import './PitchHistogram.css';

function App() {
  const audioRef = useRef(null);
  const [pitchData, setPitchData] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [makams, setMakams] = useState([]);
  const [selectedMakam, setSelectedMakam] = useState('');
  const [recordings, setRecordings] = useState([]);
  const [selectedRecording, setSelectedRecording] = useState('');
  const [pitchMethods, setPitchMethods] = useState([]);
  const [selectedPitchMethod, setSelectedPitchMethod] = useState('');
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [showMakamInfo, setShowMakamInfo] = useState(false);

  const infoButtonRef = useRef(null);

  // List of recordings that have pickle files
  const availableRecordings = [
    { cd: "CD 1", title: "17. Gazelle du désert", mode: "rast" },
    { cd: "CD 1", title: "18. Il apparut et, dans sa main", mode: "rast" },
    { cd: "CD 2", title: "11. Si léchanson", mode: "husayni" },
    { cd: "CD 2", title: "12. Dis à celui dont tout le monde aime les vertus", mode: "husayni" },
    { cd: "CD 11", title: "02. Suite", mode: "rast" },
    { cd: "CD 11", title: "03. Suite", mode: "rast" },
    { cd: "CD 13", title: "05. Ensemble of Muhammad al-Qubbânjî and Azzûrî al-Awwâd - Cest comme si midi était la nuit", mode: "husayni" },
    { cd: "CD 13", title: "07. Ensemble of Muhammad al-Qubbânjî and Azzûrî al-Awwâd - Suite", mode: "husayni" }
  ];

  // Map of pitch method names to display names
  const pitchMethodNames = {
    'pitch_pyin': 'pYIN',
    'pitch_makam': 'Makam',
    'pitch_crepe': 'CREPE'
  };

  useEffect(() => {
    // Get unique makams from available recordings
    const uniqueMakams = [...new Set(availableRecordings.map(rec => rec.mode))];
    console.log('Available makams:', uniqueMakams);
    setMakams(uniqueMakams);
  }, []);

  useEffect(() => {
    if (selectedMakam) {
      // Filter recordings by selected makam
      const filteredRecordings = availableRecordings.filter(rec => rec.mode === selectedMakam);
      console.log('Filtered recordings for makam', selectedMakam, ':', filteredRecordings);
      setRecordings(filteredRecordings);
      setSelectedRecording('');
      setSelectedPitchMethod('');
    } else {
      setRecordings([]);
      setSelectedRecording('');
      setSelectedPitchMethod('');
    }
  }, [selectedMakam]);

  useEffect(() => {
    if (selectedRecording) {
      const recording = availableRecordings.find(rec => 
        rec.cd + '/' + rec.title === selectedRecording
      );
      
      if (recording) {
        console.log('Loading data for recording:', recording);
        // Set audio URL
        setAudioUrl(`/subsetRecordings/${recording.cd}/${recording.title}.mp3`);
        
        // Load pitch data from JSON file
        fetch(`/subsetRecordings/${recording.cd}/${recording.title}.json`)
          .then(response => response.json())
          .then(data => {
            // Get available pitch methods
            const methods = Object.keys(data).filter(key => key.startsWith('pitch_'));
            console.log('Available pitch methods:', methods);
            setPitchMethods(methods);
            
            // Select first method by default
            if (methods.length > 0) {
              const firstMethod = methods[0];
              setSelectedPitchMethod(firstMethod);
              
              // Transform the pitch data
              const formattedPitchData = data[firstMethod].map(([time, frequency]) => ({
                time,
                frequency
              }));

              // Store pitch data and histogram data
              setPitchData({
                pitchPoints: formattedPitchData,
                pitch_hist_values: data.pitch_hist_values,
                pitch_hist_edges: data.pitch_hist_edges,
                pitch_hist_values_mean: data.pitch_hist_values_mean,
                pitch_hist_values_pyin: data.pitch_hist_values_pyin || data.pitch_hist_values,
                pitch_hist_values_crepe: data.pitch_hist_values_crepe,
                pitch_hist_values_makam: data.pitch_hist_values_makam,
                maxima_locs_cent: data.maxima_locs_cent
              });

              console.log('Setting pitch data with histogram values:', {
                pyin: data.pitch_hist_values_pyin?.length || data.pitch_hist_values?.length,
                crepe: data.pitch_hist_values_crepe?.length,
                makam: data.pitch_hist_values_makam?.length,
                mean: data.pitch_hist_values_mean?.length
              });
            }
          })
          .catch(error => {
            console.error('Error loading data:', error);
            setPitchData(null);
            setPitchMethods([]);
            setSelectedPitchMethod('');
          });
      }
    } else {
      setAudioUrl(null);
      setPitchData(null);
      setPitchMethods([]);
      setSelectedPitchMethod('');
    }
  }, [selectedRecording]);

  useEffect(() => {
    if (selectedRecording && selectedPitchMethod) {
      const recording = availableRecordings.find(rec => 
        rec.cd + '/' + rec.title === selectedRecording
      );
      
      if (recording) {
        // Load JSON data
        fetch(`/subsetRecordings/${recording.cd}/${recording.title}.json`)
          .then(response => response.json())
          .then(data => {
            console.log('Loaded data:', data);
            console.log('Maxima locations from JSON:', data.maxima_locs_cent);
            
            // Transform the pitch data
            const formattedPitchData = data[selectedPitchMethod].map(([time, frequency]) => ({
              time,
              frequency
            }));

            // Log the data we're about to set
            console.log('Setting pitch data:', {
              pitchPoints: formattedPitchData.slice(0, 2),
              maxima_locs_cent: data.maxima_locs_cent
            });

            // Store pitch data and histogram data
            setPitchData({
              pitchPoints: formattedPitchData,
              pitch_hist_values: data.pitch_hist_values,
              pitch_hist_edges: data.pitch_hist_edges,
              pitch_hist_values_mean: data.pitch_hist_values_mean,
              pitch_hist_values_pyin: data.pitch_hist_values_pyin || data.pitch_hist_values,
              pitch_hist_values_crepe: data.pitch_hist_values_crepe,
              pitch_hist_values_makam: data.pitch_hist_values_makam,
              maxima_locs_cent: data.maxima_locs_cent
            });

            console.log('Setting pitch data with histogram values:', {
              pyin: data.pitch_hist_values_pyin?.length || data.pitch_hist_values?.length,
              crepe: data.pitch_hist_values_crepe?.length,
              makam: data.pitch_hist_values_makam?.length,
              mean: data.pitch_hist_values_mean?.length
            });
          })
          .catch(error => {
            console.error('Error loading data:', error);
            setPitchData(null);
          });
      }
    }
  }, [selectedPitchMethod]);

  // Effect to update audio playback rate when speed changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  const handleMakamChange = (event) => {
    setSelectedMakam(event.target.value);
  };

  const handleRecordingChange = (event) => {
    setSelectedRecording(event.target.value);
  };

  const handlePitchMethodChange = (event) => {
    setSelectedPitchMethod(event.target.value);
  };

  const handleSpeedChange = (event) => {
    setPlaybackSpeed(parseFloat(event.target.value));
  };

  return (
    <div className="App">
      <div className="controls">
        <div className="select-group">
          <div className="select-container">
            <label htmlFor="makam-select">Select Makam:</label>
            <select
              id="makam-select"
              value={selectedMakam}
              onChange={handleMakamChange}
            >
              <option value="">Select a makam</option>
              {makams.map(makam => (
                <option key={makam} value={makam}>
                  {makam}
                </option>
              ))}
            </select>
          </div>

          <div className="select-container">
            <label htmlFor="recording-select">Select Recording:</label>
            <select
              id="recording-select"
              value={selectedRecording}
              onChange={handleRecordingChange}
              disabled={!selectedMakam}
            >
              <option value="">Select a recording</option>
              {recordings.map(recording => (
                <option 
                  key={recording.cd + '/' + recording.title} 
                  value={recording.cd + '/' + recording.title}
                >
                  {recording.title}
                </option>
              ))}
            </select>
          </div>

          {selectedMakam && (
            <button 
              ref={infoButtonRef}
              onClick={() => setShowMakamInfo(true)}
              className="info-button"
            >
              About {selectedMakam.charAt(0).toUpperCase() + selectedMakam.slice(1)} Makam
            </button>
          )}
        </div>
      </div>

      {audioUrl && pitchData?.pitchPoints && Array.isArray(pitchData.pitchPoints) && (
        <div className="visualization">
          <div className="visualization-controls">
            <div className="controls-row">
              <audio ref={audioRef} controls src={audioUrl} />
            </div>
            <div className="controls-row controls-row-split">
              <div className="speed-control">
                <label htmlFor="speed-control">Playback speed</label>
                <div className="speed-control-input">
                  <input
                    type="range"
                    id="speed-control"
                    min="0.25"
                    max="2"
                    step="0.25"
                    value={playbackSpeed}
                    onChange={handleSpeedChange}
                  />
                  <span className="speed-value">{playbackSpeed}x</span>
                </div>
              </div>
              <div className="select-container pitch-method-select">
                <label htmlFor="pitch-method-select">Pitch extraction method</label>
                <select
                  id="pitch-method-select"
                  value={selectedPitchMethod}
                  onChange={handlePitchMethodChange}
                  disabled={!selectedRecording || pitchMethods.length === 0}
                >
                  <option value="">Select method</option>
                  {pitchMethods.map(method => (
                    <option key={method} value={method}>
                      {pitchMethodNames[method] || method}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          <div className="visualization-content">
            <PianoVisualizer 
              pitchData={{
                pitchPoints: pitchData.pitchPoints,
                pitch_hist_values: pitchData.pitch_hist_values,
                pitch_hist_edges: pitchData.pitch_hist_edges,
                pitch_hist_values_mean: pitchData.pitch_hist_values_mean,
                maxima_locs_cent: pitchData.maxima_locs_cent
              }}
              audioRef={audioRef} 
              playbackSpeed={playbackSpeed}
              maximaLocsCent={pitchData.maxima_locs_cent}
            />
            <div className="histogram-container">
              <PitchHistogram pitchData={pitchData} />
            </div>
          </div>
        </div>
      )}

      {showMakamInfo && (
        <MakamInfoModal
          makam={selectedMakam}
          onClose={() => setShowMakamInfo(false)}
          buttonRef={infoButtonRef}
        />
      )}
    </div>
  );
}

export default App;
