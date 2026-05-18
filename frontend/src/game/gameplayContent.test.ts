import { describe, expect, test } from 'vitest';

import {
  buildBoardPressureResponse,
  buildBoardNpcProfiles,
  buildCompetitorPressureResponse,
  buildMonthlyReport,
  buildOfficeEventBubbles,
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

  test('builds office event bubbles from board competitor and insight facts', () => {
    const events = buildOfficeEventBubbles({
      boardName: 'CFO',
      boardMessage: '控制固定支出。',
      competitorName: '快答科技',
      competitorStatus: '升级企业功能',
      insightTitle: '产品仍在打磨期',
      insightDescription: '先用小预算验证客户需求。'
    });

    expect(events).toEqual([
      {
        id: 'board-signal',
        roomId: 'board',
        tone: 'board',
        title: 'CFO',
        description: '控制固定支出。',
        action: 'board'
      },
      {
        id: 'competitor-signal',
        roomId: 'sales',
        tone: 'competitor',
        title: '快答科技',
        description: '升级企业功能',
        action: 'competitor'
      },
      {
        id: 'insight-signal',
        roomId: 'product',
        tone: 'insight',
        title: '产品仍在打磨期',
        description: '先用小预算验证客户需求。',
        action: 'none'
      }
    ]);
  });

  test('builds a game-like monthly report with recovery action', () => {
    const report = buildMonthlyReport({
      month: 3,
      highlights: [
        { label: '现金', value: '$-22万', tone: 'bad' },
        { label: '产品', value: '+8 分', tone: 'good' },
        { label: '用户', value: '+160', tone: 'good' }
      ],
      reasons: ['研发投入提升了产品分，但现金消耗上升。'],
      nextPressure: '研发有效，但现金消耗上升。',
      cashChange: -220000,
      productChange: 8,
      usersChange: 160
    });

    expect(report).toEqual({
      title: '第3月执行结果',
      headline: '产品有进展，但现金在承压',
      highlightCards: [
        { label: '现金', value: '$-22万', tone: 'bad' },
        { label: '产品', value: '+8 分', tone: 'good' },
        { label: '用户', value: '+160', tone: 'good' }
      ],
      reviewLines: ['研发投入提升了产品分，但现金消耗上升。'],
      nextPressure: '研发有效，但现金消耗上升。',
      recoveryAction: {
        label: '下月补救',
        command: '花1万研发产品保持最低运转',
        description: '先压住现金消耗，再继续验证产品改进是否能转成增长。'
      }
    });
  });

  test('builds board NPC profiles from member roles and current pressure', () => {
    const profiles = buildBoardNpcProfiles({
      members: [
        { name: 'CFO', role: '财务负责人', message: '现金消耗上升。', confidence: 72 },
        { name: 'CTO', role: '技术负责人', message: '产品体验改善。', confidence: 88 }
      ],
      cashCoverageMonths: 2.4,
      productChange: 8,
      usersChange: 0
    });

    expect(profiles).toEqual([
      {
        name: 'CFO',
        role: '财务负责人',
        message: '现金消耗上升。',
        confidence: 72,
        stance: '现金纪律',
        trustTrend: '信任承压',
        pressureTags: ['现金压力', '控制支出']
      },
      {
        name: 'CTO',
        role: '技术负责人',
        message: '产品体验改善。',
        confidence: 88,
        stance: '产品护城河',
        trustTrend: '信任上升',
        pressureTags: ['产品进展', '继续验证']
      }
    ]);
  });
});
