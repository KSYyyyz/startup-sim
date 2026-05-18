export type GameplayActionDefinition = {
  title: string;
  description: string;
  command: string;
  impact: string;
  tags: string[];
};

export type QuickActionShortcut = GameplayActionDefinition & {
  id: string;
  iconKey: 'boxes' | 'users' | 'hand-coins' | 'megaphone';
};

export type PreparedAction = GameplayActionDefinition & {
  id: string;
  source: 'room' | 'quick' | 'board' | 'competitor';
  sourceLabel: string;
};

export type GameplayRoomDefinition = {
  id: string;
  name: string;
  tone: string;
  position: {
    x: number;
    y: number;
  };
  actions: GameplayActionDefinition[];
};

export type BoardPressureInput = {
  name: string;
  role: string;
  message: string;
};

export type CompetitorPressureInput = {
  name: string;
  status: string;
  mrr?: number;
  trend: string;
};

export type PressureResponseTemplate = {
  id: string;
  pattern: RegExp;
  command: string;
};

export type PressureResponsePlan = PreparedAction;

export type OfficePulseInput = {
  title: string;
  description: string;
  insightTitle: string;
};

export type OfficePulseRule = {
  id: string;
  pattern: RegExp;
  roomId: string;
  text: string;
};

export type OfficePulseSignal = {
  roomId: string;
  text: string;
};

export type RoomStatusTone = 'normal' | 'warning' | 'improving' | 'blocked' | 'opportunity';

export type RoomStatus = {
  tone: RoomStatusTone;
  label: string;
};

export type RoomStatusInput = {
  cashCoverageMonths: number;
  productChange: number;
  usersChange: number;
  mrrChange: number;
  signalText: string;
};

export type OfficeEventInput = {
  boardName: string;
  boardMessage: string;
  competitorName: string;
  competitorStatus: string;
  insightTitle: string;
  insightDescription: string;
};

export type OfficeEventBubble = {
  id: string;
  roomId: string;
  tone: 'board' | 'competitor' | 'insight';
  title: string;
  description: string;
  action: 'board' | 'competitor' | 'none';
};

export type MonthlyReportHighlight = {
  label: string;
  value: string;
  tone: string;
};

export type MonthlyReportInput = {
  month: number;
  highlights: MonthlyReportHighlight[];
  reasons?: string[];
  nextPressure: string;
  cashChange: number;
  productChange: number;
  usersChange: number;
};

export type MonthlyReport = {
  title: string;
  headline: string;
  highlightCards: MonthlyReportHighlight[];
  reviewLines: string[];
  nextPressure: string;
  recoveryAction: {
    label: string;
    command: string;
    description: string;
  };
};

export const gameContentManifest = {
  version: 'alpha-0.2',
  sources: ['docs/reference_game_analysis.md', 'docs/frontend_alpha_0_2_desktop_game_layer.md']
} as const;

export const gameplayRooms: GameplayRoomDefinition[] = [
  {
    id: 'product',
    name: '产品室',
    tone: 'product',
    position: { x: 48, y: 18 },
    actions: [
      {
        title: '产品打磨',
        description: '现金消耗中等，产品体验提升。',
        command: '花10万研发产品',
        impact: '适合早期补齐核心体验，降低技术孤岛风险。',
        tags: ['产品 +', '现金 -']
      },
      {
        title: '研发冲刺',
        description: '现金消耗较高，产品提升更快。',
        command: '花25万研发产品提升竞争力',
        impact: '适合抢窗口，但会缩短现金流可支撑时间。',
        tags: ['产品 ++', '现金 --']
      }
    ]
  },
  {
    id: 'team',
    name: '研发团队',
    tone: 'team',
    position: { x: 25, y: 23 },
    actions: [
      {
        title: '招聘人才',
        description: '固定支出上升，团队产能提升。',
        command: '花8万招聘人才',
        impact: '适合产品和交付都开始吃紧的时候。',
        tags: ['团队 +', '固定支出 +']
      }
    ]
  },
  {
    id: 'sales',
    name: '销售区',
    tone: 'sales',
    position: { x: 53, y: 66 },
    actions: [
      {
        title: '增长投放',
        description: '获客变快，但需要产品承接。',
        command: '花10万做营销推广',
        impact: '适合产品已有基本体验后扩大市场信号。',
        tags: ['用户 +', '现金 -']
      }
    ]
  },
  {
    id: 'board',
    name: '董事会',
    tone: 'board',
    position: { x: 73, y: 32 },
    actions: [
      {
        title: '融资沟通',
        description: '补充现金，但会稀释股权。',
        command: '融资300万出让8%股权',
        impact: '适合现金流紧张或准备加速扩张时。',
        tags: ['现金 +', '股权 -']
      }
    ]
  },
  {
    id: 'servers',
    name: '服务器',
    tone: 'server',
    position: { x: 77, y: 65 },
    actions: [
      {
        title: '稳定性投入',
        description: '短期不拉增长，但减少交付风险。',
        command: '花6万优化服务器稳定性',
        impact: '适合用户增长后控制故障和口碑损失。',
        tags: ['稳定性 +', '现金 -']
      }
    ]
  }
];

