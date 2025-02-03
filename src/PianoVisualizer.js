import React, {
    useRef,
    useState,
    useEffect,
    useLayoutEffect,
    useCallback,
  } from "react";
  import "./PianoVisualizer.css";
  
  // ----------------------
  // MIDI -> Label (C2=36 ~ D4=62). Adjust as you like.
  // ----------------------
  const midiToPianoKeys = {
    36: "C2",
    37: "C#2",
    38: "D2",
    39: "D#2",
    40: "E2",
    41: "F2",
    42: "F#2",
    43: "G2",
    44: "G#2",
    45: "A2",
    46: "A#2",
    47: "B2",
    48: "C3",
    49: "C#3",
    50: "D3",
    51: "D#3",
    52: "E3",
    53: "F3",
    54: "F#3",
    55: "G3",
    56: "G#3",
    57: "A3",
    58: "A#3",
    59: "B3",
    60: "C4",
    61: "C#4",
    62: "D4",
  };
  
  // ----------------------
  // AUDIO: Oscillators, One Octave Up
  // ----------------------
  
  let audioContext = null;
  const activeOscillators = {}; // e.g. { midiNote: { osc, gain }, ... }
  
  /** Create or reuse a single AudioContext */
  function getAudioContext() {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioContext;
  }
  
  /** Convert MIDI to frequency, but shift up an octave by adding 12 if desired */
  function midiToFrequency(midi, octaveShift = 12) {
    const shiftedMidi = midi + octaveShift; 
    return 440 * Math.pow(2, (shiftedMidi - 69) / 12);
  }
  
  /** Start playing a note (if not already playing) */
  function startOscillator(midi) {
    if (activeOscillators[midi]) {
      // Already playing
      return;
    }
    const ctx = getAudioContext();
    const freq = midiToFrequency(midi, 12); // shift 1 octave up
    const osc = ctx.createOscillator();
  
    osc.type = "triangle"; // "sawtooth", "square", "triangle", or "sine"
    osc.frequency.value = freq;
  
    const gain = ctx.createGain();
    gain.gain.value = 0.15; // volume
  
    osc.connect(gain).connect(ctx.destination);
    osc.start();
  
    activeOscillators[midi] = { osc, gain };
  }
  
  /** Stop playing a note if it is active */
  function stopOscillator(midi) {
    if (!activeOscillators[midi]) return;
    const { osc, gain } = activeOscillators[midi];
    osc.stop();
    osc.disconnect();
    gain.disconnect();
    delete activeOscillators[midi];
  }
  
  // ----------------------
  // PITCH LINE MAPPING
  // ----------------------
  function freqToFloatMidi(freq) {
    if (!freq || freq <= 0) return null;
    return 12 * Math.log2(freq / 440) + 69;
  }
  
  function freqToMidiRound(freq) {
    const fm = freqToFloatMidi(freq);
    return fm == null ? null : Math.round(fm);
  }
  
  // ----------------------
  // KEYBOARD MAPPING
  // A simple "ASDF" style layout for demonstration
  // (this is arbitrary; just pick a pattern you like).
  // "a" -> 60 (C4), "w" -> 61 (C#4), "s" -> 62 (D4), etc.
  // ----------------------
  const keyboardMap = {
    KeyZ: 41, // 'z' -> F2
    KeyS: 42, // 's' -> F#2
    KeyX: 43, // 'x' -> G2
    KeyD: 44, // 'd' -> G#2
    KeyC: 45, // 'c' -> A2
    KeyF: 46, // 'f' -> A#2
    KeyV: 47, // 'v' -> B2
    KeyB: 48, // 'b' -> C3
    KeyH: 49, // 'h' -> C#3
    KeyN: 50, // 'n' -> D3
    KeyJ: 51, // 'j' -> D#3
    KeyM: 52, // 'm' -> E3
    KeyQ: 53, // 'q' -> F3
    Digit2: 54, // '2' -> F#3
    KeyW: 55, // 'w' -> G3
    Digit3: 56, // '3' -> G#3
    KeyE: 57, // 'e' -> A3
    Digit4: 58, // '4' -> A#3
    KeyR: 59, // 'r' -> B3
    KeyT: 60, // 't' -> C4
    Digit6: 61, // '6' -> C#4
    KeyY: 62, // 'y' -> D4
    Digit7: 63, // '7' -> D#4
    KeyU: 64, // 'u' -> E4
    KeyI: 65, // 'i' -> F4
  };
  
  const PianoVisualizer = ({ pitchData, audioRef, playbackSpeed }) => {
    const canvasRef = useRef(null);
    const pianoRef = useRef(null);
  
    // We'll measure the center of each piano key so the falling pitch line aligns exactly
    const [keyCenters, setKeyCenters] = useState({}); 
    // The audio engine will highlight a note near the current pitch
    const [audioHighlighted, setAudioHighlighted] = useState(null); 
    // The user can press multiple notes at once (mouse or keyboard), so store them in a set
    const [userActiveNotes, setUserActiveNotes] = useState(new Set());
  
    // Sort piano keys in ascending MIDI
    const pianoKeys = Object.keys(midiToPianoKeys)
      .map((m) => parseInt(m, 10))
      .sort((a, b) => a - b);
  
    // Validate pitch data format
    useEffect(() => {
      if (!pitchData) {
        console.log('No pitch data available');
        return;
      }

      if (!Array.isArray(pitchData)) {
        console.error('Invalid pitch data format:', pitchData);
        return;
      }

      const samplePoint = pitchData[0];
      if (!samplePoint || typeof samplePoint.time !== 'number' || typeof samplePoint.frequency !== 'number') {
        console.error('Invalid pitch data point format:', samplePoint);
        return;
      }
    }, [pitchData]);
  
    // Set canvas dimensions
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      
      // Set explicit dimensions
      canvas.width = 800;
      canvas.height = 300;
      
      console.log('Set canvas dimensions:', { width: canvas.width, height: canvas.height });
    }, []);
  
    // Debug logging
    useEffect(() => {
      console.log('PianoVisualizer mounted');
      console.log('Initial pitch data:', pitchData?.slice(0, 2));
      console.log('Canvas ref:', canvasRef.current);
      console.log('Piano ref:', pianoRef.current);
    }, [pitchData]);
  
    // ----------------------
    // 1) Measure Keys Exactly Once
    // ----------------------
    useLayoutEffect(() => {
      console.log('Measuring key centers...');
      if (!pianoRef.current) {
        console.log('Piano ref not available');
        return;
      }
  
      const pianoRect = pianoRef.current.getBoundingClientRect();
      console.log('Piano rect:', pianoRect);
      const newCenters = {};
  
      const keyEls = pianoRef.current.querySelectorAll(".piano-key");
      keyEls.forEach((el) => {
        const midiStr = el.getAttribute("data-midi");
        if (!midiStr) return;
        const midi = parseInt(midiStr, 10);
  
        const rect = el.getBoundingClientRect();
        // center X relative to the .piano container
        const centerX = rect.left + rect.width / 2 - pianoRect.left;
        newCenters[midi] = centerX;
      });
  
      setKeyCenters(newCenters);
    }, []);
  
    // ----------------------
    // 2) Map freq -> X by Interpolating Key Centers
    // ----------------------
    const getXFromFreq = useCallback(
      (freq) => {
        const floatMidi = freqToFloatMidi(freq);
        if (floatMidi == null) return null;
  
        const minM = pianoKeys[0];
        const maxM = pianoKeys[pianoKeys.length - 1];
  
        if (floatMidi <= minM) return keyCenters[minM] ?? null;
        if (floatMidi >= maxM) return keyCenters[maxM] ?? null;
  
        const base = Math.floor(floatMidi);
        const next = base + 1;
        const frac = floatMidi - base;
  
        const x1 = keyCenters[base];
        const x2 = keyCenters[next];
        if (x1 == null && x2 == null) return null;
        if (x1 == null) return x2;
        if (x2 == null) return x1;
  
        return x1 + frac * (x2 - x1);
      },
      [keyCenters, pianoKeys]
    );
  
    // ----------------------
    // 3) Falling Pitch Animation
    // ----------------------
    useEffect(() => {
      console.log('Setting up animation frame');
      const canvas = canvasRef.current;
      if (!canvas) {
        console.log('Canvas not available');
        return;
      }
      const ctx = canvas.getContext("2d");
      const width = canvas.width;
      const height = canvas.height;
      
      console.log('Canvas dimensions:', { width, height });

      const pianoHeight = 100;
      const fallDuration = 1.0; // 1 second from top to keys
      let rafId;

      function renderFrame() {
        rafId = requestAnimationFrame(renderFrame);
        if (!audioRef.current || !pitchData) {
          return;
        }

        const currentTime = audioRef.current.currentTime;
        
        // Adjust the time window based on playback speed
        const adjustedFallDuration = fallDuration / playbackSpeed;
        
        // Show points in the last [−adjustedFallDuration, 0] seconds relative to currentTime
        const visiblePoints = pitchData.filter((pt) => {
          const tDiff = currentTime - pt.time;
          return tDiff >= -adjustedFallDuration && tDiff <= 0;
        });

        if (visiblePoints.length > 0) {
          console.log('Visible points:', visiblePoints.length);
        }

        ctx.clearRect(0, 0, width, height);
        ctx.beginPath();

        visiblePoints.forEach((pt, i) => {
          const tDiff = currentTime - pt.time;
          const normalized = (tDiff + adjustedFallDuration) / adjustedFallDuration; // 0..1
          const y = normalized * (height - pianoHeight);

          const x = getXFromFreq(pt.frequency);
          if (x == null) return;

          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });

        ctx.strokeStyle = "red";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Highlight the "current" pitch if within ±20ms (adjusted for playback speed)
        const timeWindow = 0.02 / playbackSpeed;
        const nowPitch = pitchData.find((pt) => Math.abs(pt.time - currentTime) < timeWindow);
        if (nowPitch) {
          const newKey = freqToMidiRound(nowPitch.frequency);
          // Only update if changed
          setAudioHighlighted((oldKey) => (oldKey !== newKey ? newKey : oldKey));
        } else {
          setAudioHighlighted((oldKey) => (oldKey != null ? null : oldKey));
        }
      }

      console.log('Starting animation frame');
      rafId = requestAnimationFrame(renderFrame);

      return () => {
        console.log('Cleaning up animation frame');
        if (rafId) cancelAnimationFrame(rafId);
      };
    }, [pitchData, audioRef, playbackSpeed, getXFromFreq]);
  
    // ----------------------
    // 4) Piano Mouse Events
    // ----------------------
    const handleMouseDown = (midi) => {
      // Start oscillator
      startOscillator(midi);
      // Add to userActiveNotes
      setUserActiveNotes((prev) => {
        if (prev.has(midi)) return prev; // already pressed
        return new Set([...prev, midi]);
      });
    };
  
    const handleMouseUpOrLeave = (midi) => {
      // Stop oscillator
      stopOscillator(midi);
      // Remove from userActiveNotes
      setUserActiveNotes((prev) => {
        if (!prev.has(midi)) return prev;
        const copy = new Set(prev);
        copy.delete(midi);
        return copy;
      });
    };
  
    // ----------------------
    // 5) Keyboard Events
    //    Pressing e.g. 'a' -> MIDI=60
    //    We'll do polyphonic: multiple keys can be pressed at once.
    // ----------------------
    useEffect(() => {
      function onKeyDown(e) {
        const midi = keyboardMap[e.code]; 
        if (midi == null) return; // not a mapped key
        // If it's newly pressed, start note
        if (!userActiveNotes.has(midi)) {
          startOscillator(midi);
          setUserActiveNotes((prev) => new Set([...prev, midi]));
        }
      }
  
      function onKeyUp(e) {
        const midi = keyboardMap[e.code];
        if (midi == null) return;
        stopOscillator(midi);
        setUserActiveNotes((prev) => {
          if (!prev.has(midi)) return prev;
          const copy = new Set(prev);
          copy.delete(midi);
          return copy;
        });
      }
  
      window.addEventListener("keydown", onKeyDown);
      window.addEventListener("keyup", onKeyUp);
  
      return () => {
        window.removeEventListener("keydown", onKeyDown);
        window.removeEventListener("keyup", onKeyUp);
      };
    }, [userActiveNotes]);
  
    // ----------------------
    // 6) Which keys to highlight?
    //    - The audio currently highlighting (audioHighlighted)
    //    - Any notes in userActiveNotes
    // ----------------------
    const getKeyClass = (midi) => {
      const label = midiToPianoKeys[midi];
      const isBlack = label.includes("#");
      // If the audio is highlighting *this* note
      const highlightAudio = audioHighlighted === midi;
      // If the user is pressing this note (mouse or keyboard)
      const highlightUser = userActiveNotes.has(midi);
  
      const isActive = highlightAudio || highlightUser;
      return `${isBlack ? "black" : "white"} ${isActive ? "active" : ""}`;
    };
  
    return (
      <div className="piano-visualizer">
        <canvas ref={canvasRef} width={800} height={300} className="pitch-canvas" />
        <div className="piano" ref={pianoRef}>
          {pianoKeys.map((midi) => {
            const label = midiToPianoKeys[midi];
            return (
              <div
                key={midi}
                data-midi={midi}
                className={`piano-key ${getKeyClass(midi)}`}
                onMouseDown={() => handleMouseDown(midi)}
                onMouseUp={() => handleMouseUpOrLeave(midi)}
                onMouseLeave={(e) => {
                  // If mouse is pressed and we leave the key, we stop the note
                  if (e.buttons === 1) {
                    handleMouseUpOrLeave(midi);
                  }
                }}
              >
                <span className="label">{label}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };
  
  export default PianoVisualizer;
  