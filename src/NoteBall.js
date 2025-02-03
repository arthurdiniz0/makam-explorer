import React from "react";

const notes = [
  "C2", "D2", "E2", "F2", "G2", "A2", "B2",
  "C3", "D3", "E3", "F3", "G3", "A3", "B3",
  "C4", "D4", "E4", "F4", "G4", "A4", "B4",
  "C5", "D5", "E5", "F5", "G5", "A5", "B5",
];

const frequencyToNoteAndPosition = (frequency) => {
  if (frequency <= 0) return { note: "", position: 0 };

  const midiNumber = Math.round(12 * Math.log2(frequency / 440) + 69);
  const noteNames = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  const noteName = noteNames[midiNumber % 12];
  const octave = Math.floor(midiNumber / 12) - 1;

  const note = `${noteName}${octave}`;

  // Calculate the position as a percentage based on the note's position in the `notes` array
  const index = notes.indexOf(note);
  const position = index >= 0 ? (index / (notes.length - 1)) * 100 : 0;

  return { note, position };
};

const NoteBall = ({ frequency }) => {
  const { note, position } = frequencyToNoteAndPosition(frequency);

  return (
    <div style={styles.container}>
      <div style={styles.axis}>
        {notes.map((n, index) => (
          <div key={index} style={styles.axisLabel}>
            {n}
          </div>
        ))}
      </div>
      <div style={{ ...styles.ball, top: `${100 - position}%` }}></div>
      <div style={styles.noteLabel}>{note || "N/A"}</div>
    </div>
  );
};

const styles = {
  container: {
    position: "relative",
    width: "150px", // Narrower container
    height: "400px",
    backgroundColor: "#2b2b2b",
    borderRadius: "10px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    paddingLeft: "30px", // Adjust padding to fit axis labels
    overflow: "hidden", // Prevent content from overflowing
  },
  axis: {
    position: "absolute",
    left: "10px", // Keep labels within bounds
    top: "10px",
    bottom: "10px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    alignItems: "flex-start",
    color: "#B0B0B0",
    fontSize: "12px", // Smaller font size
    textAlign: "right",
  },
  axisLabel: {
    flex: "1",
    whiteSpace: "nowrap",
  },
  ball: {
    position: "absolute",
    width: "15px",
    height: "15px",
    borderRadius: "50%",
    backgroundColor: "#4fc3f7",
    transition: "top 0.1s ease-in-out",
  },
  noteLabel: {
    position: "absolute",
    bottom: "10px",
    color: "#ffffff",
    fontSize: "16px",
    fontWeight: "bold",
    textAlign: "center",
    width: "100%",
  },
};

export default NoteBall;
