#!/usr/bin/env node
// Mechanical TS-ification for FrameDebugAdapter.frm native bodies (Option A)
const fs = require('fs');
const path = require('path');

const file = path.resolve(__dirname, '..', 'src', 'debug', 'state_machines', 'FrameDebugAdapter.frm');
let src = fs.readFileSync(file, 'utf8');

// 1) Comment lines: '# ...' -> '// ...'
src = src.replace(/^(\s*)#(.*)$/gm, '$1//$2');

// 2) self -> this
src = src.replace(/\bself\./g, 'this.');

// 3) Python booleans/None -> TS
src = src.replace(/\bTrue\b/g, 'true');
src = src.replace(/\bFalse\b/g, 'false');
src = src.replace(/\bNone\b/g, 'null');

// 4) if not X { -> if (!(X)) {
src = src.replace(/(^\s*)if\s+not\s+([^\{\n]+)\{/gm, (m, pre, expr) => `${pre}if (!(${expr.trim()})) {`);

// 5) if expr { -> if (expr) {
// Avoid already-parenthesized or negated expressions
src = src.replace(/(^\s*)if\s+([^(!{\n][^\{\n]*)\{/gm, (m, pre, expr) => `${pre}if (${expr.trim()}) {`);

// 6) for x in xs { -> for (const x of xs) {
src = src.replace(/(^\s*)for\s+(\w+)\s+in\s+(\w+)\s*\{/gm, (m, pre, v, coll) => `${pre}for (const ${v} of ${coll}) {`);

// 7) Python list append -> JS push
src = src.replace(/\.append\(/g, '.push(');

// 8) f-strings: f"...{expr}..." and f'...{expr}...'
function convertFStrings(s) {
  // Double-quote f-strings
  s = s.replace(/f"([^"]*)"/g, (_, inner) => {
    const converted = inner.replace(/\{([^}]+)\}/g, '${$1}');
    return '`' + converted + '`';
  });
  // Single-quote f-strings
  s = s.replace(/f'([^']*)'/g, (_, inner) => {
    const converted = inner.replace(/\{([^}]+)\}/g, '${$1}');
    return '`' + converted + '`';
  });
  return s;
}
src = convertFStrings(src);

// 9) Ensure statements end with semicolons for common simple assignments/calls
// Add semicolons at end of lines that look like plain JS statements (heuristic)
src = src.replace(/^(\s*(this\.|frameRuntime|console|return\s+[^\{].*|var\s+[^;\n]+|const\s+[^;\n]+|let\s+[^;\n]+|\}\s*))$/gm, (m, line) => {
  // Skip lines that already end with ; or { or }
  if (/;\s*$/.test(line) || /\{\s*$/.test(line) || /\}\s*$/.test(line)) return line;
  return line + ';';
});

fs.writeFileSync(file, src, 'utf8');
console.log('Applied TS-ification transforms to', file);

