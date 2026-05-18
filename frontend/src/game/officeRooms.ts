import { Boxes, HandCoins, Megaphone, Server, Users } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

import { gameplayRooms, type GameplayActionDefinition } from './gameplayContent';

export type OfficeAction = GameplayActionDefinition;

export type OfficeRoom = {
  id: string;
  name: string;
  tone: string;
  x: number;
  y: number;
  icon: LucideIcon;
  actions: OfficeAction[];
};

const roomIcons: Record<string, LucideIcon> = {
  product: Boxes,
  team: Users,
  sales: Megaphone,
  board: HandCoins,
  servers: Server
};

export const officeRooms: OfficeRoom[] = gameplayRooms.map((room) => ({
  id: room.id,
  name: room.name,
  tone: room.tone,
  x: room.position.x,
  y: room.position.y,
  icon: roomIcons[room.id] ?? Boxes,
  actions: room.actions
}));
