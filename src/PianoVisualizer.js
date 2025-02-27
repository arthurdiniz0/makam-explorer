import React, {
    useRef,
    useState,
    useEffect,
    useLayoutEffect,
    useCallback,
  } from "react";
  import "./PianoVisualizer.css";
  import TuningInfoModal from './TuningInfoModal';
  import instrumentManager from './InstrumentManager';
  import InstrumentSelector from './components/InstrumentSelector';
  
  // ----------------------
  // MIDI -> Label (F3=53 ~ A5=81). Shifted up one octave.
  // ----------------------
  const midiToPianoKeys = {
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
    63: "D#4",
    64: "E4",
    65: "F4",
    66: "F#4",
    67: "G4",
    68: "G#4",
    69: "A4",
    70: "A#4",
    71: "B4",
    72: "C5",
    73: "C#5",
    74: "D5",
    75: "D#5",
    76: "E5",
    77: "F5",
    78: "F#5",
    79: "G5",
    80: "G#5",
    81: "A5"
  };
  
  // ----------------------
  // AUDIO: Oscillators, One Octave Up
  // ----------------------
  
  /** Convert MIDI to frequency using A3=110Hz as reference */
  function midiToFrequency(midi, octaveShift = 0) {
    const shiftedMidi = midi + octaveShift;
    // Use A3=110Hz as reference (MIDI 57)
    return 110 * Math.pow(2, (shiftedMidi - 57) / 12);
  }
  
  // Update the utility functions at the top
  function hzToCents(hz, referenceFreq = 110) {
    if (hz <= 0) return null;
    return 1200 * Math.log2(hz / referenceFreq);
  }
  
  function centsToHz(cents, referenceFreq = 110) {
    if (!isFinite(cents)) return null;
    return referenceFreq * Math.pow(2, cents / 1200);
  }
  
  function findClosestCent(targetCent, centArray) {
    if (!centArray || centArray.length === 0) return null;
    
    // Find the closest peak considering octave equivalence
    return centArray.reduce((prev, curr) => {
      // Calculate the absolute distance in cents, considering octave wrapping
      const prevDist = Math.abs(((targetCent - prev + 600) % 1200) - 600);
      const currDist = Math.abs(((targetCent - curr + 600) % 1200) - 600);
      return currDist < prevDist ? curr : prev;
    });
  }
  
  // Add these utility functions
  function freqToFloatMidi(freq) {
    if (!freq || freq <= 0) return null;
    // Convert relative to A3 (110Hz = MIDI 57)
    return 12 * Math.log2(freq / 110) + 57;
  }
  
  function freqToMidiRound(freq) {
    const fm = freqToFloatMidi(freq);
    return fm == null ? null : Math.round(fm);
  }
  
  // Add keyboard mapping
  const keyboardMap = {
    KeyZ: 53, // 'z' -> F3
    KeyS: 54, // 's' -> F#3
    KeyX: 55, // 'x' -> G3
    KeyD: 56, // 'd' -> G#3
    KeyC: 57, // 'c' -> A3
    KeyF: 58, // 'f' -> A#3
    KeyV: 59, // 'v' -> B3
    KeyB: 60, // 'b' -> C4
    KeyH: 61, // 'h' -> C#4
    KeyN: 62, // 'n' -> D4
    KeyJ: 63, // 'j' -> D#4
    KeyM: 64, // 'm' -> E4
    KeyQ: 65, // 'q' -> F4
    Digit2: 66, // '2' -> F#4
    KeyW: 67, // 'w' -> G4
    Digit3: 68, // '3' -> G#4
    KeyE: 69, // 'e' -> A4
    Digit4: 70, // '4' -> A#4
    KeyR: 71, // 'r' -> B4
    KeyT: 72, // 't' -> C5
    Digit6: 73, // '6' -> C#5
    KeyY: 74, // 'y' -> D5
    Digit7: 75, // '7' -> D#5
    KeyU: 76, // 'u' -> E5
    KeyI: 77, // 'i' -> F5
    Digit9: 78, // '9' -> F#5
    KeyO: 79, // 'o' -> G5
    Digit0: 80, // '0' -> G#5
    KeyP: 81  // 'p' -> A5
  };
  
  // Add a function to find peaks in histogram data
  function findHistogramPeaks(histValues, histEdges, minPeakHeight = 0.1) {
    // First normalize the values to 0-1 range
    const maxVal = Math.max(...histValues);
    const normalizedValues = histValues.map(v => v / maxVal);
    
    // Find peaks (points higher than their neighbors and above minPeakHeight)
    const peaks = [];
    for (let i = 1; i < normalizedValues.length - 1; i++) {
      if (normalizedValues[i] > minPeakHeight && 
          normalizedValues[i] > normalizedValues[i-1] && 
          normalizedValues[i] > normalizedValues[i+1]) {
        peaks.push({
          cent: histEdges[i],
          strength: normalizedValues[i]
        });
      }
    }
    
    // Sort by strength and take top peaks
    return peaks.sort((a, b) => b.strength - a.strength);
  }
  
  // Add this function near the top with other utility functions
  function getKeyboardLabel(midi) {
    // Find the keyboard key for this MIDI note
    const entry = Object.entries(keyboardMap).find(([_, midiNum]) => midiNum === midi);
    if (!entry) return '';
    
    const keyCode = entry[0];
    // Convert KeyX format to actual key label
    if (keyCode.startsWith('Key')) {
      return keyCode.slice(3).toLowerCase();
    } else if (keyCode.startsWith('Digit')) {
      return keyCode.slice(5);
    }
    return '';
  }
  
  // Add these utility functions after the existing utility functions and before the component

  function createTuningArray(locsCent, arrayLen) {
    // Create a binary array representing frequency peaks, similar to Python implementation
    const stepSizeCents = 1200 / arrayLen;
    const arr = new Array(arrayLen).fill(0);
    
    locsCent.forEach(cents => {
      const index = Math.round(cents / stepSizeCents) % arrayLen;
      arr[index] = 1;
    });
    
    return arr;
  }

  function convolve(kernel, arr) {
    // Simple convolution for smoothing
    const result = new Array(arr.length).fill(0);
    for (let i = 0; i < arr.length; i++) {
      for (let k = 0; k < kernel.length; k++) {
        const idx = (i - Math.floor(kernel.length/2) + k + arr.length) % arr.length;
        result[i] += kernel[k] * arr[idx];
      }
    }
    return result;
  }

  function findOptimalShift(locsCentArr1, locsCentArr2, numNotesInOctave = 60) {
    // Create simplified distribution-like representations
    const arr1 = createTuningArray(locsCentArr1, numNotesInOctave);
    const arr2 = createTuningArray(locsCentArr2, numNotesInOctave);
    
    // Smooth arrays
    const kernel = [0.25, 0.5, 0.25];
    const smoothArr1 = convolve(kernel, arr1);
    const smoothArr2 = convolve(kernel, arr2);
    
    let minDistance = Infinity;
    let optimalShiftAmount = 0;
    
    // Find optimal shift
    for (let shift = 0; shift < smoothArr1.length; shift++) {
      const rotatedArr1 = [...smoothArr1.slice(shift), ...smoothArr1.slice(0, shift)];
      const distance = Math.sqrt(
        rotatedArr1.reduce((sum, val, i) => sum + Math.pow(val - smoothArr2[i], 2), 0)
      );
      
      if (distance < minDistance) {
        minDistance = distance;
        optimalShiftAmount = shift;
      }
    }
    
    // Convert shift amount to cents
    const optimalShiftCents = (optimalShiftAmount * 1200) / numNotesInOctave;
    return optimalShiftCents;
  }

  function mapToClosest(arr1, arr2) {
    // Replace values in arr1 with closest values from arr2
    const result = [...arr1];
    
    arr2.forEach(targetVal => {
      let minDiff = Infinity;
      let minIdx = 0;
      
      result.forEach((val, idx) => {
        const diff = Math.abs(val - targetVal);
        if (diff < minDiff) {
          minDiff = diff;
          minIdx = idx;
        }
      });
      
      result[minIdx] = targetVal;
    });
    
    // Check if all values in arr2 are represented
    arr2.forEach(val => {
      if (!result.includes(val)) {
        result.push(val);
      }
    });
    
    return result.sort((a, b) => a - b);
  }

  function createKeyboardMapping(maximaLocsCent) {
    // Create theoretical frequencies (0, 100, 200, ..., 1100)
    const theoreticalFreqs = Array.from({length: 12}, (_, i) => i * 100);
    
    // Find optimal shift
    const shiftCents = findOptimalShift(maximaLocsCent, theoreticalFreqs);
    
    // Shift theoretical frequencies
    const shiftedFreqs = theoreticalFreqs.map(f => (f - shiftCents + 1200) % 1200);
    
    // Map to closest estimated frequencies
    return mapToClosest(shiftedFreqs, maximaLocsCent);
  }
  
  const PianoVisualizer = ({ pitchData, audioRef, playbackSpeed, maximaLocsCent }) => {
    const canvasRef = useRef(null);
    const pianoRef = useRef(null);
    const tuningButtonRef = useRef(null);
    const audioContextRef = useRef(null);
    const activeOscillatorsRef = useRef(new Map());
    const [showTuningInfo, setShowTuningInfo] = useState(false);
    const [mappedNotes, setMappedNotes] = useState(new Map());
    const [keyCenters, setKeyCenters] = useState({}); 
    const [audioHighlighted, setAudioHighlighted] = useState(null); 
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

      console.log('Received pitch data with keys:', Object.keys(pitchData));
      console.log('Maxima locations:', pitchData.maxima_locs_cent);
      console.log('Mapped frequencies:', {
        hz: pitchData.mapped_key_freqs_hz,
        cents: pitchData.mapped_key_freqs_cent
      });

      if (!pitchData.pitchPoints || !Array.isArray(pitchData.pitchPoints)) {
        console.error('Invalid pitch data format:', pitchData);
        return;
      }

      const samplePoint = pitchData.pitchPoints[0];
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
      console.log('Initial pitch data:', {
        points: pitchData?.pitchPoints?.slice(0, 2),
        histogramBins: pitchData?.pitch_hist_values?.length,
        maximaCount: pitchData?.maxima_locs_cent?.length,
        maxima: pitchData?.maxima_locs_cent
      });
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
        // Convert frequency to cents relative to A3 (110Hz)
        const cents = hzToCents(freq, 110);
        if (cents === null) return null;

        // Find the two closest mapped notes
        let closest = { midi: null, diff: Infinity };
        let secondClosest = { midi: null, diff: Infinity };

        mappedNotes.forEach((note, midi) => {
          if (!note.isMapped) return;
          const diff = Math.abs(note.mappedCents - cents);
          if (diff < closest.diff) {
            secondClosest = closest;
            closest = { midi, diff };
          } else if (diff < secondClosest.diff) {
            secondClosest = { midi, diff };
          }
        });

        if (closest.midi === null) {
          // Fall back to standard MIDI mapping if no mapped notes found
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
        }

        // If we only found one mapped note, use its position
        if (secondClosest.midi === null) {
          return keyCenters[closest.midi];
        }

        // Get the mapped notes' data
        const note1 = mappedNotes.get(closest.midi);
        const note2 = mappedNotes.get(secondClosest.midi);
        
        // Calculate interpolation factor
        const totalDiff = Math.abs(note2.mappedCents - note1.mappedCents);
        if (totalDiff === 0) return keyCenters[closest.midi];
        
        const fraction = Math.abs(cents - note1.mappedCents) / totalDiff;
        
        // Interpolate between the two positions
        const x1 = keyCenters[closest.midi];
        const x2 = keyCenters[secondClosest.midi];
        
        return x1 + fraction * (x2 - x1);
      },
      [keyCenters, pianoKeys, mappedNotes]
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
        if (!audioRef.current || !pitchData?.pitchPoints) {
          return;
        }
  
        const currentTime = audioRef.current.currentTime;
        
        // Adjust the time window based on playback speed
        const adjustedFallDuration = fallDuration / playbackSpeed;
        
        // Show points in the last [−adjustedFallDuration, 0] seconds relative to currentTime
        const visiblePoints = pitchData.pitchPoints.filter((pt) => {
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
        const nowPitch = pitchData.pitchPoints.find((pt) => Math.abs(pt.time - currentTime) < timeWindow);
        if (nowPitch) {
          // Convert frequency to cents and find closest mapped note
          const cents = hzToCents(nowPitch.frequency, 110);
          let closestMidi = null;
          let minDiff = Infinity;

          mappedNotes.forEach((note, midi) => {
            if (!note.isMapped) return;
            const diff = Math.abs(note.mappedCents - cents);
            if (diff < minDiff) {
              minDiff = diff;
              closestMidi = midi;
            }
          });

          // Only update if changed
          setAudioHighlighted((oldKey) => (oldKey !== closestMidi ? closestMidi : oldKey));
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
  
    // Initialize audio context first
    useEffect(() => {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      return () => {
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
      };
    }, []);
  
    // Define audio functions before they are used
    const startOscillator = useCallback((midi) => {
      if (activeOscillatorsRef.current.has(midi)) {
        return;
      }

      const mappedNote = mappedNotes.get(midi);
      let frequency;
      
      if (mappedNote?.isMapped) {
        frequency = mappedNote.mappedHz;
        console.log(`Playing mapped frequency for MIDI ${midi}: ${frequency}Hz (${Math.round(mappedNote.mappedCents)}¢)`);
      } else {
        frequency = midiToFrequency(midi);
        console.log(`Playing Western frequency for MIDI ${midi}: ${frequency}Hz`);
      }

      // Validate frequency before using it
      if (!isFinite(frequency) || frequency <= 0) {
        console.error(`Invalid frequency for MIDI ${midi}: ${frequency}`);
        return;
      }

      // Play the note using the instrument manager
      instrumentManager.playNote(frequency);
      activeOscillatorsRef.current.set(midi, { frequency });
    }, [mappedNotes]);

    const stopOscillator = useCallback((midi) => {
      const oscillatorData = activeOscillatorsRef.current.get(midi);
      if (!oscillatorData) return;

      // Stop the note using the instrument manager
      instrumentManager.stopNote(oscillatorData.frequency);
      activeOscillatorsRef.current.delete(midi);
    }, []);
  
    // Define event handlers after audio functions
    const handleMouseDown = useCallback(async (midi) => {
      try {
        await startOscillator(midi);
      setUserActiveNotes((prev) => {
          if (prev.has(midi)) return prev;
        return new Set([...prev, midi]);
      });
      } catch (error) {
        console.error('Error in handleMouseDown:', error);
      }
    }, [startOscillator]);
  
    const handleMouseUpOrLeave = useCallback((midi) => {
      stopOscillator(midi);
      setUserActiveNotes((prev) => {
        if (!prev.has(midi)) return prev;
        const copy = new Set(prev);
        copy.delete(midi);
        return copy;
      });
    }, [stopOscillator]);
  
    // ----------------------
    // 4) Keyboard Events
    //    Pressing e.g. 'a' -> MIDI=60
    //    We'll do polyphonic: multiple keys can be pressed at once.
    // ----------------------
    useEffect(() => {
      async function onKeyDown(e) {
        const midi = keyboardMap[e.code]; 
        if (midi == null) return;
        if (!userActiveNotes.has(midi)) {
          try {
            await startOscillator(midi);
          setUserActiveNotes((prev) => new Set([...prev, midi]));
          } catch (error) {
            console.error('Error in onKeyDown:', error);
          }
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
    }, [startOscillator, stopOscillator, userActiveNotes]);
  
    // Update the effect that computes mapped notes
    useEffect(() => {
      // Debug the incoming data
      console.log('Pitch data received:', pitchData);
      
      // Check for mapped frequencies in the correct location
      let baseFreqsHz = pitchData?.mapped_key_freqs_hz;
      let baseFreqsCent = pitchData?.mapped_key_freqs_cent;
      const maximaLocsCent = pitchData?.maxima_locs_cent;

      if (!baseFreqsHz || !baseFreqsCent) {
        console.log('No mapped frequencies available, attempting to compute from maxima');
        if (!maximaLocsCent || !Array.isArray(maximaLocsCent)) {
          console.log('No maxima locations available for mapping');
          return;
        }

        // Create theoretical frequencies (0, 100, 200, ..., 1100)
        const theoreticalFreqs = Array.from({length: 12}, (_, i) => i * 100);
        
        // Find optimal shift
        const shiftCents = findOptimalShift(maximaLocsCent, theoreticalFreqs);
        console.log('Computed optimal shift:', shiftCents, 'cents');
        
        // Shift theoretical frequencies and map to closest maxima
        const shiftedFreqs = theoreticalFreqs.map(f => (f - shiftCents + 1200) % 1200);
        baseFreqsCent = mapToClosest(shiftedFreqs, maximaLocsCent);
        
        // Convert cents to Hz (relative to A3 = 110Hz)
        baseFreqsHz = baseFreqsCent.map(cents => centsToHz(cents, 110));
        
        console.log('Computed mappings:', {
          baseFreqsCent,
          baseFreqsHz
        });
      }

      // Create a mapping for each MIDI note
      const newMappedNotes = new Map();
      
      // Calculate frequencies for each MIDI note for reference
      const midiCents = Object.entries(midiToPianoKeys).map(([midi, note]) => {
        const freq = midiToFrequency(parseInt(midi, 10));
        const cents = hzToCents(freq, 110); // Convert to cents relative to A3 (110Hz)
        return {
          midi: parseInt(midi, 10),
          note,
          westernFreq: freq,
          westernCents: cents
        };
      }).sort((a, b) => a.midi - b.midi);  // Sort by MIDI number to maintain keyboard order

      // Find the base octave (A3 = MIDI 57)
      const baseOctaveMidi = 57; // A3
      const baseOctaveIndex = Math.floor((baseOctaveMidi - midiCents[0].midi) / 12);
      
      // Map each MIDI note to a frequency
      midiCents.forEach((midiInfo) => {
        const midiOffset = midiInfo.midi - (baseOctaveMidi - (baseOctaveIndex * 12));
        const octaveOffset = Math.floor(midiOffset / 12);
        const keyIndex = ((midiOffset % 12) + 12) % 12;
        
        if (keyIndex < baseFreqsHz.length) {
          const mappedHz = baseFreqsHz[keyIndex] * Math.pow(2, octaveOffset);
          const mappedCents = baseFreqsCent[keyIndex] + (octaveOffset * 1200);
          
          // Check if this note directly matches a peak
          const isDirectPeakMatch = pitchData.maxima_locs_cent.some(
            peakCent => Math.abs((mappedCents % 1200) - (peakCent % 1200)) < 15
          );
          
          newMappedNotes.set(midiInfo.midi, {
            midi: midiInfo.midi,
            westernFreq: midiInfo.westernFreq,
            westernCents: midiInfo.westernCents,
            mappedCents,
            mappedHz,
            centDiff: mappedCents - midiInfo.westernCents,
            isMapped: true,
            isDirectPeakMatch
          });

          console.log(`Mapped key '${getKeyboardLabel(midiInfo.midi)}' (${midiInfo.note}) to ${Math.round(mappedHz)}Hz (${Math.round(mappedCents)}¢)`);
        }
      });

      console.log('Created mappings for', newMappedNotes.size, 'notes');
      setMappedNotes(newMappedNotes);
    }, [pitchData]);
  
    // ----------------------
    // 6) Which keys to highlight?
    //    - The audio currently highlighting (audioHighlighted)
    //    - Any notes in userActiveNotes
    // ----------------------
    const getKeyClass = (midi) => {
      const label = midiToPianoKeys[midi];
      const isBlack = label.includes("#");
      const highlightAudio = audioHighlighted === midi;
      const highlightUser = userActiveNotes.has(midi);
      const mappedNote = mappedNotes.get(midi);
      
      const classes = [
        isBlack ? "black" : "white",
        highlightAudio || highlightUser ? "active" : "",
        mappedNote?.isDirectPeakMatch ? "peak-match" : ""
      ];
      
      if (mappedNote?.centDiff) {
        if (mappedNote.centDiff > 15) classes.push("sharp");
        else if (mappedNote.centDiff < -15) classes.push("flat");
      }
      
      return classes.filter(Boolean).join(" ");
    };
  
    // Add cleanup in the audio context effect:
    useEffect(() => {
      return () => {
        instrumentManager.dispose();
      };
    }, []);
  
    return (
      <div className="piano-visualizer-container">
        <div className="piano-visualizer-controls">
          <InstrumentSelector />
          <button 
            ref={tuningButtonRef}
            className={`tuning-toggle ${showTuningInfo ? 'active' : ''}`}
            onClick={() => setShowTuningInfo(!showTuningInfo)}
          >
            {showTuningInfo ? 'Hide Tuning Info' : 'Show Tuning Info'}
          </button>
        </div>

        {showTuningInfo && (
          <TuningInfoModal
            mappedNotes={mappedNotes}
            midiToPianoKeys={midiToPianoKeys}
            getKeyboardLabel={getKeyboardLabel}
            midiToFrequency={midiToFrequency}
            onClose={() => setShowTuningInfo(false)}
            buttonRef={tuningButtonRef}
          />
        )}
        
      <div className="piano-visualizer">
        <canvas ref={canvasRef} width={800} height={300} className="pitch-canvas" />
        <div className="piano" ref={pianoRef}>
          {pianoKeys.map((midi) => {
            const label = midiToPianoKeys[midi];
              const mappedNote = mappedNotes.get(midi);
              const centDiff = mappedNote?.centDiff || 0;
              
            return (
              <div
                key={midi}
                data-midi={midi}
                className={`piano-key ${getKeyClass(midi)}`}
                onMouseDown={() => handleMouseDown(midi)}
                onMouseUp={() => handleMouseUpOrLeave(midi)}
                onMouseLeave={(e) => {
                  if (e.buttons === 1) {
                    handleMouseUpOrLeave(midi);
                  }
                }}
              >
                  <span className="label">{getKeyboardLabel(midi)}</span>
                  {showTuningInfo && mappedNote && (
                    <>
                      <span className="mapped-freq">
                        {Math.round(mappedNote.mappedHz)}Hz
                      </span>
                      <span className={`cent-diff ${centDiff > 15 ? 'sharp' : centDiff < -15 ? 'flat' : ''}`}>
                        {centDiff > 0 ? '+' : ''}{Math.round(centDiff)}¢
                      </span>
                      {Math.abs(centDiff) > 15 && (
                        <div 
                          className="detune-indicator"
                          style={{
                            height: `${Math.min(Math.abs(centDiff), 100)}%`,
                            backgroundColor: centDiff > 0 ? '#ff4444' : '#4444ff'
                          }}
                        />
                      )}
                    </>
                  )}
              </div>
            );
          })}
          </div>
        </div>
      </div>
    );
  };
  
  export default PianoVisualizer;
  