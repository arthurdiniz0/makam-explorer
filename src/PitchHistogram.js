import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './PitchHistogram.css';

// Function to convert cents to note name (relative to A1 = 55Hz)
const centsToNote = (cents) => {
  const noteNames = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'];
  // Since 0 cents = A1 (55Hz), we start from there
  const semitones = Math.round(cents / 100);
  const octave = Math.floor(semitones / 12) + 1; // Start from octave 1 (A1 = 55Hz)
  const noteIndex = ((semitones % 12) + 12) % 12;
  
  // Adjust octave for notes after B
  // When we cross B->C, we need to increment the octave
  const adjustedOctave = noteIndex < 3 ? octave : octave + 1;
  return noteNames[noteIndex] + adjustedOctave;
};

// Function to get note label with cents
const getNoteLabel = (cents) => {
  if (cents % 100 === 0) {
    return centsToNote(cents);
  }
  return ''; // Only show labels for whole semitones
};

// Add this function near the top with other utility functions
function getKeyboardLabelForCents(cents) {
  // Convert cents to note name first
  const noteName = centsToNote(cents);
  
  // Map of notes to keyboard keys
  const keyboardMap = {
    'F2': 'z', 'F#2': 's', 'G2': 'x', 'G#2': 'd', 'A2': 'c', 'A#2': 'f', 'B2': 'v',
    'C3': 'b', 'C#3': 'h', 'D3': 'n', 'D#3': 'j', 'E3': 'm',
    'F3': 'q', 'F#3': '2', 'G3': 'w', 'G#3': '3', 'A3': 'e', 'A#3': '4', 'B3': 'r',
    'C4': 't', 'C#4': '6', 'D4': 'y', 'D#4': '7', 'E4': 'u',
    'F4': 'i', 'F#4': '9', 'G4': 'o', 'G#4': '0', 'A4': 'p'
  };

  return keyboardMap[noteName] || '';
}

