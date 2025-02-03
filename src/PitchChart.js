import React from "react";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend
);

/**
 * A simple line chart of pitchData:
 *  - X-axis: time in seconds
 *  - Y-axis: frequency in Hz
 * No special note labeling, just a straightforward chart.
 */
const PitchChart = ({ data }) => {
  // If no data, fallback to an empty array
  const pitchData = data || [];

  // In case the data is empty, default to a 30s span
  const totalDuration = pitchData.length > 0
    ? pitchData[pitchData.length - 1].time
    : 30;

  // Prepare the data for Chart.js
  const chartData = {
    labels: pitchData.map((d) => d.time), // x-axis
    datasets: [
      {
        label: "Pitch (Hz)",
        data: pitchData.map((d) => d.frequency), // y-axis
        borderColor: "rgba(75,192,192,1)",
        borderWidth: 2,
        pointRadius: 0, // no dots on each point
      },
    ],
  };

  // Basic chart options
  const options = {
    animation: false, // no animations
    responsive: true,
    maintainAspectRatio: false, // allow a custom height
    scales: {
      x: {
        title: { display: true, text: "Time (s)" },
        min: 0,
        max: totalDuration,
      },
      y: {
        title: { display: true, text: "Frequency (Hz)" },
        // You could set min/max if you want a fixed range, e.g.:
        // min: 65, max: 294,  // ~C2..D4
      },
    },
    plugins: {
      legend: {
        position: "top",
      },
    },
  };

  return (
    <div style={{ height: "300px" }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default PitchChart;
