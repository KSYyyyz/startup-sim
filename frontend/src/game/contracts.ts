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

export type ActionPlanSource = 'room' | 'quick' | 'board' | 'competitor' | 'monthly';

export type ActionPlanInput = {
  id: string;
  source: ActionPlanSource;
  sourceLabel: string;
  title: string;
  command: string;
  description: string;
  tags: string[];
};

export type ActionPlan = {
  id: string;
  source: ActionPlanSource;
  sourceLabel: string;
  title: string;
  command: string;
  readableIntent: string;
  tradeoffs: string[];
  authority: 'backend-turn-engine';
};

export type TurnFactChange = {
  label: string;
  value: string;
  tone: string;
};

export type TurnFactsInput = {
  month: number;
  command: string;
  highlights: TurnFactChange[];
  reasons: string[];
  nextPressure: string;
};

export type TurnFacts = {
  month: number;
  command: string;
  changes: TurnFactChange[];
  replayBasis: string[];
  nextPressure: string;
  authority: 'backend-turn-engine';
};

export type RoleMemoryInput = {
  roleId: string;
  roleName: string;
  fact: string;
  implication: string;
};

export type RoleMemory = RoleMemoryInput & {
  source: 'settled-turn-facts';
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

export function toActionPlan(input: ActionPlanInput): ActionPlan {
  return {
    id: input.id,
    source: input.source,
    sourceLabel: input.sourceLabel,
    title: input.title,
    command: input.command,
    readableIntent: input.description,
    tradeoffs: input.tags,
    authority: 'backend-turn-engine'
  };
}

export function toTurnFacts(input: TurnFactsInput): TurnFacts {
  return {
    month: input.month,
    command: input.command,
    changes: input.highlights,
    replayBasis: input.reasons,
    nextPressure: input.nextPressure,
    authority: 'backend-turn-engine'
  };
}

export function toRoleMemory(input: RoleMemoryInput): RoleMemory {
  return {
    ...input,
    source: 'settled-turn-facts'
  };
}
