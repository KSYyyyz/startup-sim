import { demoInitialState, demoSuggestions, demoTurn } from './demo';
import type { GameStateView, SuggestionResponse, TurnResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';
const DEMO_FALLBACK =
  (import.meta.env.VITE_ENABLE_DEMO_FALLBACK ?? (API_BASE ? 'false' : 'true')) !== 'false';

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
  return request<TurnResponse>(`/api/sessions/${sessionId}/turns`, {
    method: 'POST',
    body: JSON.stringify({ command })
  }).catch((error) => {
    if (!DEMO_FALLBACK) throw error;
    return demoTurn(command);
  });
}

export function loadSuggestions(sessionId: number): Promise<SuggestionResponse> {
  return request<SuggestionResponse>(`/api/sessions/${sessionId}/suggestions`).catch((error) => {
    if (!DEMO_FALLBACK) throw error;
    return demoSuggestions;
  });
}
