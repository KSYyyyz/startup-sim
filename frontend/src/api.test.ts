import { afterEach, describe, expect, test, vi } from 'vitest';

import { createSession, loadReview, loadSuggestions, previewCommand, submitTurn } from './api';

describe('Vercel demo fallback', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test('starts a playable demo when the backend API is unavailable', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('not found', { status: 404 })));

    const state = await createSession();

    expect(state.stage.company_name).toBe('NimbusAI');
    expect(state.metrics.cash_coverage_label).toBe('现金流可支撑时间');
  });

  test('uses demo mode directly on deployed static frontend without calling missing API routes', async () => {
    const fetchMock = vi.fn(async () => new Response('method not allowed', { status: 405 }));
    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('location', { hostname: 'startup-sim-khaki.vercel.app' });

    const state = await createSession();
    const preview = await previewCommand(1, '花10万研发产品，花5万做营销');
    const result = await submitTurn(1, '花10万研发产品');

    expect(fetchMock).not.toHaveBeenCalled();
    expect(state.stage.company_name).toBe('NimbusAI');
    expect(preview.summary).toBe('系统将这条 CEO 指令理解为 2 个可执行动作。');
    expect(result.state.metrics.month).toBe(2);
  });

  test('keeps phase goals and objective progress in deployed static demo mode', async () => {
    const fetchMock = vi.fn(async () => new Response('method not allowed', { status: 405 }));
    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('location', { hostname: 'startup-sim-khaki.vercel.app' });

    const state = await createSession();
    const result = await submitTurn(1, '花10万研发产品');

    expect(fetchMock).not.toHaveBeenCalled();
    expect(state.phase_goals?.title).toBe('早期生存目标');
    expect(state.phase_goals?.objectives[0].action_directions).toContain('研发投入');
    expect(JSON.stringify(state.phase_goals)).not.toContain('花10万研发产品');
    expect(JSON.stringify(state.phase_goals)).not.toContain('一键');
    expect(result.turn.objective_updates?.[0]).toMatchObject({
      id: 'product-readiness',
      title: '提升产品成熟度'
    });
    expect(JSON.stringify(result.turn.objective_updates)).not.toContain('花10万研发产品');
  });

  test('simulates a turn and suggestions in demo mode', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new Error('network down'))));

    const result = await submitTurn(1, '花10万研发产品');
    const suggestions = await loadSuggestions(1);

    expect(result.state.metrics.month).toBe(2);
    expect(result.state.board.length).toBeGreaterThan(0);
    expect(result.state.competitors.length).toBeGreaterThan(0);
    expect(suggestions.items.length).toBe(3);
  });

  test('preserves optional settled gameplay facts on turn responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(
            JSON.stringify({
              state: { metrics: { month: 2 } },
              turn: { month: 1, delta_reasons: ['旧版复盘原因'] },
              turn_facts: {
                month: 1,
                command: '花10万研发产品',
                changes: [{ label: '产品', value: '+12 分', tone: 'good' }],
                replay_basis: ['TurnFacts 复盘依据'],
                next_pressure: 'TurnFacts 下月压力'
              },
              recent_role_memory: [
                {
                  role_id: 'cfo',
                  role_name: 'CFO',
                  fact: '上月现金消耗来自研发投入。',
                  implication: 'CFO 会优先追问预算纪律。'
                }
              ],
              memory_history: [
                {
                  role_id: 'cto',
                  role_name: 'CTO',
                  fact: '产品改善来自研发投入。',
                  implication: 'CTO 会支持继续验证。'
                }
              ],
              office_signals: [
                {
                  id: 'cash-watch',
                  room_id: 'board',
                  title: '预算审查',
                  description: '董事会要求解释现金消耗。',
                  severity: 'warning',
                  source: 'role-memory',
                  visual_intent: 'surface-in-office'
                }
              ],
              story_events: [
                {
                  id: 'demo-event',
                  title: '产品冲刺',
                  description: '研发投入带来可见产品改善。',
                  tone: 'good',
                  source: 'rule-event'
                }
              ]
            }),
            { status: 200 }
          )
      )
    );

    const result = await submitTurn(1, '花10万研发产品');

    expect(result.turn_facts?.replay_basis).toEqual(['TurnFacts 复盘依据']);
    expect(result.turn_facts?.changes[0]).toEqual({ label: '产品', value: '+12 分', tone: 'good' });
    expect(result.turn_facts?.next_pressure).toBe('TurnFacts 下月压力');
    expect(result.recent_role_memory?.[0].fact).toBe('上月现金消耗来自研发投入。');
    expect(result.memory_history?.[0].role_name).toBe('CTO');
    expect(result.office_signals?.[0].room_id).toBe('board');
    expect(result.story_events?.[0].title).toBe('产品冲刺');
  });

  test('loads optional game review when the backend endpoint exists', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(
            JSON.stringify({
              ending_status: 'survived_but_average',
              ending_title: '本局复盘',
              ending_summary: '产品推进有效，但现金压力上升。',
              advice_for_next_run: '下局先设预算上限。',
              key_moments: [{ title: '研发冲刺', description: '产品分显著提升。' }],
              achievement_cards: [{ title: '产品主义者', description: '产品分提升明显。', rarity: 'silver' }],
              next_run_suggestions: ['先设预算上限', '把营销放在产品验证之后'],
              archive_summary: '档案摘要：研发路线留下清晰记录。',
              archive_timeline: [{ title: '第1月 研发冲刺', description: '产品分显著提升。' }],
              archive_badges: [{ title: '产品主义者', description: '产品分提升明显。', rarity: 'silver' }]
            }),
            { status: 200 }
          )
      )
    );

    const review = await loadReview(1);

    expect(review?.ending_title).toBe('本局复盘');
    expect(review?.key_moments?.[0].title).toBe('研发冲刺');
    expect(review?.achievement_cards?.[0].title).toBe('产品主义者');
    expect(review?.next_run_suggestions).toEqual(['先设预算上限', '把营销放在产品验证之后']);
    expect(review?.archive_summary).toBe('档案摘要：研发路线留下清晰记录。');
    expect(review?.archive_timeline?.[0].title).toBe('第1月 研发冲刺');
    expect(review?.archive_badges?.[0].title).toBe('产品主义者');
  });

  test('treats a missing review endpoint as optional', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ message: 'not found' }), { status: 404 })));

    await expect(loadReview(1)).resolves.toBeNull();
  });

  test('previews multi-action demo commands with segment budgets', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new Error('network down'))));

    const preview = await previewCommand(1, '花10万研发产品，花5万做营销');

    expect(preview.actions).toHaveLength(2);
    expect(preview.actions[0]).toMatchObject({
      label: '产品研发',
      intent: '花10万研发产品',
      budget: 100000,
      budget_label: '10万'
    });
    expect(preview.actions[1]).toMatchObject({
      label: '市场营销',
      intent: '花5万做营销',
      budget: 50000,
      budget_label: '5万'
    });
  });
});
