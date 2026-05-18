type PixiOverlayRoom = {
  x: number;
  y: number;
};

export function mountOfficePixiOverlay(container: HTMLDivElement, rooms: PixiOverlayRoom[] = []) {
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
        for (const room of rooms) {
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
