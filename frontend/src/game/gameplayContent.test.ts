import { describe, expect, test } from 'vitest';

import { gameContentManifest, gameplayRooms } from './gameplayContent';

describe('gameplay content definitions', () => {
  test('keeps room action content data-driven and UI independent', () => {
    expect(gameContentManifest.version).toBe('alpha-0.2');
    expect(gameContentManifest.sources).toContain('docs/reference_game_analysis.md');

    expect(gameplayRooms.map((room) => room.id)).toEqual(['product', 'team', 'sales', 'board', 'servers']);

    for (const room of gameplayRooms) {
      expect(room.name).toBeTruthy();
      expect(room.tone).toBeTruthy();
      expect(room.position.x).toBeGreaterThanOrEqual(0);
      expect(room.position.x).toBeLessThanOrEqual(100);
      expect(room.position.y).toBeGreaterThanOrEqual(0);
      expect(room.position.y).toBeLessThanOrEqual(100);
      expect(room.actions.length).toBeGreaterThan(0);
      expect(room).not.toHaveProperty('icon');

      for (const action of room.actions) {
        expect(action.command).toMatch(/花|融资/);
        expect(action.tags.length).toBeGreaterThan(0);
      }
    }
  });
});
