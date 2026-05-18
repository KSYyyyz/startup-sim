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
  buildPreparedActionPreview,
  buildMonthlyReport,
  buildMonthlyRecoveryAction,
  buildTurnResolutionSteps,
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
import type { CompetitorItem, MetricSet, OfficeSignalPayload, RoleMemoryPayload } from './types';
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

function roomStatusToneFromSignal(signal: OfficeSignalPayload) {
  if (signal.severity === 'critical') return 'blocked';
  if (signal.severity === 'warning' || signal.severity === 'high' || signal.severity === 'medium') return 'warning';
  if (signal.severity === 'opportunity') return 'opportunity';
  return 'normal';
}

function memoryMatchesMember(memory: RoleMemoryPayload, member: { name: string; role: string }) {
  const identity = `${memory.role_id ?? ''} ${memory.role_name ?? ''}`.toLowerCase();
  return identity.includes(member.name.toLowerCase()) || identity.includes(member.role.toLowerCase());
}

function roleMemoryLine(memory: RoleMemoryPayload) {
  return `记忆：${memory.fact}${memory.implication}`;
}

function mostRelevantMemory(memories: RoleMemoryPayload[], members: Array<{ name: string; role: string }>) {
  return memories
    .filter((memory) => members.some((member) => memoryMatchesMember(memory, member)))
    .sort((left, right) => (right.relevance_score ?? 0) - (left.relevance_score ?? 0))[0];
}

