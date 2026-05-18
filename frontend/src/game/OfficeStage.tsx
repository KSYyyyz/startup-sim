import { useEffect, useMemo, useRef, useState } from 'react';

import { officeRooms, type OfficeAction, type OfficeRoom } from './officeRooms';

type OfficeStageProps = {
  insightTitle: string;
  insightDescription: string;
  onActionSelect: (action: OfficeAction) => void;
};

function drawPixiOverlay(container: HTMLDivElement) {
  if (import.meta.env.MODE === 'test') {
    return () => {};
  }

  let disposed = false;
  let appRef: { destroy: (removeView?: boolean) => void } | null = null;

  void import('pixi.js')
    .then(async ({ Application, Graphics }) => {
      if (disposed) return;
      const app = new Application();
      await app.init({
        resizeTo: container,
        backgroundAlpha: 0,
        antialias: true
      });
      if (disposed) {
        app.destroy(true);
        return;
      }
      appRef = app;
      app.canvas.className = 'office-pixi-canvas';
      app.canvas.setAttribute('aria-hidden', 'true');
      container.prepend(app.canvas);

      const draw = () => {
        app.stage.removeChildren();
        const width = Math.max(1, app.renderer.width);
        const height = Math.max(1, app.renderer.height);
        for (const room of officeRooms) {
          const marker = new Graphics();
          const px = (room.x / 100) * width;
          const py = (room.y / 100) * height;
          marker.circle(px, py, 18);
          marker.fill({ color: 0x2f6db3, alpha: 0.18 });
          marker.stroke({ color: 0xffffff, alpha: 0.55, width: 2 });
          app.stage.addChild(marker);
        }
      };

      draw();
      app.renderer.on('resize', draw);
    })
    .catch(() => {
      // Canvas support is optional in tests and older browsers; React hotspots remain usable.
    });

  return () => {
    disposed = true;
    appRef?.destroy(true);
  };
}

export function OfficeStage({ insightTitle, insightDescription, onActionSelect }: OfficeStageProps) {
  const stageRef = useRef<HTMLDivElement | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState(officeRooms[0].id);
  const selectedRoom = useMemo<OfficeRoom>(
    () => officeRooms.find((room) => room.id === selectedRoomId) ?? officeRooms[0],
    [selectedRoomId]
  );

  useEffect(() => {
    if (!stageRef.current) return undefined;
    return drawPixiOverlay(stageRef.current);
  }, []);

  return (
    <section className="office-stage" aria-label="互动办公室场景" ref={stageRef}>
      <img src="/assets/scenes/office-command-center-v0.1.jpg" alt="NimbusAI office command center" />
      <div className="room-hotspots" aria-label="可操作房间">
        {officeRooms.map((room) => {
          const Icon = room.icon;
          return (
            <button
              className={`room-hotspot ${room.tone} ${room.id === selectedRoomId ? 'active' : ''}`}
              aria-pressed={room.id === selectedRoomId}
              key={room.id}
              onClick={() => setSelectedRoomId(room.id)}
              style={{ left: `${room.x}%`, top: `${room.y}%` }}
              type="button"
            >
              <Icon size={18} aria-hidden="true" />
              <span>{room.name}</span>
            </button>
          );
        })}
      </div>
      <div className="room-action-panel" aria-live="polite">
        <span className="room-kicker">当前房间</span>
        <strong>{selectedRoom.name}</strong>
        <div className="action-card-list">
          {selectedRoom.actions.map((action) => (
            <article className="room-action-card" key={action.title}>
              <b>{action.title}</b>
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
