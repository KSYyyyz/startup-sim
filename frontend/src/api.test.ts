import { afterEach, describe, expect, test, vi } from 'vitest';

import { createSession, loadSuggestions, submitTurn } from './api';

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

  test('simulates a turn and suggestions in demo mode', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new Error('network down'))));

    const result = await submitTurn(1, '花10万研发产品');
    const suggestions = await loadSuggestions(1);

    expect(result.state.metrics.month).toBe(2);
    expect(result.state.board.length).toBeGreaterThan(0);
    expect(result.state.competitors.length).toBeGreaterThan(0);
    expect(suggestions.items.length).toBe(3);
  });
});
