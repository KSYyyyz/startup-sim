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

import { OfficeStage } from './game/OfficeStage';
import type { OfficeAction } from './game/officeRooms';
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
      label: '月份',
      value: `第${metrics.month}月`,
      detail: '本轮节奏',
      icon: CalendarDays,
      delta: ''
    },
    {
      label: '现金',
      value: money(metrics.cash),
      detail: '账上现金',
      icon: CircleDollarSign,
      delta: signed(metrics.cash_change)
    },
    {
      label: metrics.cash_coverage_label,
      value: `${metrics.cash_coverage_months.toFixed(1)}个月`,
      detail: '固定支出覆盖',
      icon: ChartNoAxesCombined,
      delta: ''
    },
    {
      label: '月经常收入',
      value: money(metrics.mrr),
      detail: '订阅收入',
      icon: BarChart3,
      delta: signed(metrics.mrr_change)
    },
    {
      label: '用户',
      value: metrics.users.toLocaleString(),
      detail: '用户数',
      icon: Users,
      delta: signed(metrics.users_change, (v) => v.toLocaleString())
    },
    {
      label: '产品',
      value: `v0.${Math.max(1, Math.floor(metrics.product_score / 10))}.${metrics.product_score % 10}`,
      detail: `产品分 ${metrics.product_score}`,
      icon: Boxes,
      delta: signed(metrics.product_change, (v) => `${v}`)
    },
    {
      label: '声誉',
      value: `${metrics.reputation}`,
      detail: '市场口碑',
      icon: Sparkles,
      delta: ''
    },
    {
      label: '创始人股权',
      value: `${metrics.founder_equity}%`,
      detail: '持股比例',
      icon: BriefcaseBusiness,
      delta: ''
    },
    {
      label: '估值',
      value: money(metrics.valuation),
      detail: '当前融资锚点',
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

function trendText(item: CompetitorItem) {
  if (item.trend === 'up') return '上升';
  if (item.trend === 'down') return '下降';
  return '持平';
}

function turnHighlights(metrics: MetricSet) {
  return [
    { label: '现金', value: signed(metrics.cash_change) || '稳定', tone: metrics.cash_change >= 0 ? 'good' : 'bad' },
    {
      label: '产品',
      value: signed(metrics.product_change, (v) => `${v} 分`) || '观察中',
      tone: metrics.product_change >= 0 ? 'good' : 'bad'
    },
    {
      label: '用户',
      value: signed(metrics.users_change, (v) => `${v.toLocaleString()} 人`) || '观察中',
      tone: metrics.users_change >= 0 ? 'good' : 'bad'
    },
    { label: '月经常收入', value: signed(metrics.mrr_change) || '观察中', tone: metrics.mrr_change >= 0 ? 'good' : 'bad' }
  ];
}

function boardStance(member: { name: string; role: string }) {
  const identity = `${member.name} ${member.role}`;
  if (/CFO|财务/.test(identity)) return '现金纪律';
  if (/CTO|技术/.test(identity)) return '产品护城河';
  if (/COO|运营/.test(identity)) return '交付质量';
  if (/增长|Growth/.test(identity)) return '增长效率';
  return '公司治理';
}

export default function App() {
  const { state, suggestions, lastTurn, loading, submitting, error, boot, runTurn, openSuggestions } =
    useGameStore();
  const [command, setCommand] = useState('');
  const [preparedAction, setPreparedAction] = useState<OfficeAction | null>(null);
  const [rightTab, setRightTab] = useState<'board' | 'competitors' | 'advice' | 'log'>('board');

  useEffect(() => {
    void boot();
  }, [boot]);

  const cards = useMemo(() => (state ? metricCards(state.metrics) : []), [state]);
  const highlights = useMemo(() => (state ? turnHighlights(state.metrics) : []), [state]);
  const hasCommand = command.trim().length > 0;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!command.trim()) return;
    await runTurn(command);
    setCommand('');
    setPreparedAction(null);
  }

  function handleCommandChange(value: string) {
    setCommand(value);
    setPreparedAction(null);
  }

  function handleQuickCommand(value: string) {
    setCommand(value);
    setPreparedAction(null);
  }

  function handleOfficeAction(action: OfficeAction) {
    setCommand(action.command);
    setPreparedAction(action);
  }

  function clearPreparedAction() {
    setCommand('');
    setPreparedAction(null);
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

      <form onSubmit={handleSubmit} className="mobile-command-strip" aria-label="移动端快捷动作">
        <label htmlFor="mobile-turn-command">移动端本回合指令</label>
        <input
          id="mobile-turn-command"
          value={command}
          onChange={(event) => handleCommandChange(event.target.value)}
          placeholder="例如：花10万研发产品"
        />
            <button type="submit" disabled={submitting}>
              <Play size={18} />
              执行
        </button>
      </form>

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
                <dt>现金</dt>
                <dd className={state.metrics.cash_change >= 0 ? 'good' : 'bad'}>
                  {signed(state.metrics.cash_change) || '稳定'}
                </dd>
              </div>
              <div>
                <dt>月经常收入</dt>
                <dd>{signed(state.metrics.mrr_change) || '观察中'}</dd>
              </div>
              <div>
                <dt>用户</dt>
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

          {lastTurn && (
            <article className="panel result-panel monthly-report">
              <h2>月度战报</h2>
              <strong>第{lastTurn.month}月执行结果</strong>
              <section className="report-block">
                <h3>本月变化</h3>
                <div className="result-grid">
                  {highlights.map((item) => (
                    <span key={item.label}>
                      <b>{item.label}</b>
                      <em className={item.tone}>{item.value}</em>
                    </span>
                  ))}
                </div>
              </section>
              <section className="report-block">
                <h3>原因复盘</h3>
                {lastTurn.delta_reasons?.length ? (
                  <ul className="result-list">
                    {lastTurn.delta_reasons.slice(0, 3).map((reason) => (
                      <li key={reason}>{reason}</li>
                    ))}
                  </ul>
                ) : (
                  <p>本回合已结算，董事会、竞品态势和经营洞察已更新。</p>
                )}
              </section>
              <section className="report-block">
                <h3>下月压力</h3>
                <p>{state.core_tension.next_focus}</p>
              </section>
            </article>
          )}
        </aside>

        <OfficeStage
          focusTitle={state.core_tension.title}
          insightTitle={state.insight.title}
          insightDescription={state.insight.description}
          onActionSelect={handleOfficeAction}
        />

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
              {state.competitors[0] && <em className={`trend-chip ${state.competitors[0].trend}`}>{trendText(state.competitors[0])}</em>}
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
                    <small className="stance-chip">{boardStance(member)}</small>
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
                  <span>{money(item.mrr)} 月经常收入</span>
                  <em className={item.trend}>{trendLabel(item)}</em>
                  <small className={`trend-chip ${item.trend}`}>{trendText(item)}</small>
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
        <button type="button" onClick={() => handleQuickCommand('花10万研发产品')}>
          <Boxes size={22} /> 研发
        </button>
        <button type="button" onClick={() => handleQuickCommand('花8万招聘人才')}>
          <Users size={22} /> 招聘
        </button>
        <button type="button" onClick={() => handleQuickCommand('融资300万出让8%股权')}>
          <HandCoins size={22} /> 融资
        </button>
        <button type="button" onClick={() => handleQuickCommand('花10万做营销推广')}>
          <Megaphone size={22} /> 营销
        </button>
        <div className="command-stack">
          {preparedAction && (
            <article className="prepared-action" aria-label="已准备行动">
              <span>已准备行动</span>
              <strong>{preparedAction.title}</strong>
              <button type="button" aria-label="取消已准备行动" onClick={clearPreparedAction}>
                取消
              </button>
              <p>{preparedAction.description}</p>
              <code>{preparedAction.command}</code>
            </article>
          )}
          {!preparedAction && <p className="command-empty">从办公室选择行动，或直接输入 CEO 指令。</p>}
          <form onSubmit={handleSubmit} className="command-form">
            <label htmlFor="turn-command">本回合指令</label>
            <input
              id="turn-command"
              value={command}
              onChange={(event) => handleCommandChange(event.target.value)}
              placeholder="例如：花10万研发产品"
            />
            <button type="submit" disabled={submitting || !hasCommand}>
              <Play size={20} />
              执行回合
            </button>
          </form>
        </div>
      </section>

      {error && <div className="toast" role="alert">{error}</div>}
    </main>
  );
}
