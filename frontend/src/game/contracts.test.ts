import { describe, expect, test } from 'vitest';

import { gameplayContractManifest, isContractVersionCompatible } from './contracts';

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
});
