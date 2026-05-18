import { describe, expect, test } from 'vitest';

import {
  buildBoardPressureResponse,
  buildCompetitorPressureResponse,
  commandTradeoffs,
  gameContentManifest,
  gameplayRooms,
  pressureResponseTemplates
} from './gameplayContent';

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

  test('builds board and competitor pressure responses from data templates', () => {
    expect(pressureResponseTemplates.board.length).toBeGreaterThanOrEqual(4);
    expect(pressureResponseTemplates.competitor.length).toBeGreaterThanOrEqual(4);

    const cfoResponse = buildBoardPressureResponse({
      name: 'CFO',
      role: '财务负责人',
      message: '现金压力明显，需要控制支出。'
    });
    expect(cfoResponse).toEqual({
      command: '花1万研发产品保持最低运转',
      tradeoffs: ['现金流可支撑时间 +', '增长 -']
    });

    const competitorResponse = buildCompetitorPressureResponse({
      name: '灵犀客服云',
      status: '升级企业功能',
      mrr: 41000,
      trend: 'up'
    });
    expect(competitorResponse).toEqual({
      command: '花25万研发产品提升竞争力',
      tradeoffs: ['产品 ++', '现金 --']
    });

    expect(commandTradeoffs('融资300万出让8%股权')).toEqual(['现金 +', '股权 -']);
  });
});
