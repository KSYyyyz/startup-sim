import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import App from './App';

const initialState = {
  session_id: 7,
  status: 'active',
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
    description: '现在是打磨产品的最佳窗口。',
    severity: 'low',
    next_focus: '专注研发'
  },
  insight: {
    title: '产品仍在打磨期',
    description: '先用小预算验证客户需求。'
  },
  board: [
    { name: 'CFO', role: '财务负责人', message: '控制固定支出。', confidence: 84 },
    { name: 'CTO', role: '技术负责人', message: '产品体验仍需提升。', confidence: 80 }
  ],
  competitors: [
    { name: '快答科技', status: '本月暂无重大动作', mrr: 33000, trend: 'flat' }
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

const nextState = {
  ...initialState,
  metrics: {
    ...initialState.metrics,
    month: 2,
    cash: 780000,
    cash_change: -220000,
    product_score: 28,
    product_change: 8
  },
  board: [
    { name: 'CFO', role: '财务负责人', message: '研发有效，但现金消耗上升。', confidence: 83 }
  ],
  competitors: [
    { name: '灵犀客服云', status: '升级企业功能', mrr: 41000, trend: 'up' }
  ],
  insight: {
    title: '研发投入带来产品进展',
    description: '本月产品分提升，但要关注现金流可支撑时间。'
  }
};

const suggestions = {
  items: [
    {
      title: '稳健：均衡发展',
      description: '适度投入产品和轻量获客。',
      command: '花10万研发产品',
      risk_level: 'conservative',
      reason: '保持节奏'
    }
  ],
  warning: '',
  recommended_focus: '产品'
};

const commandPreview = {
  status: 'ready',
  summary: '系统将这条 CEO 指令理解为 2 个可执行动作。',
  guardrail: '这是执行前解释，数值结算仍由 TurnEngine 执行。',
  actions: [
    {
      type: 'product',
      label: '产品研发',
      intent: '花10万研发产品',
      budget: 100000,
      budget_label: '10万',
      risk_label: '中风险',
      tradeoffs: ['产品 +', '现金 -']
    },
    {
      type: 'marketing',
      label: '市场营销',
      intent: '花5万做营销',
      budget: 50000,
      budget_label: '5万',
      risk_label: '中风险',
      tradeoffs: ['用户 +', '现金 -']
    }
  ]
};

function installFetchMock() {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith('/api/sessions')) {
      return new Response(JSON.stringify(initialState), { status: 200 });
    }
    if (url.endsWith('/api/sessions/7/turns')) {
      return new Response(
        JSON.stringify({
          state: nextState,
          turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] }
        }),
        { status: 200 }
      );
    }
    if (url.endsWith('/api/sessions/7/suggestions')) {
      return new Response(JSON.stringify(suggestions), { status: 200 });
    }
    if (url.endsWith('/api/sessions/7/command-preview')) {
      return new Response(JSON.stringify(commandPreview), { status: 200 });
    }
    return new Response(JSON.stringify({ message: 'not found' }), { status: 404 });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('Startup Sim frontend shell', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  test('renders the playable command center without banned cash wording', async () => {
    installFetchMock();
    render(<App />);

    expect(await screen.findByText('NimbusAI')).toBeInTheDocument();
    expect(screen.getByText('AI SaaS 初创公司')).toBeInTheDocument();
    expect(screen.getByText('当前剧本')).toBeVisible();
    expect(screen.getByText('难度：标准')).toBeVisible();
    expect(screen.getByText('竞品追赶')).not.toBeVisible();
    expect(screen.getByRole('button', { name: '执行回合' })).toBeDisabled();
    expect(screen.getByText('从办公室选择行动，或直接输入 CEO 指令。')).toBeInTheDocument();
    expect(screen.getByText('第1月')).toBeInTheDocument();
    const hud = within(screen.getByLabelText('公司指标'));
    expect(hud.getByText('现金')).toBeInTheDocument();
    expect(hud.getByText('用户')).toBeInTheDocument();
    expect(hud.getByText('产品')).toBeInTheDocument();
    expect(hud.queryByText('声誉')).not.toBeInTheDocument();
    expect(hud.queryByText('创始人股权')).not.toBeInTheDocument();
    expect(hud.queryByText('估值')).not.toBeInTheDocument();
    expect(screen.getByText('现金流可支撑时间')).toBeInTheDocument();
    expect(screen.getByText('核心矛盾')).toBeInTheDocument();
    expect(screen.getByText('经营洞察')).toBeInTheDocument();
    expect(screen.getByLabelText('办公室提示')).toHaveTextContent('早期打磨期');
    expect(screen.queryByLabelText('办公室动态反馈')).not.toBeInTheDocument();
    expect(screen.getByLabelText('产品室状态')).toHaveTextContent('产品压力');
    expect(screen.getByLabelText('产品室经营状态')).toHaveTextContent('运转中');
    expect(screen.queryByLabelText('办公室事件')).not.toBeInTheDocument();
    expect(screen.getByLabelText('办公室操作台')).toBeInTheDocument();
    expect(screen.getByText('选中房间')).toBeInTheDocument();
    expect(screen.getAllByText('董事会').length).toBeGreaterThan(0);
    expect(screen.queryByLabelText('竞品态势')).not.toBeInTheDocument();
    expect(screen.queryByText('暂无大动作')).not.toBeInTheDocument();
    expect(screen.getByText('查看建议')).toBeInTheDocument();
    expect(screen.getAllByText('现金纪律').length).toBeGreaterThan(0);
    expect(screen.getAllByText('产品护城河').length).toBeGreaterThan(0);
    expect(screen.getAllByText('信任稳定').length).toBeGreaterThan(0);
    expect(screen.getAllByText('持续观察').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('移动端本回合指令')).toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/跑道|Runway/);
  });

  test('keeps advice collapsed until the player opens it', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('查看建议');
    expect(screen.queryByText('稳健：均衡发展')).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: '建议' }));

    expect(await screen.findByText('稳健：均衡发展')).toBeInTheDocument();
  });

  test('lets the player click office rooms to prepare action cards', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');

    expect(screen.getByLabelText('互动办公室场景')).toBeInTheDocument();
    const productRoom = screen.getByRole('button', { name: '产品室' });
    await userEvent.click(productRoom);

    expect(productRoom).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByText('选中房间')).toBeInTheDocument();
    expect(screen.getByText('产品打磨')).toBeInTheDocument();
    expect(screen.getAllByText('产品 +').length).toBeGreaterThan(0);
    expect(screen.getAllByText('现金 -').length).toBeGreaterThan(0);
    expect(screen.getByText('现金消耗中等，产品体验提升。')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: '采用行动：产品打磨' }));

    expect(screen.getByLabelText('本回合指令')).toHaveValue('花10万研发产品');
    const preparedAction = screen.getByLabelText('已准备行动');
    expect(preparedAction).toHaveTextContent('产品打磨');
    expect(preparedAction).toHaveTextContent('现金消耗中等，产品体验提升。');
    expect(preparedAction).toHaveTextContent('花10万研发产品');

    await userEvent.click(screen.getByRole('button', { name: '取消已准备行动' }));

    expect(screen.queryByLabelText('已准备行动')).not.toBeInTheDocument();
    expect(screen.getByLabelText('本回合指令')).toHaveValue('');
  });

  test('uses gameplay quick actions to prepare commands from the bottom dock', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.click(screen.getByRole('button', { name: '融资' }));

    expect(screen.getByLabelText('本回合指令')).toHaveValue('融资300万出让8%股权');
    const preparedAction = screen.getByLabelText('已准备行动');
    expect(preparedAction).toHaveTextContent('融资');
    expect(preparedAction).toHaveTextContent('补充现金，同时稀释创始人股权。');
    expect(preparedAction).toHaveTextContent('融资300万出让8%股权');
  });

  test('explains free-form CEO commands before execution', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品，花5万做营销');
    await userEvent.click(screen.getByRole('button', { name: '解释指令' }));

    const preview = await screen.findByLabelText('AI 指令解释');
    expect(preview).toHaveTextContent('系统将这条 CEO 指令理解为 2 个可执行动作。');
    expect(preview).toHaveTextContent('产品研发');
    expect(preview).toHaveTextContent('10万');
    expect(preview).toHaveTextContent('市场营销');
    expect(preview).toHaveTextContent('5万');
    expect(preview).toHaveTextContent('数值结算仍由 TurnEngine 执行');
  });

  test('keeps board and competitor details behind side tabs', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    const sideTabs = within(screen.getByRole('tablist', { name: '右侧信息' }));

    await userEvent.click(sideTabs.getByRole('button', { name: '竞品' }));

    expect(sideTabs.getByRole('button', { name: '竞品' })).toHaveClass('active');
    expect(screen.getByRole('heading', { name: '竞品态势' })).toBeInTheDocument();
    expect(screen.getAllByText('快答科技').length).toBeGreaterThan(0);

    await userEvent.click(sideTabs.getByRole('button', { name: '董事会' }));

    expect(sideTabs.getByRole('button', { name: '董事会' })).toHaveClass('active');
    expect(screen.getByRole('heading', { name: '董事会反馈' })).toBeInTheDocument();
    expect(screen.getAllByText('控制固定支出。').length).toBeGreaterThan(0);
  });

  test('lets the player turn board pressure into a command', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.click(screen.getByRole('button', { name: '回应 CFO 压力' }));

    expect(screen.getByLabelText('本回合指令')).toHaveValue('花1万研发产品保持最低运转');
    expect(screen.queryByLabelText('已生成回应指令')).not.toBeInTheDocument();
    const preparedAction = screen.getByLabelText('已准备行动');
    expect(preparedAction).toHaveTextContent('回应 CFO 压力');
    expect(preparedAction).toHaveTextContent('控制固定支出。');
    expect(preparedAction).toHaveTextContent('现金流可支撑时间 +');
    expect(preparedAction).toHaveTextContent('增长 -');
  });

  test('lets the player turn competitor pressure into a command', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.click(screen.getByRole('button', { name: '竞品' }));
    await userEvent.click(screen.getByRole('button', { name: '回应快答科技压力' }));

    expect(screen.getByLabelText('本回合指令')).toHaveValue('花10万做营销推广');
    expect(screen.queryByLabelText('已生成回应指令')).not.toBeInTheDocument();
    const preparedAction = screen.getByLabelText('已准备行动');
    expect(preparedAction).toHaveTextContent('回应快答科技压力');
    expect(preparedAction).toHaveTextContent('本月暂无重大动作');
    expect(preparedAction).toHaveTextContent('用户 +');
    expect(preparedAction).toHaveTextContent('现金 -');
  });

  test('submits a turn and refreshes post-turn board competitor and insight feedback', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    expect(await screen.findByText('第2月')).toBeInTheDocument();
    expect(screen.getByText('月度战报')).toBeInTheDocument();
    expect(screen.getByText('回合结算')).toBeInTheDocument();
    expect(screen.getByText('执行指令')).toBeInTheDocument();
    expect(screen.getAllByText('月末变化').length).toBeGreaterThan(0);
    expect(screen.getByText('战报复盘')).toBeInTheDocument();
    expect(screen.getAllByText('花10万研发产品').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('办公室月末变化')).toHaveTextContent('产品');
    expect(screen.getByLabelText('办公室月末变化')).toHaveTextContent('+8 分');
    expect(screen.getByLabelText('产品室经营状态')).toHaveTextContent('产品改善');
    expect(screen.getByText('第1月执行结果')).toBeInTheDocument();
    expect(screen.getAllByText('产品有进展，但现金在承压').length).toBeGreaterThan(0);
    expect(screen.getAllByText('本月变化').length).toBeGreaterThan(1);
    expect(screen.getByText('原因复盘')).toBeInTheDocument();
    expect(screen.getByText('下月压力')).toBeInTheDocument();
    expect(screen.getByText('下月补救')).toBeInTheDocument();
    expect(screen.getByText('先压住现金消耗，再继续验证产品改进是否能转成增长。')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '采用补救行动' }));
    expect(screen.getAllByDisplayValue('花1万研发产品保持最低运转').length).toBeGreaterThan(0);
    expect(within(screen.getByLabelText('已准备行动')).getByText('下月补救')).toBeInTheDocument();
    expect(screen.getByText('研发投入提升了产品分，但现金消耗上升。')).toBeInTheDocument();
    expect(screen.getAllByText('研发有效，但现金消耗上升。').length).toBeGreaterThan(0);
    await userEvent.click(screen.getByRole('button', { name: '竞品' }));
    expect(screen.getAllByText('灵犀客服云').length).toBeGreaterThan(0);
    expect(screen.getByText('上升')).toBeInTheDocument();
    expect(screen.getAllByText('研发投入带来产品进展').length).toBeGreaterThan(0);
  });
});
