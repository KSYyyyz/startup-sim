import { describe, expect, test } from 'vitest';

import { manualChunks } from './buildChunks';

describe('frontend build chunking', () => {
  test('keeps PixiJS in a named optional overlay chunk', () => {
    expect(manualChunks).toBeTypeOf('function');
    expect(manualChunks('D:/Startup-sim/frontend/node_modules/pixi.js/dist/pixi.mjs')).toBe('pixi-overlay');
    expect(manualChunks('D:/Startup-sim/frontend/node_modules/@pixi/core/index.mjs')).toBe('pixi-overlay');
    expect(manualChunks('D:/Startup-sim/frontend/src/App.tsx')).toBeUndefined();
  });
});
