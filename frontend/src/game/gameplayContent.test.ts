import { describe, expect, test } from 'vitest';

import {
  buildBoardPressureResponse,
  buildCompetitorPressureResponse,
  commandTradeoffs,
  gameContentManifest,
  quickActionShortcuts,
  gameplayRooms,
  officePulseRules,
  pressureResponseTemplates,
  resolveOfficePulse,
  resolveRoomStatuses
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
    expect(cfoResponse).toMatchObject({
      source: 'board',
      sourceLabel: 'CFO',
      title: '回应 CFO 压力',
      description: '现金压力明显，需要控制支出。',
      command: '花1万研发产品保持最低运转',
      tags: ['现金流可支撑时间 +', '增长 -']
    });

    const competitorResponse = buildCompetitorPressureResponse({
      name: '灵犀客服云',
      status: '升级企业功能',
      mrr: 41000,
      trend: 'up'
    });
    expect(competitorResponse).toMatchObject({
      source: 'competitor',
      sourceLabel: '灵犀客服云',
      title: '回应灵犀客服云压力',
      description: '升级企业功能',
      command: '花25万研发产品提升竞争力',
      tags: ['产品 ++', '现金 --']
    });

    expect(commandTradeoffs('融资300万出让8%股权')).toEqual(['现金 +', '股权 -']);
  });

  test('defines bottom-dock quick actions as reusable gameplay actions', () => {
    expect(quickActionShortcuts.map((action) => action.id)).toEqual(['research', 'hire', 'fundraise', 'marketing']);

    for (const action of quickActionShortcuts) {
      expect(action.title).toBeTruthy();
      expect(action.command).toMatch(/花|融资/);
      expect(action.tags).toEqual(commandTradeoffs(action.command));
      expect(action.iconKey).toMatch(/boxes|users|hand-coins|megaphone/);
    }
  });

  test('resolves office pulse signals from gameplay rules', () => {
    expect(officePulseRules.map((rule) => rule.roomId)).toEqual(['board', 'sales', 'servers']);

    expect(resolveOfficePulse({ title: '现金告急', description: '融资窗口收紧', insightTitle: '股权压力' })).toEqual({
      roomId: 'board',
      text: '现金压力'
    });
    expect(resolveOfficePulse({ title: '用户增长', description: '获客效率提升', insightTitle: '营销反馈' })).toEqual({
      roomId: 'sales',
      text: '增长压力'
    });
    expect(resolveOfficePulse({ title: '交付风险', description: '服务器稳定性下降', insightTitle: '客户投诉' })).toEqual({
      roomId: 'servers',
      text: '交付压力'
    });
    expect(resolveOfficePulse({ title: '早期打磨期', description: '继续验证需求', insightTitle: '产品仍在打磨期' })).toEqual({
      roomId: 'product',
      text: '产品压力'
    });
  });

  test('resolves data-driven room statuses from operating signals', () => {
    const statuses = resolveRoomStatuses({
      cashCoverageMonths: 2.4,
      productChange: 8,
      usersChange: 120,
      mrrChange: 5000,
      signalText: '服务器稳定性下降，交付风险升高'
    });

    expect(statuses.board).toEqual({ tone: 'warning', label: '现金紧张' });
    expect(statuses.product).toEqual({ tone: 'improving', label: '产品改善' });
    expect(statuses.sales).toEqual({ tone: 'opportunity', label: '增长机会' });
    expect(statuses.servers).toEqual({ tone: 'blocked', label: '交付阻塞' });
    expect(statuses.team).toEqual({ tone: 'normal', label: '运转中' });
  });
});
