import React, { useState, useEffect } from "react";
import { FaPlay, FaPause } from "react-icons/fa";
import { IoVolumeHigh, IoVolumeMute } from "react-icons/io5";

const AudioPlayer = ({ src, audioRef }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;

    const updateCurrentTime = () => {
      setCurrentTime(audio.currentTime);
    };

    const setAudioDuration = () => {
      setDuration(audio.duration || 0);
    };

    if (audio) {
      audio.addEventListener("timeupdate", updateCurrentTime);
      audio.addEventListener("loadedmetadata", setAudioDuration);
    }

    return () => {
      if (audio) {
        audio.removeEventListener("timeupdate", updateCurrentTime);
        audio.removeEventListener("loadedmetadata", setAudioDuration);
      }
    };
  }, [audioRef]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (audio) {
      if (isPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (audio) {
      audio.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleSliderChange = (event) => {
    const audio = audioRef.current;
    const newTime = parseFloat(event.target.value);
    if (audio) {
      audio.currentTime = newTime;
    }
    setCurrentTime(newTime);
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  return (
    <div style={styles.container}>
      <button onClick={togglePlay} style={styles.button}>
        {isPlaying ? <FaPause size={20} /> : <FaPlay size={20} />}
      </button>
      <audio ref={audioRef} src={src}></audio>
      <input
        type="range"
        min="0"
        max={duration}
        step="0.1"
        value={currentTime}
        onChange={handleSliderChange}
        style={styles.slider}
      />
      <span style={styles.time}>
        {formatTime(currentTime)} / {formatTime(duration)}
      </span>
      <button onClick={toggleMute} style={styles.button}>
        {isMuted ? <IoVolumeMute size={20} /> : <IoVolumeHigh size={20} />}
      </button>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    backgroundColor: "#2b2b2b",
    padding: "10px 20px",
    borderRadius: "10px",
    width: "100%",
    maxWidth: "600px",
    margin: "0 auto",
  },
  button: {
    backgroundColor: "transparent",
    color: "white",
    border: "none",
    cursor: "pointer",
  },
  slider: {
    flex: 1,
    margin: "0 10px",
    appearance: "none",
    backgroundColor: "#444",
    height: "5px",
    borderRadius: "5px",
    outline: "none",
    cursor: "pointer",
  },
  time: {
    color: "#fff",
    fontSize: "14px",
  },
};

export default AudioPlayer;
