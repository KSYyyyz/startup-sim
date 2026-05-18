import { describe, expect, test } from 'vitest';

import { aiSaasSeedScenario, builtinScenarios } from './scenarios';

describe('scenario metadata', () => {
  test('defines the AI SaaS seed scenario without owning settlement rules', () => {
    expect(aiSaasSeedScenario).toMatchObject({
      id: 'ai-saas-seed',
      name: 'AI SaaS 初创公司',
      version: 'alpha-0.2',
      startingCompany: {
        displayName: 'NimbusAI',
        cashLabel: '100万启动现金'
      },
      contentPack: {
        type: 'builtin',
        allowsModsLater: true
      }
    });
    expect(aiSaasSeedScenario.rooms.map((room) => room.id)).toEqual([
      'product',
      'team',
      'sales',
      'board',
      'servers'
    ]);
    expect(aiSaasSeedScenario.boardRoles.map((role) => role.stance)).toContain('现金纪律');
    expect(aiSaasSeedScenario.competitors).toHaveLength(3);
    expect(aiSaasSeedScenario.rulesAuthority).toBe('backend-turn-engine');
  });

  test('exposes builtin scenarios as a reusable catalog', () => {
    expect(builtinScenarios).toEqual([aiSaasSeedScenario]);
  });
});
