/*
 * Canon F-789SGA Batch 4 regression checks.
 *
 * These are specification-level checks for the physical Base-n secondary
 * keys. They intentionally fail until the production keypad is wired to
 * the Base-n engine; this prevents us from claiming DEC/HEX/BIN/OCT works
 * when the current HTML still treats those keys as normal scientific keys.
 *
 * Manual reference: Canon F-789SGA (EXP)_EN, Base-n calculations and
 * logical calculations.  DEC/HEX/BIN/OCT select the active radix; scientific
 * functions are unavailable in Base-n mode.
 */

const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

// Physical secondary labels must remain present.
for (const label of ['DEC', 'HEX', 'BIN', 'OCT']) {
  assert(html.includes(`>${label}</span>`), `Missing physical secondary label: ${label}`);
}

// The current production mapping is deliberately detected here.  These
// assertions document the exact incorrect mappings that Batch 4 must fix.
assert(!html.includes('data-v="÷"><span class="sub g">DEC</span>'),
  'DEC is still wired as ordinary division instead of Base-n selection');
assert(!html.includes('data-action="sqrt"><span class="sub g">HEX</span>'),
  'HEX is still wired as square-root instead of Base-n selection');
assert(!html.includes('data-action="square"><span class="sub g">BIN</span>'),
  'BIN is still wired as square instead of Base-n selection');
assert(!html.includes('data-action="cube"><span class="sub g">OCT</span>'),
  'OCT is still wired as cube instead of Base-n selection');

console.log('Batch 4 Base-n keypad wiring: PASS');
