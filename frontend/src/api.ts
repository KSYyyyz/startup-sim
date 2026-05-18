import { demoCommandPreview, demoInitialState, demoSuggestions, demoTurn } from './demo';
import type { CommandPreviewResponse, GameReviewResponse, GameStateView, SuggestionResponse, TurnResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';
const DEMO_FALLBACK =
  (import.meta.env.VITE_ENABLE_DEMO_FALLBACK ?? (API_BASE ? 'false' : 'true')) !== 'false';

function shouldUseDirectDemoFallback() {
  const hostname = globalThis.location?.hostname ?? '';
  return (
    DEMO_FALLBACK &&
    !API_BASE &&
    hostname.length > 0 &&
    !['localhost', '127.0.0.1', '::1'].includes(hostname)
  );
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {})
    },
    ...options
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message ?? '请求失败');
  }
  return payload as T;
}

export function createSession(): Promise<GameStateView> {
  if (shouldUseDirectDemoFallback()) return Promise.resolve(demoInitialState);
  return request<GameStateView>('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({
      player_name: 'Player',
      company_name: 'NimbusAI'
    })
  }).catch((error) => {
    if (!DEMO_FALLBACK) throw error;
    return demoInitialState;
  });
}

export function submitTurn(sessionId: number, command: string): Promise<TurnResponse> {
  if (shouldUseDirectDemoFallback()) return Promise.resolve(demoTurn(command));
  return request<TurnResponse>(`/api/sessions/${sessionId}/turns`, {
    method: 'POST',
    body: JSON.stringify({ command })
  }).catch((error) => {
    if (!DEMO_FALLBACK) throw error;
    return demoTurn(command);
  });
}

export function loadSuggestions(sessionId: number): Promise<SuggestionResponse> {
  if (shouldUseDirectDemoFallback()) return Promise.resolve(demoSuggestions);
  return request<SuggestionResponse>(`/api/sessions/${sessionId}/suggestions`).catch((error) => {
    if (!DEMO_FALLBACK) throw error;
    return demoSuggestions;
  });
}

export async function loadReview(sessionId: number): Promise<GameReviewResponse | null> {
  if (shouldUseDirectDemoFallback()) return null;
  try {
    const response = await fetch(`${API_BASE}/api/sessions/${sessionId}/review`, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const payload = await response.json();
    if (response.status === 404) return null;
    if (!response.ok) {
      throw new Error(payload.message ?? '复盘加载失败');
    }
    return payload as GameReviewResponse;
  } catch (error) {
    if (!DEMO_FALLBACK) throw error;
    return null;
  }
}

export function previewCommand(sessionId: number, command: string): Promise<CommandPreviewResponse> {
  if (shouldUseDirectDemoFallback()) return Promise.resolve(demoCommandPreview(command));
  return request<CommandPreviewResponse>(`/api/sessions/${sessionId}/command-preview`, {
    method: 'POST',
    body: JSON.stringify({ command })
  }).catch((error) => {
    if (!DEMO_FALLBACK) throw error;
    return demoCommandPreview(command);
  });
}
