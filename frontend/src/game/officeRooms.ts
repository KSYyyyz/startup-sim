import { Boxes, HandCoins, Megaphone, Server, Users } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type OfficeAction = {
  title: string;
  description: string;
  command: string;
  impact: string;
  tags: string[];
};

export type OfficeRoom = {
  id: string;
  name: string;
  tone: string;
  x: number;
  y: number;
  icon: LucideIcon;
  actions: OfficeAction[];
};

export const officeRooms: OfficeRoom[] = [
  {
    id: 'product',
    name: '产品室',
    tone: 'product',
    x: 48,
    y: 18,
    icon: Boxes,
    actions: [
      {
        title: '产品打磨',
        description: '现金消耗中等，产品体验提升。',
        command: '花10万研发产品',
        impact: '适合早期补齐核心体验，降低技术孤岛风险。',
        tags: ['产品 +', '现金 -']
      },
      {
        title: '研发冲刺',
        description: '现金消耗较高，产品提升更快。',
        command: '花25万研发产品提升竞争力',
        impact: '适合抢窗口，但会缩短现金流可支撑时间。',
        tags: ['产品 ++', '现金 --']
      }
    ]
  },
  {
    id: 'team',
    name: '研发团队',
    tone: 'team',
    x: 25,
    y: 23,
    icon: Users,
    actions: [
      {
        title: '招聘人才',
        description: '固定支出上升，团队产能提升。',
        command: '花8万招聘人才',
        impact: '适合产品和交付都开始吃紧的时候。',
        tags: ['团队 +', '固定支出 +']
      }
    ]
  },
  {
    id: 'sales',
    name: '销售区',
    tone: 'sales',
    x: 53,
    y: 66,
    icon: Megaphone,
    actions: [
      {
        title: '增长投放',
        description: '获客变快，但需要产品承接。',
        command: '花10万做营销推广',
        impact: '适合产品已有基本体验后扩大市场信号。',
        tags: ['用户 +', '现金 -']
      }
    ]
  },
  {
    id: 'board',
    name: '董事会',
    tone: 'board',
    x: 73,
    y: 32,
    icon: HandCoins,
    actions: [
      {
        title: '融资沟通',
        description: '补充现金，但会稀释股权。',
        command: '融资300万出让8%股权',
        impact: '适合现金流紧张或准备加速扩张时。',
        tags: ['现金 +', '股权 -']
      }
    ]
  },
  {
    id: 'servers',
    name: '服务器',
    tone: 'server',
    x: 77,
    y: 65,
    icon: Server,
    actions: [
      {
        title: '稳定性投入',
        description: '短期不拉增长，但减少交付风险。',
        command: '花6万优化服务器稳定性',
        impact: '适合用户增长后控制故障和口碑损失。',
        tags: ['稳定性 +', '现金 -']
      }
    ]
  }
];