export default function App() {
  const {
    state,
    suggestions,
    commandPreview,
    review,
    lastTurn,
    loading,
    submitting,
    previewing,
    reviewing,
    reviewUnavailable,
    error,
    boot,
    runTurn,
    explainCommand,
    clearCommandPreview,
    openSuggestions,
    openReview
  } = useGameStore();
  const [command, setCommand] = useState('');
  const [lastCommand, setLastCommand] = useState('');
  const [preparedAction, setPreparedAction] = useState<PreparedAction | null>(null);
  const [rightTab, setRightTab] = useState<'board' | 'competitors' | 'advice' | 'log'>('board');

  useEffect(() => {
    void boot();
  }, [boot]);

  const cards = useMemo(() => (state ? metricCards(state.metrics) : []), [state]);
  const highlights = useMemo(() => (state ? turnHighlights(state.metrics) : []), [state]);
  const roleMemory = [
    ...(lastTurn?.recent_role_memory ?? []),
    ...(lastTurn?.role_memory ?? []),
    ...(lastTurn?.memory_history ?? [])
  ];
  const officeSignals = lastTurn?.office_signals ?? [];
  const storyEvents = lastTurn?.story_events ?? [];
  const primaryOfficeSignal = officeSignals[0];
  const hasCommand = command.trim().length > 0;
  const pulse = useMemo(
    () =>
      primaryOfficeSignal
        ? { roomId: primaryOfficeSignal.room_id, text: primaryOfficeSignal.title }
        : state
          ? resolveOfficePulse({
              title: state.core_tension.title,
              description: state.core_tension.description,
              insightTitle: state.insight.title
            })
          : { roomId: 'product', text: '产品压力' },
    [primaryOfficeSignal, state]
  );
  const roomStatuses = useMemo(
    () => {
      const statuses = state
        ? resolveRoomStatuses({
            cashCoverageMonths: state.metrics.cash_coverage_months,
            productChange: state.metrics.product_change,
            usersChange: state.metrics.users_change,
            mrrChange: state.metrics.mrr_change,
            signalText: `${state.core_tension.title} ${state.core_tension.description} ${state.insight.title} ${state.insight.description}`
          })
        : {};
      for (const signal of officeSignals) {
        statuses[signal.room_id] = {
          tone: roomStatusToneFromSignal(signal),
          label: signal.title
        };
      }
      return statuses;
    },
    [officeSignals, state]
  );
  const boardProfiles = useMemo(
    () => {
      if (!state) return [];
      const baseProfiles = buildBoardNpcProfiles({
            members: state.board,
            cashCoverageMonths: state.metrics.cash_coverage_months,
            productChange: state.metrics.product_change,
            usersChange: state.metrics.users_change,
            cashChange: lastTurn ? state.metrics.cash_change : undefined,
            lastCommand: lastTurn ? lastCommand : undefined
          });
      const backendMemory = mostRelevantMemory(roleMemory, baseProfiles);
      if (backendMemory) {
        return baseProfiles.map((member) =>
          memoryMatchesMember(backendMemory, member)
            ? { ...member, memoryFact: roleMemoryLine(backendMemory) }
            : { ...member, memoryFact: undefined }
        );
      }
      const firstFallbackMemory = baseProfiles.find((member) => member.memoryFact)?.memoryFact;
      let fallbackUsed = false;
      return baseProfiles.map((member) => {
        if (!member.memoryFact || member.memoryFact !== firstFallbackMemory || fallbackUsed) {
          return { ...member, memoryFact: undefined };
        }
        fallbackUsed = true;
        return member;
      });
    },
    [lastCommand, lastTurn, roleMemory, state]
  );
  const competitorMoves = useMemo(() => (state ? buildCompetitorMoves(state.competitors) : []), [state]);
  const monthlyFacts = lastTurn?.turn_facts;
  const monthlyHighlights = useMemo(
    () =>
      monthlyFacts
        ? monthlyFacts.changes.map((change) => ({
            label: change.label,
            value: change.value,
            tone: change.tone
          }))
        : highlights,
    [highlights, monthlyFacts]
  );
  const monthlyReport = useMemo(
    () =>
      state && lastTurn
        ? buildMonthlyReport({
            month: lastTurn.month,
            highlights: monthlyHighlights,
            reasons: monthlyFacts?.replay_basis ?? lastTurn.delta_reasons,
            nextPressure: monthlyFacts?.next_pressure ?? state.core_tension.next_focus,
            command: monthlyFacts?.command ?? lastCommand,
            cashChange: state.metrics.cash_change,
            productChange: state.metrics.product_change,
            usersChange: state.metrics.users_change
          })
        : null,
    [lastCommand, lastTurn, monthlyFacts, monthlyHighlights, state]
  );
  const turnResolutionSteps = useMemo(
    () =>
      monthlyReport && (monthlyFacts?.command ?? lastCommand)
        ? buildTurnResolutionSteps({
            command: monthlyFacts?.command ?? lastCommand,
            highlights: monthlyHighlights,
            reportHeadline: monthlyReport.headline
          })
        : [],
    [lastCommand, monthlyFacts, monthlyHighlights, monthlyReport]
  );
  const executionPreview = useMemo(
    () => commandPreview ?? (preparedAction ? buildPreparedActionPreview(preparedAction) : null),
    [commandPreview, preparedAction]
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!command.trim()) return;
    const submittedCommand = command.trim();
    setLastCommand(submittedCommand);
    await runTurn(submittedCommand);
    setCommand('');
    setPreparedAction(null);
    clearCommandPreview();
  }

  function handleCommandChange(value: string) {
    setCommand(value);
    setPreparedAction(null);
    clearCommandPreview();
  }

  function handleQuickAction(action: QuickActionShortcut) {
    setCommand(action.command);
    clearCommandPreview();
    setPreparedAction(prepareAction(action, { id: action.id, source: 'quick', sourceLabel: '快捷行动' }));
  }

  function handleOfficeAction(action: OfficeAction) {
    setCommand(action.command);
    clearCommandPreview();
    setPreparedAction(prepareAction(action, { id: `room-${action.title}`, source: 'room', sourceLabel: '办公室行动' }));
  }

  function clearPreparedAction() {
    setCommand('');
    setPreparedAction(null);
    clearCommandPreview();
  }

  function handleBoardResponse(member: { name: string; role: string; message: string }) {
    const response = buildBoardPressureResponse(member);
    setCommand(response.command);
    clearCommandPreview();
    setPreparedAction(response);
  }

  function handleCompetitorResponse(item: CompetitorItem) {
    const response = buildCompetitorPressureResponse(item);
    setCommand(response.command);
    clearCommandPreview();
    setPreparedAction(response);
  }

  function handleMonthlyRecovery() {
    if (!monthlyReport) return;
    const action = monthlyReport.recoveryAction;
    setCommand(action.command);
    clearCommandPreview();
    setPreparedAction(buildMonthlyRecoveryAction(monthlyReport, lastTurn?.month ?? 0));
  }

  async function handleAdvice() {
    setRightTab('advice');
    if (!suggestions) {
      await openSuggestions();
    }
  }

  async function handleExplainCommand() {
    if (!command.trim()) return;
    await explainCommand(command);
  }

  async function handleReview() {
    await openReview();
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
        <button
          type="button"
          aria-label="移动端解释指令"
          disabled={previewing || !hasCommand}
          onClick={handleExplainCommand}
        >
          解释
        </button>
        <button type="submit" aria-label="移动端执行" disabled={submitting || !hasCommand}>
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
              <section className="report-block fact-citations" aria-label="月报事实依据">
                <h3>事实依据</h3>
                {monthlyReport.factCitations.map((fact) => (
                  <span key={fact.label}>
                    <b>{fact.label}</b>
                    <em>{fact.value}</em>
                  </span>
                ))}
              </section>
              <section className="report-block review-entry" aria-label="轻量复盘入口">
                <h3>轻量复盘</h3>
                <button type="button" onClick={handleReview} disabled={reviewing}>
                  {reviewing ? '加载复盘中' : '查看轻量复盘'}
                </button>
                {reviewUnavailable && <p>复盘接口暂未开放。</p>}
                {review && (
                  <div aria-label="轻量复盘">
                    <b>{review.ending_title ?? '本局复盘'}</b>
                    {review.ending_summary && <p>{review.ending_summary}</p>}
                    {review.key_moments?.[0] && (
                      <span>
                        {review.key_moments[0].title}：{review.key_moments[0].description}
                      </span>
                    )}
                    {review.advice_for_next_run && <small>{review.advice_for_next_run}</small>}
                  </div>
                )}
              </section>
              {storyEvents.length > 0 && (
                <section className="report-block story-events" aria-label="本月事件">
                  <h3>本月事件</h3>
                  {storyEvents.slice(0, 3).map((event) => (
                    <article className={`story-event ${event.tone}`} key={event.id}>
                      <b>{event.title}</b>
                      <span>{event.description}</span>
                    </article>
                  ))}
                </section>
              )}
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
          focusTitle={primaryOfficeSignal?.title ?? state.core_tension.title}
          pulseRoomId={pulse.roomId}
          pulseText={pulse.text}
          resultHighlights={lastTurn ? highlights : []}
          officeSignals={officeSignals}
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
                    {member.memoryFact && <p className="board-memory">{member.memoryFact}</p>}
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
          {executionPreview && (
            <article className="command-preview compact" aria-label="AI 指令解释">
              <span>AI 指令解释</span>
              <strong>{executionPreview.summary}</strong>
              <div className="preview-action-list">
                {executionPreview.actions.map((action) => (
                  <div className="preview-action-row" key={`${action.type}-${action.intent}-${action.budget}`}>
                    <b>{action.label}</b>
                    <small>{action.budget_label}</small>
                    <em>{action.risk_label}</em>
                    <p>{action.intent}</p>
                    <div className="action-tags" aria-label={`${action.label}预期取舍`}>
                      {action.tradeoffs.map((tag) => (
                        <small key={tag}>{tag}</small>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <p>{executionPreview.guardrail}</p>
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
            <button type="button" className="explain-command-button" disabled={previewing || !hasCommand} onClick={handleExplainCommand}>
              解释指令
            </button>
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
