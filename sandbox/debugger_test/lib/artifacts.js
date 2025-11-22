const fs = require('fs');

function extractTrailer(name, text) {
  const start = `/*#${name}#`;
  const end = `#${name}#*/`;
  const i = text.indexOf(start);
  const j = text.indexOf(end);
  if (i === -1 || j === -1 || j <= i) return null;
  const inner = text.slice(i + start.length, j).trim();
  try { return JSON.parse(inner); } catch { return null; }
}

function readAndExtract(filePath) {
  const txt = fs.readFileSync(filePath, 'utf8');
  return {
    errors: extractTrailer('errors-json', txt),
    frameMap: extractTrailer('frame-map', txt),
    visitorMap: extractTrailer('visitor-map', txt),
    debugManifest: extractTrailer('debug-manifest', txt),
  };
}

module.exports = { extractTrailer, readAndExtract };

