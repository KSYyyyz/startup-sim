import { describe, expect, test } from 'vitest';

import { gameplayContractManifest, isContractVersionCompatible, toActionPlan, toTurnFacts } from './contracts';

describe('engine-neutral gameplay contracts', () => {
  test('documents the shared contracts that connect frontend backend and future engines', () => {
    expect(gameplayContractManifest.version).toBe('alpha-0.4-contracts.0');
    expect(gameplayContractManifest.rulesAuthority).toBe('backend-turn-engine');
    expect(gameplayContractManifest.contracts.map((item) => item.name)).toEqual([
      'ActionPlan',
      'TurnFacts',
      'RoleMemory',
      'OfficeSignal',
      'ScenarioDefinition',
      'AssetManifest'
    ]);
    expect(gameplayContractManifest.engineTargets).toEqual(['web-react', 'tauri-desktop', 'unity-prototype']);
  });

  test('accepts compatible alpha contract versions only', () => {
    expect(isContractVersionCompatible('alpha-0.4-contracts.0')).toBe(true);
    expect(isContractVersionCompatible('alpha-0.4-contracts.3')).toBe(true);
    expect(isContractVersionCompatible('alpha-0.5-contracts.0')).toBe(false);
    expect(isContractVersionCompatible('legacy')).toBe(false);
  });

  test('converts prepared action inputs into engine-neutral action plans', () => {
    const plan = toActionPlan({
      id: 'quick-research',
      source: 'quick',
      sourceLabel: '快捷行动',
      title: '研发',
      command: '花10万研发产品',
      description: '投入产品打磨，提升核心体验。',
      tags: ['产品 +', '现金 -']
    });

    expect(plan).toEqual({
      id: 'quick-research',
      source: 'quick',
      sourceLabel: '快捷行动',
      title: '研发',
      command: '花10万研发产品',
      readableIntent: '投入产品打磨，提升核心体验。',
      tradeoffs: ['产品 +', '现金 -'],
      authority: 'backend-turn-engine'
    });
  });

  test('converts settled highlights and replay reasons into turn facts', () => {
    const facts = toTurnFacts({
      month: 3,
      command: '花10万研发产品',
      highlights: [
        { label: '现金', value: '$-22万', tone: 'bad' },
        { label: '产品', value: '+8 分', tone: 'good' }
      ],
      reasons: ['研发投入提升了产品分，但现金消耗上升。'],
      nextPressure: '继续验证产品改善是否能转化成增长。'
    });

    expect(facts).toEqual({
      month: 3,
      command: '花10万研发产品',
      changes: [
        { label: '现金', value: '$-22万', tone: 'bad' },
        { label: '产品', value: '+8 分', tone: 'good' }
      ],
      replayBasis: ['研发投入提升了产品分，但现金消耗上升。'],
      nextPressure: '继续验证产品改善是否能转化成增长。',
      authority: 'backend-turn-engine'
    });
  });
});
