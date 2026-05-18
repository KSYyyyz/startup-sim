import { create } from 'zustand';

import { createSession, loadSuggestions, previewCommand, submitTurn } from './api';
import type { CommandPreviewResponse, GameStateView, SuggestionResponse, TurnResponse } from './types';

type GameStore = {
  state: GameStateView | null;
  suggestions: SuggestionResponse | null;
  commandPreview: CommandPreviewResponse | null;
  lastTurn: TurnResponse['turn'] | null;
  loading: boolean;
  submitting: boolean;
  previewing: boolean;
  error: string;
  boot: () => Promise<void>;
  runTurn: (command: string) => Promise<void>;
  explainCommand: (command: string) => Promise<void>;
  clearCommandPreview: () => void;
  openSuggestions: () => Promise<void>;
};

export const useGameStore = create<GameStore>((set, get) => ({
  state: null,
  suggestions: null,
  commandPreview: null,
  lastTurn: null,
  loading: false,
  submitting: false,
  previewing: false,
  error: '',
  async boot() {
    if (get().state || get().loading) return;
    set({ loading: true, error: '' });
    try {
      const state = await createSession();
      set({ state, lastTurn: null, commandPreview: null, loading: false });
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
      set({
        state: result.state,
        lastTurn: {
          ...result.turn,
          turn_facts: result.turn.turn_facts ?? result.turn_facts,
          role_memory: result.turn.role_memory ?? result.role_memory,
          office_signals: result.turn.office_signals ?? result.office_signals,
          story_events: result.turn.story_events ?? result.story_events
        },
        suggestions: null,
        commandPreview: null,
        submitting: false
      });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '执行失败', submitting: false });
    }
  },
  async explainCommand(command: string) {
    const current = get().state;
    const cleanCommand = command.trim();
    if (!current || !cleanCommand) return;
    set({ previewing: true, error: '' });
    try {
      const commandPreview = await previewCommand(current.session_id, cleanCommand);
      set({ commandPreview, previewing: false });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '指令解释失败', previewing: false });
    }
  },
  clearCommandPreview() {
    set({ commandPreview: null });
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
