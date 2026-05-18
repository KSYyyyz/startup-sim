export type ScenarioRoom = {
  id: 'product' | 'team' | 'sales' | 'board' | 'servers';
  name: string;
  fantasy: string;
};

export type ScenarioBoardRole = {
  id: string;
  title: string;
  stance: string;
  focus: string;
};

export type ScenarioCompetitor = {
  id: string;
  name: string;
  style: string;
  pressure: string;
};

export type GameScenario = {
  id: string;
  name: string;
  version: string;
  pitch: string;
  startingCompany: {
    displayName: string;
    cashLabel: string;
    founderRole: string;
  };
  rooms: ScenarioRoom[];
  boardRoles: ScenarioBoardRole[];
  competitors: ScenarioCompetitor[];
  marketTags: string[];
  contentPack: {
    type: 'builtin';
    allowsModsLater: boolean;
  };
  rulesAuthority: 'backend-turn-engine';
};

export const aiSaasSeedScenario: GameScenario = {
  id: 'ai-saas-seed',
  name: 'AI SaaS 初创公司',
  version: 'alpha-0.2',
  pitch: '带领一家早期 AI SaaS 公司在现金、产品、增长和董事会压力之间寻找 PMF。',
  startingCompany: {
    displayName: 'NimbusAI',
    cashLabel: '100万启动现金',
    founderRole: 'CEO'
  },
  rooms: [
    { id: 'product', name: '产品室', fantasy: '把模糊需求打磨成客户愿意留下的功能。' },
    { id: 'team', name: '团队区', fantasy: '让小团队在压力下保持节奏和士气。' },
    { id: 'sales', name: '增长区', fantasy: '用有限预算验证渠道和客户意愿。' },
    { id: 'board', name: '董事会', fantasy: '面对不同立场的顾问和投资人压力。' },
    { id: 'servers', name: '交付机房', fantasy: '守住稳定性、交付和客户信任。' }
  ],
  boardRoles: [
    { id: 'cfo', title: '财务顾问', stance: '现金纪律', focus: '现金流可支撑时间和固定支出' },
    { id: 'cto', title: '技术顾问', stance: '产品护城河', focus: '产品质量、可靠性和长期技术壁垒' },
    { id: 'growth', title: '增长合伙人', stance: '增长效率', focus: '获客质量、渠道验证和收入增长' }
  ],
  competitors: [
    { id: 'lingxi-cloud', name: '灵犀客服云', style: '产品速度快', pressure: '持续升级企业功能' },
    { id: 'kuaida-tech', name: '快答科技', style: '营销投入高', pressure: '用渠道声量抢占早期客户' },
    { id: 'zhiyuan-suite', name: '智元套件', style: '大客户关系强', pressure: '通过集成方案绑定标杆客户' }
  ],
  marketTags: ['AI SaaS', '企业服务', '早期 PMF', '订阅收入', '董事会压力'],
  contentPack: {
    type: 'builtin',
    allowsModsLater: true
  },
  rulesAuthority: 'backend-turn-engine'
};

export const builtinScenarios: GameScenario[] = [aiSaasSeedScenario];
