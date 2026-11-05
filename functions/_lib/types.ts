// Minimal structural types so the code type-checks without pulling in the full Workers typings,
// and so tests can pass in a fake D1.
export interface D1Result<T = unknown> { results?: T[]; success?: boolean; meta?: Record<string, unknown> }
export interface D1Statement {
  bind(...values: unknown[]): D1Statement;
  all<T = unknown>(): Promise<D1Result<T>>;
  first<T = unknown>(): Promise<T | null>;
  run(): Promise<D1Result>;
}
export interface D1Like {
  prepare(sql: string): D1Statement;
  batch(stmts: D1Statement[]): Promise<D1Result[]>;
}
export interface Env {
  DB: D1Like;
  ASSETS: { fetch(req: Request | string): Promise<Response> };
  ACCESS_TEAM_DOMAIN?: string;
  ACCESS_AUD?: string;
  ACCESS_ALLOWED_EMAILS?: string;
  DEV_BYPASS_ACCESS?: string;
}
