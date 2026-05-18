export function manualChunks(id: string) {
  const normalizedId = id.replace(/\\/g, '/');
  if (normalizedId.includes('/node_modules/pixi.js/') || normalizedId.includes('/node_modules/@pixi/')) {
    return 'pixi-overlay';
  }
  return undefined;
}
