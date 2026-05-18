import { render, screen, waitFor } from '@testing-library/react';
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
    expect(screen.getByText('第1月')).toBeInTheDocument();
    expect(screen.getAllByText('现金').length).toBeGreaterThan(0);
    expect(screen.getAllByText('用户').length).toBeGreaterThan(0);
    expect(screen.getAllByText('产品').length).toBeGreaterThan(0);
    expect(screen.getAllByText('声誉').length).toBeGreaterThan(0);
    expect(screen.getAllByText('创始人股权').length).toBeGreaterThan(0);
    expect(screen.getAllByText('估值').length).toBeGreaterThan(0);
    expect(screen.getByText('现金流可支撑时间')).toBeInTheDocument();
    expect(screen.getByText('核心矛盾')).toBeInTheDocument();
    expect(screen.getByText('董事会')).toBeInTheDocument();
    expect(screen.getByText('竞品态势')).toBeInTheDocument();
    expect(screen.getByText('查看建议')).toBeInTheDocument();
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

  test('submits a turn and refreshes post-turn board competitor and insight feedback', async () => {
    installFetchMock();
    render(<App />);

    await screen.findByText('NimbusAI');
    await userEvent.type(screen.getByLabelText('本回合指令'), '花10万研发产品');
    await userEvent.click(screen.getByRole('button', { name: '执行回合' }));

    expect(await screen.findByText('第2月')).toBeInTheDocument();
    expect(screen.getByText('回合结果')).toBeInTheDocument();
    expect(screen.getByText('第1月执行结果')).toBeInTheDocument();
    expect(screen.getByText('研发投入提升了产品分，但现金消耗上升。')).toBeInTheDocument();
    expect(screen.getByText('研发有效，但现金消耗上升。')).toBeInTheDocument();
    expect(screen.getByText('灵犀客服云')).toBeInTheDocument();
    expect(screen.getByText('研发投入带来产品进展')).toBeInTheDocument();
  });
});
