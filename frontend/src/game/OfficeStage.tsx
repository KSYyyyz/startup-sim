import { useEffect, useMemo, useRef, useState } from 'react';

import type { OfficeEventBubble, RoomStatus } from './gameplayContent';
import { officeRooms, type OfficeAction, type OfficeRoom } from './officeRooms';
import { mountOfficePixiOverlay } from './pixiOverlay';

type OfficeStageProps = {
  focusTitle: string;
  insightTitle: string;
  insightDescription: string;
  boardSignal: string;
  competitorSignal: string;
  pulseRoomId: string;
  pulseText: string;
  resultHighlights: Array<{
    label: string;
    value: string;
    tone: string;
  }>;
  roomStatuses: Record<string, RoomStatus>;
  officeEvents: OfficeEventBubble[];
  onBoardSignalSelect: () => void;
  onCompetitorSignalSelect: () => void;
  onActionSelect: (action: OfficeAction) => void;
};

export function OfficeStage({
  focusTitle,
  insightTitle,
  insightDescription,
  boardSignal,
  competitorSignal,
  pulseRoomId,
  pulseText,
  resultHighlights,
  roomStatuses,
  officeEvents,
  onBoardSignalSelect,
  onCompetitorSignalSelect,
  onActionSelect
}: OfficeStageProps) {
  const stageRef = useRef<HTMLDivElement | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState(officeRooms[0].id);
  const selectedRoom = useMemo<OfficeRoom>(
    () => officeRooms.find((room) => room.id === selectedRoomId) ?? officeRooms[0],
    [selectedRoomId]
  );

  useEffect(() => {
    if (!stageRef.current) return undefined;
    return mountOfficePixiOverlay(stageRef.current, officeRooms);
  }, []);

  return (
    <section className="office-stage" aria-label="互动办公室场景" ref={stageRef}>
      <img src="/assets/scenes/office-command-center-v0.1.jpg" alt="NimbusAI office command center" />
      <div className="office-bubble" aria-label="办公室提示">
        <span>本月焦点</span>
        <strong>{focusTitle}</strong>
      </div>
      <div className="office-feedback" aria-label="办公室动态反馈">
        <span>动态反馈</span>
        <button type="button" aria-label={`查看董事会信号：${boardSignal}`} onClick={onBoardSignalSelect}>
          <strong>{boardSignal}</strong>
        </button>
        <button type="button" aria-label={`查看竞品信号：${competitorSignal}`} onClick={onCompetitorSignalSelect}>
          <small>{competitorSignal}</small>
        </button>
      </div>
      {resultHighlights.length > 0 && (
        <div className="office-result-pulses" aria-label="办公室月末变化">
          <span>月末变化</span>
          {resultHighlights.map((item) => (
            <strong className={item.tone} key={item.label}>
              {item.label} {item.value}
            </strong>
          ))}
        </div>
      )}
      <div className="room-hotspots" aria-label="可操作房间">
        {officeRooms.map((room) => {
          const Icon = room.icon;
          const roomStatus = roomStatuses[room.id] ?? { tone: 'normal', label: '运转中' };
          return (
            <div className="room-hotspot-wrap" key={room.id} style={{ left: `${room.x}%`, top: `${room.y}%` }}>
              <button
                className={`room-hotspot ${room.tone} ${room.id === selectedRoomId ? 'active' : ''}`}
                aria-pressed={room.id === selectedRoomId}
                onClick={() => setSelectedRoomId(room.id)}
                type="button"
              >
                <Icon size={18} aria-hidden="true" />
                <span>{room.name}</span>
              </button>
              {room.id === pulseRoomId && (
                <span className="room-pulse" aria-label={`${room.name}状态`}>
                  {pulseText}
                </span>
              )}
              <span className={`room-status ${roomStatus.tone}`} aria-label={`${room.name}经营状态`}>
                {roomStatus.label}
              </span>
            </div>
          );
        })}
      </div>
      <div className="office-event-layer" aria-label="办公室事件">
        {officeEvents.map((event) => {
          const room = officeRooms.find((item) => item.id === event.roomId) ?? officeRooms[0];
          const handleClick =
            event.action === 'board'
              ? onBoardSignalSelect
              : event.action === 'competitor'
                ? onCompetitorSignalSelect
                : undefined;
          const eventNode = (
            <>
              <strong>{event.title}</strong>
              <span>{event.tone === 'board' ? '董事会' : event.tone === 'competitor' ? '竞品' : '洞察'}</span>
            </>
          );
          return handleClick ? (
            <button
              className={`office-event-bubble ${event.tone}`}
              key={event.id}
              style={{ left: `${room.x}%`, top: `${room.y + 10}%` }}
              title={event.description}
              type="button"
              onClick={handleClick}
            >
              {eventNode}
            </button>
          ) : (
            <span
              className={`office-event-bubble ${event.tone}`}
              key={event.id}
              style={{ left: `${room.x}%`, top: `${room.y + 10}%` }}
              title={event.description}
            >
              {eventNode}
            </span>
          );
        })}
      </div>
      <div className="room-action-panel" aria-label="办公室操作台" aria-live="polite">
        <span className="room-kicker">选中房间</span>
        <strong>{selectedRoom.name}</strong>
        <div className="action-card-list">
          {selectedRoom.actions.map((action) => (
            <article className="room-action-card" key={action.title}>
              <b>{action.title}</b>
              <div className="action-tags" aria-label={`${action.title}取舍`}>
                {action.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
              <p>{action.description}</p>
              <small>{action.impact}</small>
              <button type="button" onClick={() => onActionSelect(action)}>
                采用行动：{action.title}
              </button>
            </article>
          ))}
        </div>
      </div>
      <div className="insight-strip">
        <strong>{insightTitle}</strong>
        <span>{insightDescription}</span>
      </div>
    </section>
  );
}