const PitchHistogram = ({ pitchData }) => {
  const svgRef = useRef();
  const containerRef = useRef();

  useEffect(() => {
    console.log('Pitch data received:', pitchData);

    if (!pitchData?.pitch_hist_values || !pitchData?.pitch_hist_edges) {
      console.log('Missing histogram data:', {
        values: pitchData?.pitch_hist_values,
        edges: pitchData?.pitch_hist_edges
      });
      return;
    }

    // Get the histogram data
    const values = Array.from(pitchData.pitch_hist_values || []);  // Default histogram values
    const edges = Array.from(pitchData.pitch_hist_edges);
    const meanValues = Array.from(pitchData.pitch_hist_values_mean || []);
    const pyinValues = Array.from(pitchData.pitch_hist_values_pyin || values);  // Fall back to default values
    const crepeValues = Array.from(pitchData.pitch_hist_values_crepe || []);
    const makamValues = Array.from(pitchData.pitch_hist_values_makam || []);

    // Debug logging
    console.log('Raw pitch data keys:', Object.keys(pitchData));
    console.log('Histogram data lengths:', { 
      default: values.length,
      pyin: pyinValues.length,
      crepe: crepeValues.length,
      makam: makamValues.length,
      mean: meanValues.length,
      edges: edges.length
    });
    console.log('Sample values:', {
      default: values.slice(0, 5),
      pyin: pyinValues.slice(0, 5),
      crepe: crepeValues.slice(0, 5),
      makam: makamValues.slice(0, 5),
      mean: meanValues.slice(0, 5)
    });

    // Clear previous content
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Get container width
    const containerWidth = containerRef.current.clientWidth;
    
    // Set up dimensions with extra space for labels
    const margin = { top: 20, right: 120, bottom: 80, left: 50 };
    const width = Math.min(800, containerWidth - margin.left - margin.right);
    const height = 250 - margin.top - margin.bottom;

    // Create SVG
    const g = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([1000, 3500])
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max([...pyinValues, ...meanValues, ...crepeValues, ...makamValues])])
      .range([height, 0]);

    // Add grid lines
    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisBottom(xScale)
        .tickSize(height)
        .tickFormat('')
        .tickValues([1000, 1500, 2000, 2500, 3000, 3500])
      );

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat('')
      );

    // Create line generator
    const line = d3.line()
      .x((d, i) => xScale(edges[i]))
      .y(d => yScale(d))
      .curve(d3.curveMonotoneX);

    // Add the lines in specific order (mean in back, others in front)
    if (meanValues.length > 0) {
      g.append('path')
        .datum(meanValues)
        .attr('class', 'line')
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', '#ffffff')  // white for mean
        .attr('stroke-width', 2)
        .attr('opacity', 0.7);
    }

    if (pyinValues.length > 0) {
      g.append('path')
        .datum(pyinValues)
        .attr('class', 'line')
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', '#ff4444')  // red for pyin
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.7);
    }

    if (crepeValues.length > 0) {
      g.append('path')
        .datum(crepeValues)
        .attr('class', 'line')
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', '#44ff44')  // green for crepe
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.7);
    }

    if (makamValues.length > 0) {
      g.append('path')
        .datum(makamValues)
        .attr('class', 'line')
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', '#4444ff')  // blue for makam
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.7);
    }

    // Add x-axis with cent values
    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickValues([1000, 1500, 2000, 2500, 3000, 3500])
        .tickFormat(d => d + '¢')
      );

    // Add note labels more frequently (every 100 cents instead of 200)
    const notePositions = d3.range(1000, 3501, 100);
    
    // Create a group for x-axis labels
    const xAxisLabels = g.append('g')
      .attr('class', 'x-axis-labels');

    // Add note name labels
    const noteLabels = xAxisLabels.append('g')
      .attr('class', 'note-labels')
      .attr('transform', `translate(0,${height + 25})`);

    noteLabels.selectAll('text')
      .data(notePositions)
      .enter()
      .append('text')
      .attr('x', d => xScale(d))
      .attr('y', 5)
      .attr('transform', d => `rotate(45, ${xScale(d)}, 5)`)
      .attr('text-anchor', 'start')
      .attr('fill', 'currentColor')
      .attr('class', d => d % 1200 === 0 ? 'note-label primary' : 'note-label secondary')
      .text(d => centsToNote(d));

    // Add keyboard key labels
    const keyLabels = xAxisLabels.append('g')
      .attr('class', 'key-labels')
      .attr('transform', `translate(0,${height + 45})`);

    keyLabels.selectAll('text')
      .data(notePositions)
      .enter()
      .append('text')
      .attr('x', d => xScale(d))
      .attr('y', 5)
      .attr('text-anchor', 'middle')
      .attr('fill', 'currentColor')
      .attr('class', 'key-label')
      .text(d => getKeyboardLabelForCents(d));

    // Add y-axis
    g.append('g')
      .attr('class', 'y-axis')
      .call(d3.axisLeft(yScale)
        .ticks(5)
      )
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -55)
      .attr('x', -height / 2)
      .attr('fill', 'currentColor')
      .style('text-anchor', 'middle')
      .text('Count');

    // Add legend
    const legend = g.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${width + 20}, 10)`);

    const methods = [
      { name: 'pYIN', color: '#ff4444' },
      { name: 'CREPE', color: '#44ff44' },
      { name: 'Makam', color: '#4444ff' },
      { name: 'Mean', color: '#ffffff' }
    ];

    methods.forEach((method, i) => {
      const legendItem = legend.append('g')
        .attr('transform', `translate(0, ${i * 20})`);

      legendItem.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 0)
        .attr('y2', 0)
        .attr('stroke', method.color)
        .attr('stroke-width', 2);

      legendItem.append('text')
        .attr('x', 25)
        .attr('y', 4)
        .attr('fill', 'currentColor')
        .style('font-size', '10px')
        .text(method.name);
    });

  }, [pitchData]);

  return (
    <div className="pitch-histogram" ref={containerRef}>
      <h3>Pitch Histogram</h3>
      <div className="histogram-svg-container">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
};

export default PitchHistogram; 