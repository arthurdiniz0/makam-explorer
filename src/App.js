import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import './App.css';
import './theme.css'; // Import theme CSS
import { ThemeProvider } from './ThemeContext'; // Import ThemeProvider
import PianoVisualizer from './PianoVisualizer';
import MakamInfoModal from './MakamInfoModal';
import PitchHistogram from './PitchHistogram';
import MapPage from './MapPage';
import GeoMap from './GeoMap';
import CountryPage from './CountryPage';
import NavBar from './NavBar';
import './PitchHistogram.css';

// Country data with recording information 
const countryData = {
  egypt: {
    name: 'Egypt',
    id: 'egypt',
    svgId: 'EG'
  },
  iraq: {
    name: 'Iraq',
    id: 'iraq',
    svgId: 'IQ'
  },
  algeria: {
    name: 'Algeria',
    id: 'algeria',
    svgId: 'DZ'
  },
  morocco: {
    name: 'Morocco',
    id: 'maroc',
    svgId: 'MA'
  },
  tunisia: {
    name: 'Tunisia',
    id: 'tunisia',
    svgId: 'TN'
  },
  turkey: {
    name: 'Turkey',
    id: 'turkey',
    svgId: 'TR'
  },
  syria: {
    name: 'Syria',
    id: 'syria',
    svgId: 'SY'
  }
};

// Hardcoded data for the recordings we know exist
const availableRecordings = [
  {
    path: "CD 1/17. Gazelle du désert",
    title: "Gazelle du désert",
    mode: "rast",
    artist: "Ensemble Al-Kindi",
    region: "syria"
  },
  {
    path: "CD 1/18. Il apparut et, dans sa main",
    title: "Il apparut et, dans sa main",
    mode: "rast",
    artist: "Ensemble Al-Kindi",
    region: "syria"
  },
  {
    path: "CD 2/11. Si léchanson",
    title: "Si léchanson",
    mode: "husayni",
    artist: "Ensemble Al-Kindi",
    region: "egypt"
  },
  {
    path: "CD 2/12. Dis à celui dont tout le monde aime les vertus",
    title: "Dis à celui dont tout le monde aime les vertus",
    mode: "husayni",
    artist: "Ensemble Al-Kindi",
    region: "egypt"
  },
  {
    path: "CD 11/02. Suite",
    title: "Suite (CD 11/02)",
    mode: "rast",
    artist: "Ottoman Ensemble",
    region: "turkey"
  },
  {
    path: "CD 11/03. Suite",
    title: "Suite (CD 11/03)",
    mode: "rast", 
    artist: "Ottoman Ensemble",
    region: "turkey"
  },
  {
    path: "CD 13/05. Ensemble of Muhammad al-Qubbânjî and Azzûrî al-Awwâd - Cest comme si midi était la nuit",
    title: "Cest comme si midi était la nuit",
    mode: "husayni",
    artist: "Ensemble of Muhammad al-Qubbânjî and Azzûrî al-Awwâd",
    region: "iraq"
  },
  {
    path: "CD 13/07. Ensemble of Muhammad al-Qubbânjî and Azzûrî al-Awwâd - Suite",
    title: "Suite",
    mode: "husayni",
    artist: "Ensemble of Muhammad al-Qubbânjî and Azzûrî al-Awwâd",
    region: "iraq"
  }
];

// Wrap MainApp with useLocation
function MainAppWrapper() {
  const location = useLocation();
  return <MainApp location={location} />;
}

function MainApp({ location }) {
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

  // Map of pitch method names to display names
  const pitchMethodNames = {
    'pitch_pyin': 'pYIN',
    'pitch_makam': 'Makam',
    'pitch_crepe': 'CREPE'
  };

  // Check for recording from navigation state (from country page)
  useEffect(() => {
    if (location && location.state && location.state.selectedRecording) {
      const recordingPath = location.state.selectedRecording;
      
      // Find the recording in availableRecordings
      const recording = availableRecordings.find(rec => rec.path === recordingPath);
      
      if (recording) {
        // Set the makam first, which will populate the recordings dropdown
        setSelectedMakam(recording.mode);
        
        // Then set the selected recording after a small delay to ensure the recordings have been filtered
        setTimeout(() => {
          setSelectedRecording(recordingPath);
        }, 100);
      }
    }
  }, [location]);

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
        rec.path === selectedRecording
      );
      
      if (recording) {
        console.log('Loading data for recording:', recording);
        // Set audio URL
        setAudioUrl(`/subsetRecordings/${recording.path}.mp3`);
        
        // Load pitch data from JSON file
        fetch(`/subsetRecordings/${recording.path}.json`)
          .then(response => response.json())
          .then(data => {
            // Get available pitch methods - filter to only include the three main methods
            const allMethods = Object.keys(data).filter(key => key.startsWith('pitch_'));
            const validMethods = allMethods.filter(method => 
              ['pitch_pyin', 'pitch_crepe', 'pitch_makam'].includes(method)
            );
            console.log('Available pitch methods:', validMethods);
            setPitchMethods(validMethods);
            
            // Select first method by default
            if (validMethods.length > 0) {
              const firstMethod = validMethods[0];
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
        rec.path === selectedRecording
      );
      
      if (recording) {
        // Load JSON data
        fetch(`/subsetRecordings/${recording.path}.json`)
          .then(response => response.json())
          .then(data => {
            console.log('Loaded data:', data);
            console.log('Maxima locations from JSON:', data.maxima_locs_cent);
            
            // Check if selectedPitchMethod is valid
            if (!['pitch_pyin', 'pitch_crepe', 'pitch_makam'].includes(selectedPitchMethod)) {
              // If not valid, try to set a valid one
              const validMethods = Object.keys(data).filter(key => 
                ['pitch_pyin', 'pitch_crepe', 'pitch_makam'].includes(key)
              );
              if (validMethods.length > 0) {
                setSelectedPitchMethod(validMethods[0]);
                return; // will trigger this effect again with the valid method
              }
            }
            
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
      <div className="app-header">
        <h1>Makam Explorer</h1>
        <Link to="/map" className="map-link">Map Explorer</Link>
      </div>
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
                  key={recording.path} 
                  value={recording.path}
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
          <div className="visualization-content">
            <div className="player-controls-container">
              <audio ref={audioRef} controls src={audioUrl} className="audio-player" />
              <div className="playback-controls">
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

function MapPageWrapper() {
  return (
    <div className="map-page-wrapper">
      <h1>Makam Explorer - Geography</h1>
      <p>Explore musical traditions by region. Click on a country to discover recordings from that region.</p>
      <GeoMap availableRecordings={availableRecordings} />
    </div>
  );
}

function CountryPageWrapper() {
  const navigate = useNavigate();
  const [selectedRecording, setSelectedRecording] = useState(null);
  
  const handleRecordingSelect = (recording) => {
    setSelectedRecording(recording);
  };
  
  return (
    <CountryPage 
      availableRecordings={availableRecordings} 
      onSelectRecording={handleRecordingSelect}
    />
  );
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="app-container">
          <NavBar />
          <div className="app-content">
            <Routes>
              <Route path="/" element={<MainAppWrapper />} />
              <Route path="/map" element={<MapPageWrapper />} />
              <Route path="/country/:countryId" element={<CountryPageWrapper />} />
            </Routes>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
