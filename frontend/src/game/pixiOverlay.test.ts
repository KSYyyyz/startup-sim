import { describe, expect, test } from 'vitest';

import { mountOfficePixiOverlay } from './pixiOverlay';

describe('office Pixi overlay boundary', () => {
  test('keeps the optional canvas layer inert during tests', () => {
    const container = document.createElement('div');
    const dispose = mountOfficePixiOverlay(container);

    expect(container.querySelector('canvas')).toBeNull();
    expect(() => dispose()).not.toThrow();
  });
});
