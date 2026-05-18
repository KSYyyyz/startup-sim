export type GameplayContractName =
  | 'ActionPlan'
  | 'TurnFacts'
  | 'RoleMemory'
  | 'OfficeSignal'
  | 'ScenarioDefinition'
  | 'AssetManifest';

export type GameplayContractManifest = {
  version: string;
  rulesAuthority: 'backend-turn-engine';
  engineTargets: Array<'web-react' | 'tauri-desktop' | 'unity-prototype'>;
  contracts: Array<{
    name: GameplayContractName;
    owner: 'backend-agent' | 'frontend-agent' | 'shared-contract';
    purpose: string;
  }>;
};

export const gameplayContractManifest: GameplayContractManifest = {
  version: 'alpha-0.4-contracts.0',
  rulesAuthority: 'backend-turn-engine',
  engineTargets: ['web-react', 'tauri-desktop', 'unity-prototype'],
  contracts: [
    {
      name: 'ActionPlan',
      owner: 'shared-contract',
      purpose: 'Describes a prepared player action before deterministic settlement.'
    },
    {
      name: 'TurnFacts',
      owner: 'backend-agent',
      purpose: 'Describes what actually happened after TurnEngine settlement.'
    },
    {
      name: 'RoleMemory',
      owner: 'backend-agent',
      purpose: 'Describes role memory derived from historical facts.'
    },
    {
      name: 'OfficeSignal',
      owner: 'shared-contract',
      purpose: 'Describes room-level visual signals without binding to React or Unity.'
    },
    {
      name: 'ScenarioDefinition',
      owner: 'shared-contract',
      purpose: 'Describes scenario rooms, roles, competitors, and market framing.'
    },
    {
      name: 'AssetManifest',
      owner: 'frontend-agent',
      purpose: 'Describes reusable image-2 assets and engine-safe references.'
    }
  ]
};

export function isContractVersionCompatible(version: string) {
  return /^alpha-0\.4-contracts\.\d+$/.test(version);
}
