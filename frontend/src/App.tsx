import { useEffect, useMemo, useState } from 'react';
import {
  BarChart3,
  Bot,
  Boxes,
  CalendarDays,
  ChartNoAxesCombined,
  CircleDollarSign,
  HandCoins,
  Megaphone,
  Play,
  Settings,
  Users
} from 'lucide-react';

import { OfficeStage } from './game/OfficeStage';
import {
  buildBoardPressureResponse,
  buildBoardNpcProfiles,
  buildCompetitorPressureResponse,
  buildCompetitorMoves,
  buildMonthlyReport,
  buildTurnResolutionSteps,
  commandTradeoffs,
  prepareAction,
  quickActionShortcuts,
  type PreparedAction,
  resolveOfficePulse,
  resolveRoomStatuses,
  type QuickActionShortcut
} from './game/gameplayContent';
import type { OfficeAction } from './game/officeRooms';
import { builtinScenarios } from './game/scenarios';
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

const quickActionIcons = {
  boxes: Boxes,
  users: Users,
  'hand-coins': HandCoins,
  megaphone: Megaphone
} satisfies Record<QuickActionShortcut['iconKey'], typeof Boxes>;

const activeScenario = builtinScenarios[0];

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

export default function App() {
  const { state, suggestions, lastTurn, loading, submitting, error, boot, runTurn, openSuggestions } =
    useGameStore();
  const [command, setCommand] = useState('');
  const [lastCommand, setLastCommand] = useState('');
  const [preparedAction, setPreparedAction] = useState<PreparedAction | null>(null);
  const [rightTab, setRightTab] = useState<'board' | 'competitors' | 'advice' | 'log'>('board');

  useEffect(() => {
    void boot();
  }, [boot]);

  const cards = useMemo(() => (state ? metricCards(state.metrics) : []), [state]);
  const highlights = useMemo(() => (state ? turnHighlights(state.metrics) : []), [state]);
  const hasCommand = command.trim().length > 0;
  const pulse = useMemo(
    () =>
      state
        ? resolveOfficePulse({
            title: state.core_tension.title,
            description: state.core_tension.description,
            insightTitle: state.insight.title
          })
        : { roomId: 'product', text: '产品压力' },
    [state]
  );
  const roomStatuses = useMemo(
    () =>
      state
        ? resolveRoomStatuses({
            cashCoverageMonths: state.metrics.cash_coverage_months,
            productChange: state.metrics.product_change,
            usersChange: state.metrics.users_change,
            mrrChange: state.metrics.mrr_change,
            signalText: `${state.core_tension.title} ${state.core_tension.description} ${state.insight.title} ${state.insight.description}`
          })
        : {},
    [state]
  );
  const boardProfiles = useMemo(
    () =>
      state
        ? buildBoardNpcProfiles({
            members: state.board,
            cashCoverageMonths: state.metrics.cash_coverage_months,
            productChange: state.metrics.product_change,
            usersChange: state.metrics.users_change
          })
        : [],
    [state]
  );
  const competitorMoves = useMemo(() => (state ? buildCompetitorMoves(state.competitors) : []), [state]);
  const monthlyReport = useMemo(
    () =>
      state && lastTurn
        ? buildMonthlyReport({
            month: lastTurn.month,
            highlights,
            reasons: lastTurn.delta_reasons,
            nextPressure: state.core_tension.next_focus,
            cashChange: state.metrics.cash_change,
            productChange: state.metrics.product_change,
            usersChange: state.metrics.users_change
          })
        : null,
    [highlights, lastTurn, state]
  );
  const turnResolutionSteps = useMemo(
    () =>
      monthlyReport && lastCommand
        ? buildTurnResolutionSteps({
            command: lastCommand,
            highlights,
            reportHeadline: monthlyReport.headline
          })
        : [],
    [highlights, lastCommand, monthlyReport]
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!command.trim()) return;
    const submittedCommand = command.trim();
    setLastCommand(submittedCommand);
    await runTurn(submittedCommand);
    setCommand('');
    setPreparedAction(null);
  }

  function handleCommandChange(value: string) {
    setCommand(value);
    setPreparedAction(null);
  }

  function handleQuickAction(action: QuickActionShortcut) {
    setCommand(action.command);
    setPreparedAction(prepareAction(action, { id: action.id, source: 'quick', sourceLabel: '快捷行动' }));
  }

  function handleOfficeAction(action: OfficeAction) {
    setCommand(action.command);
    setPreparedAction(prepareAction(action, { id: `room-${action.title}`, source: 'room', sourceLabel: '办公室行动' }));
  }

  function clearPreparedAction() {
    setCommand('');
    setPreparedAction(null);
  }

  function handleBoardResponse(member: { name: string; role: string; message: string }) {
    const response = buildBoardPressureResponse(member);
    setCommand(response.command);
    setPreparedAction(response);
  }

  function handleCompetitorResponse(item: CompetitorItem) {
    const response = buildCompetitorPressureResponse(item);
    setCommand(response.command);
    setPreparedAction(response);
  }

  function handleMonthlyRecovery() {
    if (!monthlyReport) return;
    const action = monthlyReport.recoveryAction;
    setCommand(action.command);
    setPreparedAction(
      prepareAction(
        {
          title: action.label,
          description: action.description,
          impact: '现金流可支撑时间 + / 风险 -',
          command: action.command,
          tags: commandTradeoffs(action.command)
        },
        { id: `monthly-${lastTurn?.month ?? 'latest'}`, source: 'quick', sourceLabel: '月报行动' }
      )
    );
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

          <details className="panel scenario-entry" aria-label="当前剧本">
            <summary>
              <span>{activeScenario.menu.statusLabel}</span>
              <div>
                <h2>当前剧本</h2>
                <strong>{activeScenario.menu.title}</strong>
                <small>难度：{activeScenario.menu.difficulty}</small>
              </div>
            </summary>
            <p>{activeScenario.menu.subtitle}</p>
            <div className="scenario-tags">
              {activeScenario.menu.featureTags.map((tag) => (
                <b key={tag}>{tag}</b>
              ))}
            </div>
          </details>

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
            <div className="insight-note">
              <b>经营洞察</b>
              <span>{state.insight.title}</span>
              <p>{state.insight.description}</p>
            </div>
          </article>

          {monthlyReport && (
            <article className="panel result-panel monthly-report">
              <h2>月度战报</h2>
              {turnResolutionSteps.length > 0 && (
                <section className="resolution-timeline" aria-label="回合结算">
                  <h3>回合结算</h3>
                  {turnResolutionSteps.map((step) => (
                    <div className={`resolution-step ${step.tone}`} key={step.title}>
                      <b>{step.title}</b>
                      <span>{step.detail}</span>
                    </div>
                  ))}
                </section>
              )}
              <strong>{monthlyReport.title}</strong>
              <p className="report-headline">{monthlyReport.headline}</p>
              <section className="report-block">
                <h3>本月变化</h3>
                <div className="result-grid">
                  {monthlyReport.highlightCards.map((item) => (
                    <span key={item.label}>
                      <b>{item.label}</b>
                      <em className={item.tone}>{item.value}</em>
                    </span>
                  ))}
                </div>
              </section>
              <section className="report-block">
                <h3>原因复盘</h3>
                <ul className="result-list">
                  {monthlyReport.reviewLines.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              </section>
              <section className="report-block">
                <h3>下月压力</h3>
                <p>{monthlyReport.nextPressure}</p>
              </section>
              <section className="report-block report-recovery">
                <h3>{monthlyReport.recoveryAction.label}</h3>
                <p>{monthlyReport.recoveryAction.description}</p>
                <button type="button" onClick={handleMonthlyRecovery}>
                  采用补救行动
                </button>
              </section>
            </article>
          )}
        </aside>

        <OfficeStage
          focusTitle={state.core_tension.title}
          pulseRoomId={pulse.roomId}
          pulseText={pulse.text}
          resultHighlights={lastTurn ? highlights : []}
          roomStatuses={roomStatuses}
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

          {rightTab === 'board' && (
            <article className="panel tall-panel">
              <h2>董事会反馈</h2>
              {boardProfiles.map((member) => (
                <div className="board-row" key={member.name}>
                  <div className="avatar">{member.name.slice(0, 1)}</div>
                  <div>
                    <strong>{member.name}</strong>
                    <div className="board-profile-line">
                      <small className="stance-chip">{member.stance}</small>
                      <small className={`trust-chip ${member.trustTrend === '信任承压' ? 'strained' : ''}`}>
                        {member.trustTrend}
                      </small>
                    </div>
                    <span>{member.role}</span>
                    <div className="board-pressure-tags" aria-label={`${member.name}压力标签`}>
                      {member.pressureTags.map((tag) => (
                        <small key={tag}>{tag}</small>
                      ))}
                    </div>
                    <p>{member.message}</p>
                    <button type="button" className="board-response-button" onClick={() => handleBoardResponse(member)}>
                      回应 {member.name} 压力
                    </button>
                  </div>
                  <em>{member.confidence}</em>
                </div>
              ))}
            </article>
          )}

          {rightTab === 'competitors' && (
            <article className="panel tall-panel" aria-label="竞品态势">
              <h2>竞品态势</h2>
              {competitorMoves.map((item) => (
                <div className="competitor-row" key={item.name}>
                  <strong>{item.name}</strong>
                  <small className="competitor-move-chip">{item.moveType}</small>
                  <span>{money(item.mrr)} 月经常收入</span>
                  <em className={item.trend}>{trendLabel(item)}</em>
                  <small className={`trend-chip ${item.trend}`}>{trendText(item)}</small>
                  <p>{item.status}</p>
                  <p className="competitor-move-reason">{item.reason}</p>
                  <code className="competitor-command">{item.responseCommand}</code>
                  <button
                    type="button"
                    className="competitor-response-button"
                    onClick={() => handleCompetitorResponse(item)}
                  >
                    回应{item.name}压力
                  </button>
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
        {quickActionShortcuts.map((action) => {
          const Icon = quickActionIcons[action.iconKey];
          return (
            <button type="button" onClick={() => handleQuickAction(action)} key={action.id}>
              <Icon size={22} /> {action.title}
            </button>
          );
        })}
        <div className="command-stack">
          {preparedAction && (
            <article className="prepared-action" aria-label="已准备行动">
              <span>已准备行动</span>
              <strong>{preparedAction.title}</strong>
              <button type="button" aria-label="取消已准备行动" onClick={clearPreparedAction}>
                取消
              </button>
              <p>{preparedAction.description}</p>
              <div className="action-tags" aria-label="已准备行动取舍">
                {preparedAction.tags.map((tag) => (
                  <small key={tag}>{tag}</small>
                ))}
              </div>
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
