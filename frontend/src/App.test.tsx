import { render, screen, waitFor, within } from '@testing-library/react';
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
    expect(screen.getByRole('button', { name: '执行回合' })).toBeDisabled();
    expect(screen.getByText('从办公室选择行动，或直接输入 CEO 指令。')).toBeInTheDocument();
    expect(screen.getByText('第1月')).toBeInTheDocument();
    expect(screen.getAllByText('现金').length).toBeGreaterThan(0);
    expect(screen.getAllByText('用户').length).toBeGreaterThan(0);
    expect(screen.getAllByText('产品').length).toBeGreaterThan(0);
    expect(screen.getAllByText('声誉').length).toBeGreaterThan(0);
    expect(screen.getAllByText('创始人股权').length).toBeGreaterThan(0);
    expect(screen.getAllByText('估值').length).toBeGreaterThan(0);
    expect(screen.getByText('现金流可支撑时间')).toBeInTheDocument();
    expect(screen.getByText('核心矛盾')).toBeInTheDocument();
    expect(screen.getByLabelText('办公室提示')).toHaveTextContent('早期打磨期');
    const officeFeedback = screen.getByLabelText('办公室动态反馈');
    expect(officeFeedback).toHaveTextContent('CFO');
    expect(officeFeedback).toHaveTextContent('控制固定支出。');
    expect(officeFeedback).toHaveTextContent('快答科技：本月暂无重大动作');
    expect(screen.getByLabelText('产品室状态')).toHaveTextContent('产品压力');
    expect(screen.getAllByText('董事会').length).toBeGreaterThan(0);
    expect(screen.getByText('竞品态势')).toBeInTheDocument();
    expect(screen.getByText('持平')).toBeInTheDocument();
    expect(screen.getByText('查看建议')).toBeInTheDocument();
    expect(screen.getByText('现金纪律')).toBeInTheDocument();
    expect(screen.getByText('产品护城河')).toBeInTheDocument();
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
    expect(screen.getByText('当前房间')).toBeInTheDocument();
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

  test('lets office feedback signals open matching side panels', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    const sideTabs = within(screen.getByRole('tablist', { name: '右侧信息' }));

    await userEvent.click(screen.getByRole('button', { name: /查看竞品信号/ }));

    expect(sideTabs.getByRole('button', { name: '竞品' })).toHaveClass('active');
    expect(screen.getByRole('heading', { name: '竞品态势' })).toBeInTheDocument();
    expect(screen.getAllByText('快答科技').length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole('button', { name: /查看董事会信号/ }));

    expect(sideTabs.getByRole('button', { name: '董事会' })).toHaveClass('active');
    expect(screen.getByRole('heading', { name: '董事会反馈' })).toBeInTheDocument();
    expect(screen.getByText('控制固定支出。')).toBeInTheDocument();
  });

  test('lets the player turn board pressure into a command', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.click(screen.getByRole('button', { name: '回应 CFO 压力' }));

    expect(screen.getByLabelText('本回合指令')).toHaveValue('花1万研发产品保持最低运转');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('CFO');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('控制固定支出。');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('现金流可支撑时间 +');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('增长 -');
    expect(screen.queryByLabelText('已准备行动')).not.toBeInTheDocument();
  });

  test('lets the player turn competitor pressure into a command', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.click(screen.getByRole('button', { name: /查看竞品信号/ }));
    await userEvent.click(screen.getByRole('button', { name: '回应快答科技压力' }));

    expect(screen.getByLabelText('本回合指令')).toHaveValue('花10万做营销推广');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('快答科技');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('本月暂无重大动作');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('用户 +');
    expect(screen.getByLabelText('已生成回应指令')).toHaveTextContent('现金 -');
    expect(screen.queryByLabelText('已准备行动')).not.toBeInTheDocument();
  });

  test('submits a turn and refreshes post-turn board competitor and insight feedback', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    expect(await screen.findByText('第2月')).toBeInTheDocument();
    expect(screen.getByText('月度战报')).toBeInTheDocument();
    expect(screen.getByLabelText('办公室月末变化')).toHaveTextContent('产品');
    expect(screen.getByLabelText('办公室月末变化')).toHaveTextContent('+8 分');
    expect(screen.getByText('第1月执行结果')).toBeInTheDocument();
    expect(screen.getAllByText('本月变化').length).toBeGreaterThan(1);
    expect(screen.getByText('原因复盘')).toBeInTheDocument();
    expect(screen.getByText('下月压力')).toBeInTheDocument();
    expect(screen.getByText('研发投入提升了产品分，但现金消耗上升。')).toBeInTheDocument();
    expect(screen.getByText('研发有效，但现金消耗上升。')).toBeInTheDocument();
    expect(screen.getByText('灵犀客服云')).toBeInTheDocument();
    expect(screen.getByText('上升')).toBeInTheDocument();
    expect(screen.getByText('研发投入带来产品进展')).toBeInTheDocument();
  });
});
