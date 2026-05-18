import { describe, expect, test } from 'vitest';

import { gameplayContractManifest, isContractVersionCompatible, toActionPlan } from './contracts';

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
});
