import { afterEach, describe, expect, test, vi } from 'vitest';

import { createSession, loadSuggestions, previewCommand, submitTurn } from './api';

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
              role_memory: [
                {
                  role_id: 'cfo',
                  role_name: 'CFO',
                  fact: '上月现金消耗来自研发投入。',
                  implication: 'CFO 会优先追问预算纪律。'
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
    expect(result.role_memory?.[0].fact).toBe('上月现金消耗来自研发投入。');
    expect(result.office_signals?.[0].room_id).toBe('board');
    expect(result.story_events?.[0].title).toBe('产品冲刺');
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
