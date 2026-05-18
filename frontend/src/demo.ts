import type { CommandPreviewResponse, GameStateView, SuggestionResponse, TurnResponse } from './types';

export const demoInitialState: GameStateView = {
  session_id: 1,
  status: 'demo',
  metrics: {
    month: 1,
    cash: 1000000,
    cash_change: 0,
    cash_coverage_label: '现金流可支撑时间',
    cash_coverage_months: 8.3,
    mrr: 0,
    mrr_change: 0,
    users: 0,
    users_change: 0,
    product_score: 20,
    product_change: 0,
    reputation: 50,
    founder_equity: 100,
    valuation: 2640000
  },
  stage: {
    company_name: 'NimbusAI',
    week_label: 'Week 1, Mon',
    focus: '活下去、做产品、拿到下一轮机会'
  },
  core_tension: {
    title: '早期打磨期',
    description: '第1个月，产品分20。现在是打磨产品的最佳窗口，你有时间和资源把产品做好。',
    severity: 'low',
    next_focus: '专注研发，在竞品反应过来之前建立产品壁垒。'
  },
  insight: {
    title: '产品仍在打磨期',
    description: '现阶段优先把产品体验做稳，再考虑更大规模获客。'
  },
  board: [
    {
      name: 'CFO',
      role: '财务负责人',
      message: '现金流正常，可支撑8.3个月。保持现有节奏，预留至少6个月安全垫。',
      confidence: 88
    },
    {
      name: 'CTO',
      role: '技术负责人',
      message: '产品还太弱。现在应该投入研发，把核心体验补起来。',
      confidence: 83
    },
    {
      name: 'COO',
      role: '运营负责人',
      message: '运营稳定，先关注交付质量和客户满意度。',
      confidence: 78
    }
  ],
  competitors: [
    {
      name: '快答科技',
      status: '本月暂无重大动作',
      mrr: 33000,
      trend: 'flat'
    }
  ],
  advice_entry: {
    label: '查看建议',
    summary: '输入「建议」查看详情'
  },
  ending: {
    type: 'none',
    description: ''
  }
};

export const demoSuggestions: SuggestionResponse = {
  items: [
    {
      title: '稳健：产品打磨',
      description: '用较小预算提升产品分，先让体验变得可靠。',
      command: '花10万研发产品',
      risk_level: 'conservative',
      reason: '早期最重要的是把产品做扎实。'
    },
    {
      title: '激进：研发冲刺',
      description: '集中资源快速提升产品竞争力，但会缩短现金流可支撑时间。',
      command: '花25万研发产品提升竞争力',
      risk_level: 'aggressive',
      reason: '抢在竞品反应前建立产品壁垒。'
    },
    {
      title: '风险：避免空转',
      description: '不要在产品体验不足时大规模营销，获客会变贵且留不住用户。',
      command: '花8万研发产品',
      risk_level: 'warning',
      reason: '营销需要产品承接，否则会消耗现金。'
    }
  ],
  warning: '',
  recommended_focus: '产品：先把产品分提升到40以上，再扩大获客。'
};

export function demoCommandPreview(command: string): CommandPreviewResponse {
  const clauses = command
    .split(/[，,；;、]/)
    .map((item) => item.trim())
    .filter(Boolean);
  const sourceClauses = clauses.length > 0 ? clauses : [command.trim()];
  const actions = sourceClauses.flatMap((clause) => {
    const budgetMatch = clause.match(/(\d+)万/);
    const budget = budgetMatch ? Number(budgetMatch[1]) * 10000 : 0;
    const budgetLabel = budgetMatch ? `${budgetMatch[1]}万` : '无直接支出';
    if (/研发|产品|功能|迭代/i.test(clause)) {
      return [
        {
          type: 'product',
          label: '产品研发',
          intent: clause,
          budget,
          budget_label: budgetLabel,
          risk_label: '中风险',
          tradeoffs: ['产品 +', '现金 -']
        }
      ];
    }
    if (/营销|推广|获客|广告/i.test(clause)) {
      return [
        {
          type: 'marketing',
          label: '市场营销',
          intent: clause,
          budget,
          budget_label: budgetLabel,
          risk_label: '中风险',
          tradeoffs: ['用户 +', '现金 -']
        }
      ];
    }
    return [];
  });
  return {
    status: actions.length > 0 ? 'ready' : 'needs_clarification',
    summary:
      actions.length > 0
        ? `系统将这条 CEO 指令理解为 ${actions.length} 个可执行动作。`
        : '没有识别到可执行动作。可以尝试写明预算和方向，例如：花10万研发产品。',
    guardrail: '这是执行前解释，数值结算仍由 TurnEngine 执行。',
    actions
  };
}

export function demoTurn(command: string): TurnResponse {
  const productFocused = /研发|产品|build/i.test(command);
  const marketingFocused = /营销|推广|market/i.test(command);
  const productChange = productFocused ? 12 : 4;
  const usersChange = marketingFocused ? 86 : 0;
  const mrrChange = marketingFocused ? 3200 : 0;
  const cashChange = productFocused ? -220000 : marketingFocused ? -180000 : -120000;

  return {
    state: {
      ...demoInitialState,
      metrics: {
        ...demoInitialState.metrics,
        month: 2,
        cash: demoInitialState.metrics.cash + cashChange,
        cash_change: cashChange,
        cash_coverage_months: 6.5,
        mrr: mrrChange,
        mrr_change: mrrChange,
        users: usersChange,
        users_change: usersChange,
        product_score: demoInitialState.metrics.product_score + productChange,
        product_change: productChange
      },
      core_tension: {
        title: productFocused ? '产品推进 vs 现金消耗' : '增长动作 vs 产品承接',
        description: productFocused
          ? '研发带来了产品进展，但现金流可支撑时间正在缩短。'
          : '增长动作开始产生信号，但产品质量仍决定留存。',
        severity: 'medium',
        next_focus: '继续推进，但要控制单月支出，避免现金压力过早出现。'
      },
      insight: {
        title: productFocused ? '研发投入带来产品进展' : '增长开始有反馈',
        description: productFocused
          ? '本月产品分明显提升，下一步可以小规模验证客户反馈。'
          : '营销带来新用户，但要观察留存和转化质量。'
      },
      competitors: [
        {
          name: '灵犀客服云',
          status: '升级企业功能，继续抢高端客户',
          mrr: 41000,
          trend: 'up'
        }
      ],
      board: [
        {
          name: 'CFO',
          role: '财务负责人',
          message: '本月投入有效，但现金消耗上升。建议把单月支出控制在可承受范围。',
          confidence: 84
        },
        {
          name: 'CTO',
          role: '技术负责人',
          message: '产品推进方向正确，可以继续打磨核心功能。',
          confidence: 86
        },
        {
          name: 'COO',
          role: '运营负责人',
          message: '注意交付节奏，别让团队同时背太多目标。',
          confidence: 79
        }
      ]
    },
    turn: {
      month: 1,
      delta_reasons: ['Vercel demo mode: simulated one turn']
    }
  };
}
