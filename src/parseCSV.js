import Papa from "papaparse";

const parseCSV = (csvFile, callback) => {
  Papa.parse(csvFile, {
    download: true,
    header: false, // Assumes no header row in the CSV
    complete: (results) => {
      const data = results.data
        .map(([timestamp, frequency]) => ({
          time: parseFloat(timestamp),
          frequency: parseFloat(frequency),
        }))
        .filter((row) => !isNaN(row.time) && !isNaN(row.frequency)); // Filter valid rows
      callback(data);
    },
    error: (error) => {
      console.error("Error parsing CSV:", error);
    },
  });
};

export default parseCSV;
