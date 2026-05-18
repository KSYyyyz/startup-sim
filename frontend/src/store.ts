import { create } from 'zustand';

import { createSession, loadSuggestions, submitTurn } from './api';
import type { GameStateView, SuggestionResponse } from './types';

type GameStore = {
  state: GameStateView | null;
  suggestions: SuggestionResponse | null;
  loading: boolean;
  submitting: boolean;
  error: string;
  boot: () => Promise<void>;
  runTurn: (command: string) => Promise<void>;
  openSuggestions: () => Promise<void>;
};

export const useGameStore = create<GameStore>((set, get) => ({
  state: null,
  suggestions: null,
  loading: false,
  submitting: false,
  error: '',
  async boot() {
    if (get().state || get().loading) return;
    set({ loading: true, error: '' });
    try {
      const state = await createSession();
      set({ state, loading: false });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '启动失败', loading: false });
    }
  },
  async runTurn(command: string) {
    const current = get().state;
    if (!current) return;
    set({ submitting: true, error: '' });
    try {
      const result = await submitTurn(current.session_id, command);
      set({ state: result.state, submitting: false });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '执行失败', submitting: false });
    }
  },
  async openSuggestions() {
    const current = get().state;
    if (!current) return;
    set({ error: '' });
    try {
      const suggestions = await loadSuggestions(current.session_id);
      set({ suggestions });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '建议加载失败' });
    }
  }
}));
