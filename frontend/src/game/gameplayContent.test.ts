import { describe, expect, test } from 'vitest';

import {
  buildBoardPressureResponse,
  buildBoardNpcProfiles,
  buildCompetitorPressureResponse,
  buildCompetitorMoves,
  buildCurrentMonthGoal,
  buildNewPlayerGuidance,
  buildPreparedActionPreview,
  buildMonthlyReport,
  buildMonthlyRecoveryAction,
  buildOfficeEventBubbles,
  buildTurnResolutionSteps,
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
      command: '花10万研发产品',
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
      factCitations: [
        { label: '执行指令', value: '花10万研发产品' },
        { label: '结算变化', value: '现金 $-22万 · 产品 +8 分 · 用户 +160' },
        { label: '复盘依据', value: '研发投入提升了产品分，但现金消耗上升。' }
      ],
      nextPressure: '研发有效，但现金消耗上升。',
      recoveryAction: {
        label: '下月补救',
        command: '花1万研发产品保持最低运转',
        description: '先压住现金消耗，再继续验证产品改进是否能转成增长。'
      }
    });
  });

  test('builds monthly recovery actions outside React UI', () => {
    const report = buildMonthlyReport({
      month: 3,
      highlights: [{ label: '现金', value: '$-22万', tone: 'bad' }],
      reasons: ['现金消耗上升。'],
      nextPressure: '需要收紧节奏。',
      command: '花10万研发产品',
      cashChange: -220000,
      productChange: 0,
      usersChange: 0
    });

    expect(buildMonthlyRecoveryAction(report, 3)).toMatchObject({
      id: 'monthly-3',
      source: 'monthly',
      sourceLabel: '月报行动',
      title: '下月止血',
      command: '花1万研发产品保持最低运转',
      impact: '现金流可支撑时间 + / 风险 -',
      tags: ['现金流可支撑时间 +', '增长 -']
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
      usersChange: 0,
      cashChange: -220000,
      lastCommand: '花10万研发产品'
    });

    expect(profiles).toEqual([
      {
        name: 'CFO',
        role: '财务负责人',
        message: '现金消耗上升。',
        confidence: 72,
        stance: '现金纪律',
        trustTrend: '信任承压',
        pressureTags: ['现金压力', '控制支出'],
        memoryFact: '记忆：上月现金减少，CFO 会继续盯预算。'
      },
      {
        name: 'CTO',
        role: '技术负责人',
        message: '产品体验改善。',
        confidence: 88,
        stance: '产品护城河',
        trustTrend: '信任上升',
        pressureTags: ['产品进展', '继续验证'],
        memoryFact: '记忆：上月产品有改善，CTO 更愿意支持继续验证。'
      }
    ]);
  });

  test('builds a unified read-only preview for prepared actions', () => {
    const preparedAction = buildBoardPressureResponse({
      name: 'CFO',
      role: '财务负责人',
      message: '现金压力明显，需要控制支出。'
    });

    const preview = buildPreparedActionPreview(preparedAction);

    expect(preview).toEqual({
      status: 'ready',
      summary: '已从 CFO 生成 1 个执行前预期。',
      guardrail: '这是执行前预期，数值结算仍由 TurnEngine 执行。',
      actions: [
        {
          type: 'prepared',
          label: '回应 CFO 压力',
          intent: '花1万研发产品保持最低运转',
          budget: 10000,
          budget_label: '1万',
          risk_label: '低风险',
          tradeoffs: ['现金流可支撑时间 +', '增长 -']
        }
      ]
    });
  });

  test('builds competitor moves from status and trend', () => {
    const moves = buildCompetitorMoves([
      { name: '灵犀客服云', status: '升级企业功能', mrr: 41000, trend: 'up' },
      { name: '快答科技', status: '本月暂无重大动作', mrr: 33000, trend: 'flat' }
    ]);

    expect(moves).toEqual([
      {
        name: '灵犀客服云',
        status: '升级企业功能',
        mrr: 41000,
        trend: 'up',
        moveType: '功能升级',
        reason: '正在强化产品能力，可能抢走重视功能完整度的客户。',
        responseCommand: '花25万研发产品提升竞争力'
      },
      {
        name: '快答科技',
        status: '本月暂无重大动作',
        mrr: 33000,
        trend: 'flat',
        moveType: '暂无大动作',
        reason: '市场窗口暂时平静，适合用小步试错积累优势。',
        responseCommand: '花10万做营销推广'
      }
    ]);
  });

  test('builds turn resolution steps from command highlights and report', () => {
    const steps = buildTurnResolutionSteps({
      command: '花10万研发产品',
      highlights: [
        { label: '现金', value: '$-22万', tone: 'bad' },
        { label: '产品', value: '+8 分', tone: 'good' }
      ],
      reportHeadline: '产品有进展，但现金在承压'
    });

    expect(steps).toEqual([
      { title: '执行指令', detail: '花10万研发产品', tone: 'neutral' },
      { title: '月末变化', detail: '现金 $-22万 · 产品 +8 分', tone: 'mixed' },
      { title: '战报复盘', detail: '产品有进展，但现金在承压', tone: 'focus' }
    ]);
  });

  test('builds first-three-month guidance without executable commands', () => {
    const monthOne = buildNewPlayerGuidance({
      month: 1,
      cashCoverageMonths: 8.3,
      productScore: 20,
      users: 0,
      mrr: 0,
      hasLastTurn: false
    });
    const monthTwo = buildNewPlayerGuidance({
      month: 2,
      cashCoverageMonths: 6.5,
      productScore: 32,
      users: 0,
      mrr: 0,
      hasLastTurn: true
    });

    expect(monthOne).toEqual({
      stepLabel: '第1步',
      title: '先读局面',
      description: '先看现金、产品和核心矛盾，再从办公室选一个小动作试水。',
      focusTags: ['现金流可支撑时间', '产品室', '小步试错'],
      checkHint: '本月只需要完成一次明确行动，别急着同时扩张和融资。'
    });
    expect(monthTwo?.title).toBe('读懂结算');
    expect(JSON.stringify(monthOne)).not.toContain('花10万研发产品');
    expect(JSON.stringify(monthOne)).not.toContain('一键');
    expect(buildNewPlayerGuidance({ month: 4, cashCoverageMonths: 5, productScore: 40, users: 100, mrr: 5000 })).toBeNull();
  });

  test('builds a current month goal as direction not command', () => {
    expect(
      buildCurrentMonthGoal({
        month: 1,
        cashCoverageMonths: 8.3,
        productScore: 20,
        users: 0,
        mrr: 0
      })
    ).toEqual({
      title: '本月小目标',
      statusLabel: '产品验证前',
      progressLabel: '产品 20/35',
      why: '产品还没到可验证区间，优先把核心体验补到能拿去见客户的程度。',
      directionTags: ['提升产品成熟度', '保持现金纪律', '准备客户验证'],
      riskHint: '不要把本月目标理解成固定指令；你仍然可以用任意 CEO 指令达成方向。'
    });

    const cashGoal = buildCurrentMonthGoal({
      month: 3,
      cashCoverageMonths: 2.8,
      productScore: 44,
      users: 120,
      mrr: 8000
    });
    expect(cashGoal.statusLabel).toBe('现金承压');
    expect(cashGoal.directionTags).toContain('压低单月消耗');
    expect(JSON.stringify(cashGoal)).not.toContain('花1万');
    expect(JSON.stringify(cashGoal)).not.toContain('融资300万');
  });
});
