import { useEffect, useMemo, useState } from 'react';
import {
  Banknote,
  BarChart3,
  Bot,
  Boxes,
  BriefcaseBusiness,
  CalendarDays,
  ChartNoAxesCombined,
  CircleDollarSign,
  HandCoins,
  Megaphone,
  Play,
  Settings,
  Sparkles,
  Users
} from 'lucide-react';

import { useGameStore } from './store';
import type { CompetitorItem, MetricSet } from './types';
import './styles.css';

function money(value: number) {
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(2)}M`;
  if (Math.abs(value) >= 10_000) return `$${Math.round(value / 10_000)}万`;
  return `$${value.toLocaleString()}`;
}

function signed(value: number, formatter = money) {
  if (value === 0) return '';
  return `${value > 0 ? '+' : ''}${formatter(value)}`;
}

function metricCards(metrics: MetricSet) {
  return [
    {
      label: 'Month',
      value: `Month ${metrics.month}`,
      detail: 'Week rhythm',
      icon: CalendarDays,
      delta: ''
    },
    {
      label: 'Cash',
      value: money(metrics.cash),
      detail: '现金',
      icon: CircleDollarSign,
      delta: signed(metrics.cash_change)
    },
    {
      label: metrics.cash_coverage_label,
      value: `${metrics.cash_coverage_months.toFixed(1)} months`,
      detail: '固定支出覆盖',
      icon: ChartNoAxesCombined,
      delta: ''
    },
    {
      label: 'MRR',
      value: money(metrics.mrr),
      detail: '经常性收入',
      icon: BarChart3,
      delta: signed(metrics.mrr_change)
    },
    {
      label: 'Users',
      value: metrics.users.toLocaleString(),
      detail: '用户数',
      icon: Users,
      delta: signed(metrics.users_change, (v) => v.toLocaleString())
    },
    {
      label: 'Product',
      value: `v0.${Math.max(1, Math.floor(metrics.product_score / 10))}.${metrics.product_score % 10}`,
      detail: `产品分 ${metrics.product_score}`,
      icon: Boxes,
      delta: signed(metrics.product_change, (v) => `${v}`)
    },
    {
      label: 'Reputation',
      value: `${metrics.reputation}`,
      detail: '声誉',
      icon: Sparkles,
      delta: ''
    },
    {
      label: 'Equity',
      value: `${metrics.founder_equity}%`,
      detail: '创始人股权',
      icon: BriefcaseBusiness,
      delta: ''
    },
    {
      label: 'Valuation',
      value: money(metrics.valuation),
      detail: '估值',
      icon: Banknote,
      delta: ''
    }
  ];
}

function trendLabel(item: CompetitorItem) {
  if (item.trend === 'up') return '↑';
  if (item.trend === 'down') return '↓';
  return '→';
}

export default function App() {
  const { state, suggestions, loading, submitting, error, boot, runTurn, openSuggestions } =
    useGameStore();
  const [command, setCommand] = useState('');
  const [rightTab, setRightTab] = useState<'board' | 'competitors' | 'advice' | 'log'>('board');

  useEffect(() => {
    void boot();
  }, [boot]);

  const cards = useMemo(() => (state ? metricCards(state.metrics) : []), [state]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!command.trim()) return;
    await runTurn(command);
    setCommand('');
  }

  async function handleAdvice() {
    setRightTab('advice');
    if (!suggestions) {
      await openSuggestions();
    }
  }

  if (loading || !state) {
    return (
      <main className="loading-screen">
        <div className="loading-card">正在启动 NimbusAI 董事会作战室...</div>
      </main>
    );
  }

  return (
    <main className="app-shell text-slate-900">
      <section className="hud" aria-label="公司指标">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <article className="hud-card" key={card.label}>
              <Icon size={24} aria-hidden="true" />
              <div>
                <strong>{card.value}</strong>
                <span>{card.label}</span>
                {card.delta && <em className={card.delta.startsWith('+') ? 'good' : 'bad'}>{card.delta}</em>}
              </div>
            </article>
          );
        })}
        <button className="icon-button" aria-label="设置">
          <Settings size={24} />
        </button>
      </section>

      <section className="workspace">
        <aside className="left-stack">
          <div className="brand-panel">
            <Bot size={42} />
            <div>
              <h1>{state.stage.company_name}</h1>
              <p>{state.stage.focus}</p>
            </div>
          </div>

          <article className="panel">
            <h2>本月变化</h2>
            <dl className="change-list">
              <div>
                <dt>Cash</dt>
                <dd className={state.metrics.cash_change >= 0 ? 'good' : 'bad'}>
                  {signed(state.metrics.cash_change) || '稳定'}
                </dd>
              </div>
              <div>
                <dt>MRR</dt>
                <dd>{signed(state.metrics.mrr_change) || '观察中'}</dd>
              </div>
              <div>
                <dt>Users</dt>
                <dd>{signed(state.metrics.users_change, (v) => v.toLocaleString()) || '观察中'}</dd>
              </div>
            </dl>
          </article>

          <article className="panel core-panel">
            <h2>核心矛盾</h2>
            <strong>{state.core_tension.title}</strong>
            <p>{state.core_tension.description}</p>
            <small>{state.core_tension.next_focus}</small>
          </article>
        </aside>

        <section className="office-stage" aria-label="办公室场景">
          <img src="/office-preview.jpg" alt="NimbusAI office command center" />
          <div className="stage-badge product">Product Room</div>
          <div className="stage-badge team">Dev Team</div>
          <div className="stage-badge sales">Sales</div>
          <div className="stage-badge server">Servers</div>
          <div className="insight-strip">
            <strong>{state.insight.title}</strong>
            <span>{state.insight.description}</span>
          </div>
        </section>

        <aside className="right-stack">
          <div className="tabs" role="tablist" aria-label="右侧信息">
            <button className={rightTab === 'board' ? 'active' : ''} onClick={() => setRightTab('board')}>
              董事会
            </button>
            <button
              className={rightTab === 'competitors' ? 'active' : ''}
              onClick={() => setRightTab('competitors')}
            >
              竞品
            </button>
            <button className={rightTab === 'advice' ? 'active' : ''} onClick={handleAdvice}>
              建议
            </button>
            <button className={rightTab === 'log' ? 'active' : ''} onClick={() => setRightTab('log')}>
              记录
            </button>
          </div>

          <button className="advice-entry" type="button" onClick={handleAdvice}>
            <strong>{state.advice_entry.label}</strong>
            <span>{state.advice_entry.summary}</span>
          </button>

          <article className="competitor-glance" aria-label="竞品态势">
            <strong>竞品态势</strong>
            <span>
              <b>{state.competitors[0]?.name ?? '暂无竞品'}</b>
              <small>{state.competitors[0]?.status ?? '本月暂无重大动作'}</small>
            </span>
          </article>

          {rightTab === 'board' && (
            <article className="panel tall-panel">
              <h2>董事会反馈</h2>
              {state.board.map((member) => (
                <div className="board-row" key={member.name}>
                  <div className="avatar">{member.name.slice(0, 1)}</div>
                  <div>
                    <strong>{member.name}</strong>
                    <span>{member.role}</span>
                    <p>{member.message}</p>
                  </div>
                  <em>{member.confidence}</em>
                </div>
              ))}
            </article>
          )}

          {rightTab === 'competitors' && (
            <article className="panel tall-panel">
              <h2>竞品态势</h2>
              {state.competitors.map((item) => (
                <div className="competitor-row" key={item.name}>
                  <strong>{item.name}</strong>
                  <span>{money(item.mrr)} MRR</span>
                  <em className={item.trend}>{trendLabel(item)}</em>
                  <p>{item.status}</p>
                </div>
              ))}
            </article>
          )}

          {rightTab === 'advice' && (
            <article className="panel tall-panel">
              <h2>建议详情</h2>
              <p>{state.advice_entry.summary}</p>
              {suggestions?.items.map((item) => (
                <div className="advice-row" key={item.title}>
                  <strong>{item.title}</strong>
                  <p>{item.description}</p>
                  <code>{item.command}</code>
                </div>
              ))}
            </article>
          )}

          {rightTab === 'log' && (
            <article className="panel tall-panel">
              <h2>经营记录</h2>
              <p>当前状态：{state.status}</p>
              <p>估值：{money(state.metrics.valuation)}</p>
              {state.ending.type !== 'none' && <strong>{state.ending.description}</strong>}
            </article>
          )}
        </aside>
      </section>

      <section className="action-dock" aria-label="本回合动作">
        <button type="button" onClick={() => setCommand('花10万研发产品')}>
          <Boxes size={22} /> Build
        </button>
        <button type="button" onClick={() => setCommand('花8万招聘人才')}>
          <Users size={22} /> Hire
        </button>
        <button type="button" onClick={() => setCommand('融资300万出让8%股权')}>
          <HandCoins size={22} /> Fundraise
        </button>
        <button type="button" onClick={() => setCommand('花10万做营销推广')}>
          <Megaphone size={22} /> Marketing
        </button>
        <form onSubmit={handleSubmit} className="command-form">
          <label htmlFor="turn-command">本回合指令</label>
          <input
            id="turn-command"
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            placeholder="例如：花10万研发产品"
          />
          <button type="submit" disabled={submitting}>
            <Play size={20} />
            执行回合
          </button>
        </form>
      </section>

      {error && <div className="toast" role="alert">{error}</div>}
    </main>
  );
}
