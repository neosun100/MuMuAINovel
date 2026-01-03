// 伏笔类型定义
export interface Foreshadow {
  id: string;
  project_id: string;
  title: string;
  description: string;
  foreshadow_type: 'character' | 'plot' | 'item' | 'setting' | 'relationship';
  status: 'planted' | 'hinted' | 'resolved' | 'abandoned';
  importance: number;
  planted_chapter_id?: string;
  planted_chapter_number?: number;
  planted_content?: string;
  planted_at?: string;
  resolved_chapter_id?: string;
  resolved_chapter_number?: number;
  resolved_content?: string;
  resolved_at?: string;
  related_characters: string[];
  related_foreshadows: string[];
  tags: string[];
  remind_before_chapters: number;
  auto_remind: boolean;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ForeshadowListResponse {
  items: Foreshadow[];
  total: number;
  planted_count: number;
  resolved_count: number;
  pending_count: number;
}

export interface ForeshadowReminder {
  foreshadow_id: string;
  title: string;
  description: string;
  planted_chapter_number: number;
  expected_resolve_chapter: number;
  current_chapter: number;
  chapters_remaining: number;
  importance: number;
  related_characters: string[];
}

export interface ForeshadowReminderResponse {
  reminders: ForeshadowReminder[];
  total: number;
}

export interface ForeshadowCreate {
  project_id: string;
  title: string;
  description: string;
  foreshadow_type?: 'character' | 'plot' | 'item' | 'setting' | 'relationship';
  importance?: number;
  planted_chapter_id?: string;
  planted_chapter_number?: number;
  planted_content?: string;
  resolved_chapter_number?: number;
  related_characters?: string[];
  tags?: string[];
  remind_before_chapters?: number;
  auto_remind?: boolean;
  notes?: string;
}

export interface ForeshadowUpdate {
  title?: string;
  description?: string;
  foreshadow_type?: 'character' | 'plot' | 'item' | 'setting' | 'relationship';
  status?: 'planted' | 'hinted' | 'resolved' | 'abandoned';
  importance?: number;
  planted_chapter_id?: string;
  planted_chapter_number?: number;
  planted_content?: string;
  resolved_chapter_id?: string;
  resolved_chapter_number?: number;
  resolved_content?: string;
  related_characters?: string[];
  related_foreshadows?: string[];
  tags?: string[];
  remind_before_chapters?: number;
  auto_remind?: boolean;
  notes?: string;
}

export interface ResolveForeshadowRequest {
  resolved_chapter_id?: string;
  resolved_chapter_number: number;
  resolved_content?: string;
  notes?: string;
}
