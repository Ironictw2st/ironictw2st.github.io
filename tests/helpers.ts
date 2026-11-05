// Test helpers: a D1-compatible wrapper over node:sqlite (real SQL, real migration), and a JWT signer.
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import type { D1Like, D1Statement, D1Result } from '../functions/_lib/types.ts';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

class Stmt implements D1Statement {
  db: DatabaseSync; sql: string; params: unknown[];
  constructor(db: DatabaseSync, sql: string, params: unknown[] = []) { this.db = db; this.sql = sql; this.params = params; }
  bind(...values: unknown[]): D1Statement { return new Stmt(this.db, this.sql, values); }
  async all<T = unknown>(): Promise<D1Result<T>> { return { results: this.db.prepare(this.sql).all(...(this.params as any[])) as T[] }; }
  async first<T = unknown>(): Promise<T | null> { return (this.db.prepare(this.sql).get(...(this.params as any[])) as T | undefined) ?? null; }
  async run(): Promise<D1Result> {
    const r = this.db.prepare(this.sql).run(...(this.params as any[]));
    return { success: true, meta: { last_row_id: Number(r.lastInsertRowid), changes: Number(r.changes) } };
  }
}

export function makeDb(): D1Like & { raw: DatabaseSync } {
  const raw = new DatabaseSync(':memory:');
  raw.exec(readFileSync(join(root, 'migrations', '0001_roadmap.sql'), 'utf8'));
  return {
    raw,
    prepare: (sql: string) => new Stmt(raw, sql),
    async batch(stmts: D1Statement[]) {
      // D1 batches are atomic: all or nothing
      raw.exec('BEGIN');
      try {
        const out: D1Result[] = [];
        for (const s of stmts) out.push(await (s as Stmt).run());
        raw.exec('COMMIT');
        return out;
      } catch (e) { raw.exec('ROLLBACK'); throw e; }
    },
  };
}

const b64u = (buf: ArrayBuffer | Uint8Array) =>
  Buffer.from(buf instanceof Uint8Array ? buf : new Uint8Array(buf)).toString('base64url');

export async function makeKey() {
  const kp = await crypto.subtle.generateKey(
    { name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
  const jwk = (await crypto.subtle.exportKey('jwk', kp.publicKey)) as { n: string; e: string; kty: string };
  return { priv: kp.privateKey, jwk };
}

export async function signJwt(priv: CryptoKey, payload: Record<string, unknown>, header: Record<string, unknown> = { alg: 'RS256', kid: 'k1' }) {
  const h = b64u(new TextEncoder().encode(JSON.stringify(header)));
  const p = b64u(new TextEncoder().encode(JSON.stringify(payload)));
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', priv, new TextEncoder().encode(`${h}.${p}`));
  return `${h}.${p}.${b64u(sig)}`;
}

export const TEAM = 'wiki.cloudflareaccess.com';
export const AUD = 'aud-tag-123';
