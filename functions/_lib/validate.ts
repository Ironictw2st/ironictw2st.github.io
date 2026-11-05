// Input validation for the roadmap API. Pure functions, no Workers APIs, so they unit-test under plain node.

export const STATUSES = ['live', 'next', 'planned', 'idea'] as const;
export const CATEGORIES = ['Mod', 'Map', 'Script Extender', 'Mod Manager', 'Wiki'] as const;
export type Status = (typeof STATUSES)[number];
export type Category = (typeof CATEGORIES)[number];

export interface ItemInput {
  title: string;
  description: string;
  status: Status;
  category: Category;
  version: string;
  release_date: string;
  draft: 0 | 1;
  progress: number | null; // 0-100, or null when not tracked
  link: string;           // site-internal path such as /total_war/changes.html, or ''
}

export const MAX_BODY_BYTES = 64 * 1024;
export const MAX_REORDER_ITEMS = 500;

export class ValidationError extends Error {
  readonly field: string;
  constructor(field: string, message: string) {
    super(message);
    this.field = field;
  }
}

const CONTROL = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/;

function str(v: unknown, field: string, min: number, max: number, multiline = false): string {
  if (typeof v !== 'string') throw new ValidationError(field, `${field} must be text`);
  const s = v.replace(/\r\n/g, '\n').trim();
  if (s.length < min) throw new ValidationError(field, `${field} is required`);
  if (s.length > max) throw new ValidationError(field, `${field} must be at most ${max} characters`);
  if (CONTROL.test(s) || (!multiline && /[\n\t]/.test(s))) throw new ValidationError(field, `${field} has invalid characters`);
  return s;
}

function oneOf<T extends string>(v: unknown, field: string, allowed: readonly T[]): T {
  if (typeof v !== 'string' || !(allowed as readonly string[]).includes(v)) {
    throw new ValidationError(field, `${field} must be one of: ${allowed.join(', ')}`);
  }
  return v as T;
}

/** Validate a full item (create or update). Throws ValidationError. */
export function parseItem(body: unknown): ItemInput {
  if (typeof body !== 'object' || body === null || Array.isArray(body)) throw new ValidationError('body', 'body must be a JSON object');
  const b = body as Record<string, unknown>;
  const release = b.release_date === undefined || b.release_date === null || b.release_date === '' ? '' : str(b.release_date, 'release_date', 1, 10);
  if (release !== '' && !/^\d{4}(-\d{2}(-\d{2})?)?$/.test(release)) {
    throw new ValidationError('release_date', 'release_date must look like 2026, 2026-11 or 2026-11-05');
  }
  const version = b.version === undefined || b.version === null || b.version === '' ? '' : str(b.version, 'version', 0, 20);
  const description = b.description === undefined || b.description === null || b.description === '' ? '' : str(b.description, 'description', 0, 280, true);
  const draftRaw = b.draft === undefined ? 0 : b.draft;
  if (draftRaw !== 0 && draftRaw !== 1 && draftRaw !== true && draftRaw !== false) throw new ValidationError('draft', 'draft must be true or false');
  let progress: number | null = null;
  if (b.progress !== undefined && b.progress !== null && b.progress !== '') {
    const n = typeof b.progress === 'string' && /^\d{1,3}$/.test(b.progress) ? Number(b.progress) : b.progress;
    if (typeof n !== 'number' || !Number.isInteger(n) || n < 0 || n > 100) throw new ValidationError('progress', 'progress must be a whole number from 0 to 100');
    progress = n;
  }
  return {
    progress,
    link: parseLink(b.link),
    title: str(b.title, 'title', 1, 80),
    description,
    status: oneOf(b.status, 'status', STATUSES),
    category: oneOf(b.category, 'category', CATEGORIES),
    version,
    release_date: release,
    draft: draftRaw === 1 || draftRaw === true ? 1 : 0,
  };
}

/**
 * Links may only point inside the wiki (total_war/ or tools/ pages), so the roadmap can never be used to publish an
 * external or javascript: URL. Accepts "/total_war/x.html#a" or "total_war/x.html"; stores the leading-slash form.
 */
export function parseLink(v: unknown): string {
  if (v === undefined || v === null || v === '') return '';
  if (typeof v !== 'string') throw new ValidationError('link', 'link must be text');
  let s = v.trim();
  if (s === '') return '';
  if (!s.startsWith('/')) s = '/' + s;
  if (s.length > 200 || !/^\/(total_war|tools)\/[A-Za-z0-9_./?=&#%~+-]+$/.test(s) || s.includes('..') || s.includes('//')) {
    throw new ValidationError('link', 'link must be a wiki page such as total_war/changes.html');
  }
  return s;
}

/** Parse a positive integer id from a route param or JSON value. */
export function parseId(v: unknown, field = 'id'): number {
  const n = typeof v === 'string' && /^\d{1,12}$/.test(v) ? Number(v) : v;
  if (typeof n !== 'number' || !Number.isSafeInteger(n) || n < 1) throw new ValidationError(field, `${field} must be a positive integer`);
  return n;
}

export interface ReorderEntry { id: number; status: Status }

/** Body: { order: [{id, status}, ...] } in the desired final order (all items). */
export function parseReorder(body: unknown): ReorderEntry[] {
  if (typeof body !== 'object' || body === null) throw new ValidationError('body', 'body must be a JSON object');
  const order = (body as Record<string, unknown>).order;
  if (!Array.isArray(order) || order.length === 0 || order.length > MAX_REORDER_ITEMS) {
    throw new ValidationError('order', `order must be a list of 1 to ${MAX_REORDER_ITEMS} entries`);
  }
  const seen = new Set<number>();
  return order.map((e, i) => {
    if (typeof e !== 'object' || e === null) throw new ValidationError(`order[${i}]`, 'entry must be an object');
    const id = parseId((e as Record<string, unknown>).id, `order[${i}].id`);
    if (seen.has(id)) throw new ValidationError(`order[${i}].id`, 'duplicate id');
    seen.add(id);
    return { id, status: oneOf((e as Record<string, unknown>).status, `order[${i}].status`, STATUSES) };
  });
}