export const quickActionShortcuts: QuickActionShortcut[] = [
  {
    id: 'research',
    iconKey: 'boxes',
    title: '研发',
    description: '投入产品打磨，提升核心体验。',
    command: '花10万研发产品',
    impact: '适合早期把产品体验补到可验证水平。',
    tags: commandTradeoffs('花10万研发产品')
  },
  {
    id: 'hire',
    iconKey: 'users',
    title: '招聘',
    description: '补充团队产能，但固定支出会上升。',
    command: '花8万招聘人才',
    impact: '适合产品和交付都开始吃紧的时候。',
    tags: commandTradeoffs('花8万招聘人才')
  },
  {
    id: 'fundraise',
    iconKey: 'hand-coins',
    title: '融资',
    description: '补充现金，同时稀释创始人股权。',
    command: '融资300万出让8%股权',
    impact: '适合现金流紧张或准备加速扩张时。',
    tags: commandTradeoffs('融资300万出让8%股权')
  },
  {
    id: 'marketing',
    iconKey: 'megaphone',
    title: '营销',
    description: '扩大获客和市场信号，但消耗现金。',
    command: '花10万做营销推广',
    impact: '适合产品已有基本体验后扩大增长。',
    tags: commandTradeoffs('花10万做营销推广')
  }
];

export const pressureResponseTemplates = {
  board: [
    {
      id: 'board-cash-discipline',
      pattern: /CFO|财务|现金|支出/,
      command: '花1万研发产品保持最低运转'
    },
    {
      id: 'board-product-moat',
      pattern: /CTO|技术|产品/,
      command: '花10万研发产品'
    },
    {
      id: 'board-delivery-quality',
      pattern: /COO|运营|交付|团队/,
      command: '花5万招聘人才'
    },
    {
      id: 'board-growth-efficiency',
      pattern: /增长|Growth|用户|获客/,
      command: '花10万做营销推广'
    }
  ],
  competitor: [
    {
      id: 'competitor-enterprise-feature',
      pattern: /企业|功能|产品|升级/,
      command: '花25万研发产品提升竞争力'
    },
    {
      id: 'competitor-reliability',
      pattern: /服务器|稳定|故障|交付/,
      command: '花6万优化服务器稳定性'
    },
    {
      id: 'competitor-market-up',
      pattern: /trend:up/,
      command: '花10万做营销推广'
    },
    {
      id: 'competitor-market-down',
      pattern: /trend:down/,
      command: '花10万研发产品'
    }
  ]
} satisfies Record<'board' | 'competitor', PressureResponseTemplate[]>;

export const officePulseRules: OfficePulseRule[] = [
  {
    id: 'cash-pressure',
    pattern: /现金|融资|股权/,
    roomId: 'board',
    text: '现金压力'
  },
  {
    id: 'growth-pressure',
    pattern: /用户|增长|营销|获客/,
    roomId: 'sales',
    text: '增长压力'
  },
  {
    id: 'delivery-pressure',
    pattern: /服务器|稳定|交付/,
    roomId: 'servers',
    text: '交付压力'
  }
];

export function commandTradeoffs(value: string) {
  if (/保持最低运转/.test(value)) return ['现金流可支撑时间 +', '增长 -'];
  if (/融资/.test(value)) return ['现金 +', '股权 -'];
  if (/招聘/.test(value)) return ['团队 +', '固定支出 +'];
  if (/营销/.test(value)) return ['用户 +', '现金 -'];
  if (/服务器|稳定/.test(value)) return ['稳定性 +', '现金 -'];
  if (/25万|提升竞争力/.test(value)) return ['产品 ++', '现金 --'];
  return ['产品 +', '现金 -'];
}

function responseFromTemplates(templates: PressureResponseTemplate[], signal: string, fallbackCommand: string) {
  const command = templates.find((template) => template.pattern.test(signal))?.command ?? fallbackCommand;
  return {
    command,
    tradeoffs: commandTradeoffs(command)
  };
}

export function prepareAction(
  action: GameplayActionDefinition,
  options: {
    id: string;
    source: PreparedAction['source'];
    sourceLabel: string;
  }
): PreparedAction {
  return {
    ...action,
    id: options.id,
    source: options.source,
    sourceLabel: options.sourceLabel
  };
}

