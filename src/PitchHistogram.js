import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import './PitchHistogram.css';

// Function to convert cents to note name
const centsToNote = (cents) => {
  const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const semitones = Math.round(cents / 100);
  const octave = Math.floor(semitones / 12) + 4;
  const noteIndex = ((semitones % 12) + 12) % 12;
  return noteNames[noteIndex] + octave;
};

// Function to get note label with cents
const getNoteLabel = (cents) => {
  if (cents % 100 === 0) {
    return centsToNote(cents);
  }
  return ''; // Only show labels for whole semitones
};

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
    const values = Array.from(pitchData.pitch_hist_values);
    const edges = Array.from(pitchData.pitch_hist_edges);

    console.log('Histogram data:', { values, edges });

    // Clear previous content
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Get container width
    const containerWidth = containerRef.current.clientWidth;
    
    // Set up dimensions with extra space for labels
    const margin = { top: 20, right: 20, bottom: 60, left: 50 };
    const width = Math.min(800, containerWidth - margin.left - margin.right);
    const height = 250 - margin.top - margin.bottom;

    // Create SVG
    const g = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Filter data for the range 500-2400
    const filteredData = values.filter((_, i) => edges[i] >= 500 && edges[i] <= 2400);
    const filteredEdges = edges.filter(edge => edge >= 500 && edge <= 2400);

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([500, 2400])  // Fixed range from 500 to 2400 cents
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(filteredData)])
      .range([height, 0]);

    // Add grid lines
    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisBottom(xScale)
        .tickSize(height)
        .tickFormat('')
        .ticks(15)
      );

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat('')
      );

    // Create and add the bars
    g.selectAll('rect')
      .data(filteredData)
      .enter()
      .append('rect')
      .attr('x', (d, i) => xScale(filteredEdges[i]))
      .attr('y', d => yScale(d))
      .attr('width', (d, i) => {
        const nextEdge = filteredEdges[i + 1] || filteredEdges[i] + (filteredEdges[1] - filteredEdges[0]);
        return Math.max(0, xScale(nextEdge) - xScale(filteredEdges[i]) - 1);
      })
      .attr('height', d => height - yScale(d))
      .attr('fill', '#3498db')
      .attr('opacity', 0.7);

    // Create axes
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d => `${d}`)
      .ticks(15);
    
    const yAxis = d3.axisLeft(yScale)
      .ticks(5);

    // Add axes
    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis);

    // Add note labels with more space from x-axis
    const noteLabels = g.append('g')
      .attr('class', 'note-labels')
      .attr('transform', `translate(0,${height + 35})`);  // Increased from 25 to 35

    // Add note labels every 100 cents within the 500-2400 range
    const notePositions = filteredEdges.filter(e => e % 100 === 0);
    noteLabels.selectAll('text')
      .data(notePositions)
      .enter()
      .append('text')
      .attr('x', d => xScale(d))
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .attr('fill', 'currentColor')
      .attr('class', 'note-label primary')
      .text(centsToNote);

    // Add y-axis
    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis)
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -55)
      .attr('x', -height / 2)
      .attr('fill', 'currentColor')
      .style('text-anchor', 'middle')
      .text('Count');

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