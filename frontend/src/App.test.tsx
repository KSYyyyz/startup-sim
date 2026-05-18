import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import App from './App';
import { useGameStore } from './store';
import type { TurnResponse } from './types';

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
  phase_goals: {
    phase_label: '0-12个月',
    title: '早期生存目标',
    summary: '先让产品和现金流进入可验证节奏。',
    objectives: [
      {
        id: 'product-readiness',
        title: '提升产品成熟度',
        status: '进行中',
        progress_label: '产品 20/35',
        action_directions: ['研发投入', '客户访谈', '小范围试点'],
        risk_hint: '不要在客户验证不足时一次性加大投放。'
      },
      {
        id: 'cash-discipline',
        title: '保持现金纪律',
        status: '进行中',
        progress_label: '现金流可支撑时间 8.3个月',
        action_directions: ['控制固定支出', '小额试验', '融资准备'],
        risk_hint: '现金流可支撑时间低于4个月时先收缩预算。'
      }
    ]
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

function installFetchMock(
  turnPayload: Pick<
    TurnResponse,
    | 'turn'
    | 'turn_facts'
    | 'role_memory'
    | 'recent_role_memory'
    | 'memory_history'
    | 'office_signals'
    | 'story_events'
  > = {
    turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] }
  },
  reviewPayload: unknown = null
) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith('/api/sessions')) {
      return new Response(JSON.stringify(initialState), { status: 200 });
    }
    if (url.endsWith('/api/sessions/7/turns')) {
      return new Response(
        JSON.stringify({
          state: nextState,
          ...turnPayload
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
    if (url.endsWith('/api/sessions/7/review')) {
      return reviewPayload
        ? new Response(JSON.stringify(reviewPayload), { status: 200 })
        : new Response(JSON.stringify({ message: 'not found' }), { status: 404 });
    }
    return new Response(JSON.stringify({ message: 'not found' }), { status: 404 });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('Startup Sim frontend shell', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    useGameStore.setState({
      state: null,
      suggestions: null,
      commandPreview: null,
      review: null,
      lastTurn: null,
      loading: false,
      submitting: false,
      previewing: false,
      reviewing: false,
      reviewUnavailable: false,
      error: ''
    });
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
    expect(screen.getByRole('button', { name: '解释指令' })).toBeDisabled();
    expect(screen.getByRole('button', { name: '移动端执行' })).toBeDisabled();
    expect(screen.getByRole('button', { name: '移动端解释指令' })).toBeDisabled();
    expect(screen.getByText('从办公室选择行动，或直接输入 CEO 指令。')).toBeInTheDocument();
    expect(screen.getByText('第1月')).toBeInTheDocument();
    const hud = within(screen.getByLabelText('公司指标'));
    expect(hud.getByText('现金')).toBeInTheDocument();
    expect(hud.getByText('用户')).toBeInTheDocument();
    expect(hud.getByText('产品')).toBeInTheDocument();
    expect(hud.queryByText('声誉')).not.toBeInTheDocument();
    expect(hud.queryByText('创始人股权')).not.toBeInTheDocument();
    expect(hud.queryByText('估值')).not.toBeInTheDocument();
    expect(hud.getByText('现金流可支撑时间')).toBeInTheDocument();
    expect(screen.getByText('核心矛盾')).toBeInTheDocument();
    expect(screen.getByText('经营洞察')).toBeInTheDocument();
    const onboarding = screen.getByLabelText('新手经营节奏');
    expect(onboarding).toHaveTextContent('第1步');
    expect(onboarding).toHaveTextContent('先读局面');
    expect(onboarding).toHaveTextContent('现金流可支撑时间');
    expect(onboarding).not.toHaveTextContent('花10万研发产品');
    expect(onboarding).not.toHaveTextContent('一键');
    const monthGoal = screen.getByLabelText('本月小目标');
    expect(monthGoal).toHaveTextContent('产品验证前');
    expect(monthGoal).toHaveTextContent('产品 20/35');
    expect(monthGoal).toHaveTextContent('产品成熟度');
    expect(monthGoal).toHaveTextContent('57%');
    expect(monthGoal).toHaveTextContent('产品达到可验证区间');
    expect(monthGoal).toHaveTextContent('现金流可支撑时间保持安全');
    expect(monthGoal).toHaveTextContent('已满足');
    expect(monthGoal).toHaveTextContent('准备客户验证');
    expect(within(monthGoal).queryByRole('button')).not.toBeInTheDocument();
    expect(monthGoal).not.toHaveTextContent('花10万研发产品');
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
    const goalPanel = screen.getByLabelText('阶段目标');
    expect(goalPanel).toHaveTextContent('早期生存目标');
    expect(goalPanel).toHaveTextContent('提升产品成熟度');
    expect(goalPanel).toHaveTextContent('产品 20/35');
    expect(goalPanel).toHaveTextContent('研发投入');
    expect(goalPanel).toHaveTextContent('客户访谈');
    expect(goalPanel).toHaveTextContent('不要在客户验证不足时一次性加大投放。');
    expect(within(goalPanel).queryByRole('button')).not.toBeInTheDocument();
    expect(goalPanel).not.toHaveTextContent('花10万研发产品');
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
    const productExpectation = screen.getByLabelText('产品打磨行动预期');
    expect(productExpectation).toHaveTextContent('收益');
    expect(productExpectation).toHaveTextContent('产品体验更完整，后续客户验证更有底气。');
    expect(productExpectation).toHaveTextContent('代价');
    expect(productExpectation).toHaveTextContent('本月现金会减少，其他动作空间变小。');
    expect(productExpectation).toHaveTextContent('适合时机');
    expect(productExpectation).toHaveTextContent('产品还没到可验证区间，但现金流可支撑时间仍安全。');
    expect(productExpectation).toHaveTextContent('风险');
    expect(productExpectation).toHaveTextContent('如果不尽快接触客户，可能继续陷入闭门打磨。');

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
    const preview = screen.getByLabelText('AI 指令解释');
    expect(preview).toHaveTextContent('已从 快捷行动 生成 1 个执行前预期。');
    expect(preview).toHaveTextContent('现金 +');
    expect(preview).toHaveTextContent('股权 -');
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
    expect(preview).not.toHaveTextContent('花10万研发产品，花5万做营销 产品 +');
    expect(screen.getByLabelText('AI 指令解释')).toHaveClass('compact');
  });

  test('lets the mobile command strip explain commands before execution', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('移动端本回合指令'), '花10万研发产品，花5万做营销');
    await userEvent.click(screen.getByRole('button', { name: '移动端解释指令' }));

    const preview = await screen.findByLabelText('AI 指令解释');
    expect(preview).toHaveTextContent('产品研发');
    expect(preview).toHaveTextContent('市场营销');
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
    expect(screen.getAllByText('执行指令').length).toBeGreaterThan(0);
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
    expect(screen.getByText('事实依据')).toBeInTheDocument();
    expect(screen.getAllByText('执行指令').length).toBeGreaterThan(1);
    expect(screen.getAllByText('花10万研发产品').length).toBeGreaterThan(1);
    expect(screen.getByText('结算变化')).toBeInTheDocument();
    expect(screen.getByText('下月压力')).toBeInTheDocument();
    expect(screen.getByText('下月补救')).toBeInTheDocument();
    expect(screen.getByText('先压住现金消耗，再继续验证产品改进是否能转成增长。')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '采用补救行动' }));
    expect(screen.getAllByDisplayValue('花1万研发产品保持最低运转').length).toBeGreaterThan(0);
    expect(within(screen.getByLabelText('已准备行动')).getByText('下月补救')).toBeInTheDocument();
    expect(screen.getAllByText('研发投入提升了产品分，但现金消耗上升。').length).toBeGreaterThan(1);
    expect(screen.getAllByText('研发有效，但现金消耗上升。').length).toBeGreaterThan(0);
    expect(screen.getByText('记忆：上月现金减少，CFO 会继续盯预算。')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '竞品' }));
    expect(screen.getAllByText('灵犀客服云').length).toBeGreaterThan(0);
    expect(screen.getByText('上升')).toBeInTheDocument();
    expect(screen.getAllByText('研发投入带来产品进展').length).toBeGreaterThan(0);
  });

  test('uses settled turn facts first when building the monthly report', async () => {
    installFetchMock({
      turn: { month: 1, delta_reasons: ['旧版 delta_reasons 不应进入 TurnFacts 月报。'] },
      turn_facts: {
        month: 1,
        command: '花10万研发产品',
        changes: [
          { label: 'TurnFacts 产品', value: '+12 分', tone: 'good' },
          { label: 'TurnFacts 现金', value: '-20 万', tone: 'bad' }
        ],
        replay_basis: ['TurnFacts 复盘依据：研发效率高于预期。'],
        next_pressure: 'TurnFacts 下月压力：控制燃烧率。'
      }
    });
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    expect(await screen.findByText('月度战报')).toBeInTheDocument();
    expect(screen.getByText('TurnFacts 产品')).toBeInTheDocument();
    expect(screen.getByText('+12 分')).toBeInTheDocument();
    expect(screen.getByText('TurnFacts 现金')).toBeInTheDocument();
    expect(screen.getByText('-20 万')).toBeInTheDocument();
    expect(screen.getAllByText('TurnFacts 复盘依据：研发效率高于预期。').length).toBeGreaterThan(1);
    expect(screen.getByText('TurnFacts 下月压力：控制燃烧率。')).toBeInTheDocument();
    expect(screen.queryByText('旧版 delta_reasons 不应进入 TurnFacts 月报。')).not.toBeInTheDocument();
  });

  test('shows objective progress after a turn without executable objective commands', async () => {
    installFetchMock({
      turn: {
        month: 1,
        delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'],
        objective_updates: [
          {
            id: 'product-readiness',
            title: '提升产品成熟度',
            status: '完成',
            summary: '产品成熟度目标推进明显。'
          },
          {
            id: 'cash-discipline',
            title: '保持现金纪律',
            status: '承压',
            summary: '现金消耗上升，需要控制下月预算。'
          }
        ]
      }
    });
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    const objectiveProgress = await screen.findByLabelText('目标进展');
    expect(objectiveProgress).toHaveTextContent('提升产品成熟度');
    expect(objectiveProgress).toHaveTextContent('完成');
    expect(objectiveProgress).toHaveTextContent('保持现金纪律');
    expect(objectiveProgress).toHaveTextContent('承压');
    expect(within(objectiveProgress).queryByRole('button')).not.toBeInTheDocument();
    expect(objectiveProgress).not.toHaveTextContent('花10万研发产品');
    expect(screen.queryByRole('button', { name: '采用目标行动' })).not.toBeInTheDocument();
  });

  test('uses backend role memory and office signals before deterministic fallbacks', async () => {
    installFetchMock({
      turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] },
      role_memory: [
        {
          role_id: 'cfo',
          role_name: 'CFO',
          fact: '后端事实：现金消耗来自研发冲刺。',
          implication: 'CFO 会要求下月预算上限。'
        }
      ],
      office_signals: [
        {
          id: 'cash-review',
          room_id: 'board',
          title: '后端信号：预算审查',
          description: '董事会要求解释现金消耗。',
          severity: 'warning',
          source: 'role-memory',
          visual_intent: 'surface-in-office'
        },
        {
          id: 'delivery-watch',
          room_id: 'servers',
          title: '后端信号：交付风险',
          description: '服务稳定性需要关注。',
          severity: 'critical',
          source: 'turn-facts',
          visual_intent: 'surface-in-office'
        }
      ],
      story_events: [
        {
          id: 'product-event',
          title: '后端事件：产品冲刺',
          description: '研发投入带来可见产品改善。',
          tone: 'good',
          source: 'rule-event'
        }
      ]
    });
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    expect(await screen.findByText('月度战报')).toBeInTheDocument();
    expect(screen.getByLabelText('办公室提示')).toHaveTextContent('后端信号：预算审查');
    expect(screen.getByLabelText('办公室信号')).toHaveTextContent('后端信号：预算审查');
    expect(screen.getByLabelText('办公室信号')).toHaveTextContent('后端信号：交付风险');
    expect(screen.getByLabelText('董事会状态')).toHaveTextContent('后端信号：预算审查');
    expect(screen.getByLabelText('董事会经营状态')).toHaveTextContent('后端信号：预算审查');
    expect(screen.getByLabelText('服务器经营状态')).toHaveTextContent('后端信号：交付风险');
    expect(screen.getByLabelText('本月事件')).toHaveTextContent('后端事件：产品冲刺');
    expect(screen.getByLabelText('本月事件')).toHaveTextContent('研发投入带来可见产品改善。');
    expect(screen.getByText('记忆：后端事实：现金消耗来自研发冲刺。CFO 会要求下月预算上限。')).toBeInTheDocument();
    expect(screen.queryByText('记忆：上月现金减少，CFO 会继续盯预算。')).not.toBeInTheDocument();
  });

  test('shows only the most relevant board memory from recent and historical facts', async () => {
    installFetchMock({
      turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] },
      role_memory: [
        {
          role_id: 'cfo',
          role_name: 'CFO',
          fact: '旧 role_memory：现金减少。',
          implication: '旧建议。'
        }
      ],
      recent_role_memory: [
        {
          role_id: 'cfo',
          role_name: 'CFO',
          fact: '最近事实：研发让现金承压。',
          implication: 'CFO 会先问预算上限。'
        }
      ],
      memory_history: [
        {
          role_id: 'cfo',
          role_name: 'CFO',
          fact: '历史事实：早期现金健康。',
          implication: '历史建议。'
        }
      ]
    });
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    expect(await screen.findByText('记忆：最近事实：研发让现金承压。CFO 会先问预算上限。')).toBeInTheDocument();
    expect(screen.queryByText('记忆：旧 role_memory：现金减少。旧建议。')).not.toBeInTheDocument();
    expect(screen.queryByText('记忆：历史事实：早期现金健康。历史建议。')).not.toBeInTheDocument();
    expect(document.querySelectorAll('.board-memory')).toHaveLength(1);
  });

  test('loads a compact game review entry without opening a new panel', async () => {
    installFetchMock(
      {
        turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] }
      },
      {
        ending_status: 'survived_but_average',
        review_phase: '终局复盘',
        status_copy: '已结束',
        ending_title: '本局复盘',
        ending_summary: '产品推进有效，但现金压力上升。',
        advice_for_next_run: '下局先设预算上限。',
        key_moments: [{ title: '研发冲刺', description: '产品分显著提升。' }],
        achievement_cards: [
          { title: '产品主义者', description: '产品分提升明显。', rarity: 'silver' },
          { title: '现金守夜人', description: '及时注意到现金压力。', rarity: 'bronze' },
          { title: '董事会沟通者', description: '保持董事会反馈可见。', rarity: 'bronze' },
          { title: '不应显示的第 4 个成就', description: '超过上限。', rarity: 'gold' }
        ],
        next_run_suggestions: ['先设预算上限', '只保留一条主线动作', '复盘获客质量', '不应显示的第 4 条建议']
      }
    );
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));
    await userEvent.click(await screen.findByRole('button', { name: '查看轻量复盘' }));

    const review = await screen.findByLabelText('轻量复盘');
    expect(review).toHaveTextContent('本局复盘');
    expect(review).toHaveTextContent('终局复盘');
    expect(review).toHaveTextContent('已结束');
    expect(review).toHaveTextContent('产品推进有效，但现金压力上升。');
    expect(review).toHaveTextContent('研发冲刺');
    expect(review).toHaveTextContent('下局先设预算上限。');
    expect(review).toHaveTextContent('产品主义者');
    expect(review).toHaveTextContent('现金守夜人');
    expect(review).toHaveTextContent('董事会沟通者');
    expect(review).not.toHaveTextContent('不应显示的第 4 个成就');
    expect(review).toHaveTextContent('先设预算上限');
    expect(review).toHaveTextContent('只保留一条主线动作');
    expect(review).toHaveTextContent('复盘获客质量');
    expect(review).not.toHaveTextContent('不应显示的第 4 条建议');
    expect(screen.queryByRole('heading', { name: '复盘详情' })).not.toBeInTheDocument();
    expect(document.body.textContent).not.toMatch(/跑道|Runway/);
  });

  test('opens a compact archive tab and limits archive facts from review payload', async () => {
    const fetchMock = installFetchMock(
      {
        turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] }
      },
      {
        ending_status: 'survived_but_average',
        review_phase: '终局复盘',
        status_copy: '已结束',
        ending_title: '本局复盘',
        ending_summary: '旧摘要不应优先显示。',
        archive_summary: '档案摘要：研发路线留下清晰记录。',
        archive_timeline: [
          { title: '第1月 研发冲刺', description: '产品分提升。' },
          { title: '第2月 现金审查', description: '董事会要求收紧预算。' },
          { title: '第3月 用户验证', description: '小规模获客开始反馈。' },
          { title: '第4月 产品定型', description: '核心功能稳定。' },
          { title: '第5月 复盘沉淀', description: '形成下一局假设。' },
          { title: '第6月 不应显示', description: '超过档案时间线上限。' }
        ],
        archive_badges: [
          { title: '产品主义者', description: '产品分提升明显。', rarity: 'silver' },
          { title: '现金守夜人', description: '及时注意到现金压力。', rarity: 'bronze' },
          { title: '董事会沟通者', description: '保持董事会反馈可见。', rarity: 'bronze' },
          { title: '第4个不应显示徽章', description: '超过徽章上限。', rarity: 'gold' }
        ],
        key_moments: [{ title: '兜底关键时刻不应显示', description: 'archive_timeline 存在时不用兜底。' }],
        achievement_cards: [{ title: '兜底成就不应显示', description: 'archive_badges 存在时不用兜底。' }]
      }
    );
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));
    await screen.findByText('月度战报');

    expect(fetchMock.mock.calls.some(([input]) => String(input).endsWith('/api/sessions/7/review'))).toBe(false);

    const sideTabs = within(screen.getByRole('tablist', { name: '右侧信息' }));
    await userEvent.click(sideTabs.getByRole('button', { name: '档案' }));

    const archive = await screen.findByLabelText('局内档案');
    expect(archive).toHaveTextContent('档案摘要：研发路线留下清晰记录。');
    expect(archive).toHaveTextContent('终局复盘');
    expect(archive).toHaveTextContent('已结束');
    expect(archive).toHaveTextContent('第1月 研发冲刺');
    expect(archive).toHaveTextContent('第5月 复盘沉淀');
    expect(archive).not.toHaveTextContent('第6月 不应显示');
    expect(archive).toHaveTextContent('产品主义者');
    expect(archive).toHaveTextContent('现金守夜人');
    expect(archive).toHaveTextContent('董事会沟通者');
    expect(archive).not.toHaveTextContent('第4个不应显示徽章');
    expect(archive).not.toHaveTextContent('兜底关键时刻不应显示');
    expect(archive).not.toHaveTextContent('兜底成就不应显示');
    expect(document.body.textContent).not.toMatch(/跑道|Runway/);
  });

  test('falls back to key moments and achievement cards when archive fields are absent', async () => {
    installFetchMock(
      {
        turn: { month: 1, delta_reasons: ['研发投入提升了产品分，但现金消耗上升。'] }
      },
      {
        ending_status: 'active',
        review_phase: '阶段复盘',
        status_copy: '进行中',
        ending_summary: '阶段摘要：现金承压但产品方向清晰。',
        key_moments: [
          { title: '兜底时刻 1', description: '研发推进。' },
          { title: '兜底时刻 2', description: '现金承压。' },
          { title: '兜底时刻 3', description: '用户验证。' },
          { title: '兜底时刻 4', description: '产品定型。' },
          { title: '兜底时刻 5', description: '准备复盘。' },
          { title: '兜底时刻 6 不应显示', description: '超过时间线上限。' }
        ],
        achievement_cards: [
          { title: '兜底成就 1', description: '保持产品推进。', rarity: 'common' },
          { title: '兜底成就 2', description: '识别现金压力。', rarity: 'common' },
          { title: '兜底成就 3', description: '维持董事会沟通。', rarity: 'common' },
          { title: '兜底成就 4 不应显示', description: '超过徽章上限。', rarity: 'rare' }
        ]
      }
    );
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));
    await userEvent.click(within(screen.getByRole('tablist', { name: '右侧信息' })).getByRole('button', { name: '档案' }));

    const archive = await screen.findByLabelText('局内档案');
    expect(archive).toHaveTextContent('阶段摘要：现金承压但产品方向清晰。');
    expect(archive).toHaveTextContent('兜底时刻 1');
    expect(archive).toHaveTextContent('兜底时刻 5');
    expect(archive).not.toHaveTextContent('兜底时刻 6 不应显示');
    expect(archive).toHaveTextContent('兜底成就 1');
    expect(archive).toHaveTextContent('兜底成就 3');
    expect(archive).not.toHaveTextContent('兜底成就 4 不应显示');
    expect(document.body.textContent).not.toMatch(/跑道|Runway/);
  });

  test('keeps the archive unavailable message when review endpoint is missing', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.click(within(screen.getByRole('tablist', { name: '右侧信息' })).getByRole('button', { name: '档案' }));

    const archive = await screen.findByLabelText('局内档案');
    expect(archive).toHaveTextContent('复盘接口暂未开放。');
    expect(document.body.textContent).not.toMatch(/跑道|Runway/);
  });

  test('keeps the compact review unavailable message when the review endpoint is missing', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));
    await userEvent.click(await screen.findByRole('button', { name: '查看轻量复盘' }));

    expect(await screen.findByText('复盘接口暂未开放。')).toBeInTheDocument();
  });
});