export function buildBoardPressureResponse(member: BoardPressureInput): PressureResponsePlan {
  const signal = `${member.name} ${member.role} ${member.message}`;
  const response = responseFromTemplates(pressureResponseTemplates.board, signal, '花10万研发产品');
  return prepareAction(
    {
      title: `回应 ${member.name} 压力`,
      description: member.message,
      command: response.command,
      impact: '根据董事会压力生成的 CEO 回应。',
      tags: response.tradeoffs
    },
    {
      id: `board-${member.name}`,
      source: 'board',
      sourceLabel: member.name
    }
  );
}

export function buildCompetitorPressureResponse(item: CompetitorPressureInput): PressureResponsePlan {
  const signal = `${item.name} ${item.status} trend:${item.trend}`;
  const response = responseFromTemplates(pressureResponseTemplates.competitor, signal, '花10万做营销推广');
  return prepareAction(
    {
      title: `回应${item.name}压力`,
      description: item.status,
      command: response.command,
      impact: '根据竞品态势生成的 CEO 回应。',
      tags: response.tradeoffs
    },
    {
      id: `competitor-${item.name}`,
      source: 'competitor',
      sourceLabel: item.name
    }
  );
}

export function resolveOfficePulse(input: OfficePulseInput): OfficePulseSignal {
  const signal = `${input.title} ${input.description} ${input.insightTitle}`;
  const rule = officePulseRules.find((item) => item.pattern.test(signal));
  return rule ? { roomId: rule.roomId, text: rule.text } : { roomId: 'product', text: '产品压力' };
}

export function resolveRoomStatuses(input: RoomStatusInput): Record<string, RoomStatus> {
  const statuses: Record<string, RoomStatus> = {
    product: { tone: 'normal', label: '运转中' },
    team: { tone: 'normal', label: '运转中' },
    sales: { tone: 'normal', label: '运转中' },
    board: { tone: 'normal', label: '运转中' },
    servers: { tone: 'normal', label: '运转中' }
  };

  if (input.cashCoverageMonths < 3) {
    statuses.board = { tone: 'warning', label: '现金紧张' };
  }
  if (input.productChange > 0) {
    statuses.product = { tone: 'improving', label: '产品改善' };
  }
  if (input.usersChange > 0 || input.mrrChange > 0) {
    statuses.sales = { tone: 'opportunity', label: '增长机会' };
  }
  if (/服务器|稳定|交付|故障/.test(input.signalText)) {
    statuses.servers = { tone: 'blocked', label: '交付阻塞' };
  }
  if (/团队|招聘|士气/.test(input.signalText)) {
    statuses.team = { tone: 'warning', label: '团队吃紧' };
  }

  return statuses;
}

export function buildOfficeEventBubbles(input: OfficeEventInput): OfficeEventBubble[] {
  return [
    {
      id: 'board-signal',
      roomId: 'board',
      tone: 'board',
      title: input.boardName,
      description: input.boardMessage,
      action: 'board'
    },
    {
      id: 'competitor-signal',
      roomId: 'sales',
      tone: 'competitor',
      title: input.competitorName,
      description: input.competitorStatus,
      action: 'competitor'
    },
    {
      id: 'insight-signal',
      roomId: 'product',
      tone: 'insight',
      title: input.insightTitle,
      description: input.insightDescription,
      action: 'none'
    }
  ];
}

export function buildMonthlyReport(input: MonthlyReportInput): MonthlyReport {
  const reviewLines =
    input.reasons && input.reasons.length
      ? input.reasons.slice(0, 3)
      : ['本回合已结算，董事会、竞品态势和经营洞察已更新。'];

  let headline = '公司继续向前推进';
  let recoveryAction = {
    label: '下月行动',
    command: '花10万研发产品',
    description: '保持小步试错，用一个明确行动继续推进核心矛盾。'
  };

  if (input.cashChange < 0 && input.productChange > 0) {
    headline = '产品有进展，但现金在承压';
    recoveryAction = {
      label: '下月补救',
      command: '花1万研发产品保持最低运转',
      description: '先压住现金消耗，再继续验证产品改进是否能转成增长。'
    };
  } else if (input.usersChange > 0) {
    headline = '增长开始出现，但要验证质量';
    recoveryAction = {
      label: '下月追击',
      command: '花10万做营销推广',
      description: '把新增用户转成可复用增长经验，避免只买到短期流量。'
    };
  } else if (input.cashChange < 0) {
    headline = '现金消耗上升，需要收紧节奏';
    recoveryAction = {
      label: '下月止血',
      command: '花1万研发产品保持最低运转',
      description: '优先延长现金流可支撑时间，再寻找更确定的增长机会。'
    };
  }

  return {
    title: `第${input.month}月执行结果`,
    headline,
    highlightCards: input.highlights,
    reviewLines,
    nextPressure: input.nextPressure,
    recoveryAction
  };
}
