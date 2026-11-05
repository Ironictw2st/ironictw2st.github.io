// Cloudflare Access JWT verification (defence in depth).
// Access already blocks unauthenticated requests at the edge; this module makes the Function
// itself refuse any request that does not carry a valid Access token for THIS application,
// so a mis-configured Access policy or a request that bypasses the edge still gets a 403.
// No passwords, no sessions of our own.
//
// Token: header `Cf-Access-Jwt-Assertion` (RS256).  Keys: https://<team>.cloudflareaccess.com/cdn-cgi/access/certs

export interface AccessEnv {
  ACCESS_TEAM_DOMAIN?: string;      // e.g. "yourteam.cloudflareaccess.com"
  ACCESS_AUD?: string;              // Application Audience (AUD) tag of the Access app
  ACCESS_ALLOWED_EMAILS?: string;   // optional extra allow-list, comma separated
  DEV_BYPASS_ACCESS?: string;       // "1" ONLY in .dev.vars, honoured only for localhost
}

export interface Identity { email: string; sub: string; devBypass?: boolean }

export class AccessDenied extends Error {
  readonly status: number;
  constructor(message: string, status = 403) { super(message); this.status = status; }
}

interface Jwk { kid: string; kty: string; alg?: string; n: string; e: string }
export type KeyFetcher = (teamDomain: string) => Promise<Jwk[]>;

const defaultFetcher: KeyFetcher = async (teamDomain) => {
  const r = await fetch(`https://${teamDomain}/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error(`certs fetch failed: ${r.status}`);
  const j = (await r.json()) as { keys?: Jwk[] };
  return j.keys ?? [];
};

const keyCache = new Map<string, { at: number; keys: Jwk[] }>();
const KEY_TTL_MS = 60 * 60 * 1000;

export function _clearKeyCache(): void { keyCache.clear(); }

function b64urlToBytes(s: string): Uint8Array {
  const pad = '='.repeat((4 - (s.length % 4)) % 4);
  const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/') + pad);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function parseJson(bytes: Uint8Array): any {
  return JSON.parse(new TextDecoder().decode(bytes));
}

async function getKeys(team: string, fetcher: KeyFetcher, force = false): Promise<Jwk[]> {
  const c = keyCache.get(team);
  if (!force && c && Date.now() - c.at < KEY_TTL_MS) return c.keys;
  const keys = await fetcher(team);
  keyCache.set(team, { at: Date.now(), keys });
  return keys;
}

/** Verify a token. Throws AccessDenied (403) on anything wrong. `now` is seconds since epoch (injectable for tests). */
export async function verifyAccessJwt(
  token: string | null,
  env: AccessEnv,
  opts: { fetchKeys?: KeyFetcher; now?: number } = {},
): Promise<Identity> {
  const team = (env.ACCESS_TEAM_DOMAIN ?? '').trim();
  const aud = (env.ACCESS_AUD ?? '').trim();
  // Fail closed: an unconfigured deployment must not be writable.
  if (!team || !aud) throw new AccessDenied('Access is not configured', 403);
  if (!token) throw new AccessDenied('Missing Access token');

  const parts = token.split('.');
  if (parts.length !== 3 || parts.some((p) => !/^[A-Za-z0-9_-]+$/.test(p))) throw new AccessDenied('Malformed token');
  let header: any, payload: any;
  try {
    header = parseJson(b64urlToBytes(parts[0]));
    payload = parseJson(b64urlToBytes(parts[1]));
  } catch { throw new AccessDenied('Malformed token'); }

  // Only RS256 (never "none", never HS*): the algorithm is fixed by us, not by the token.
  if (header?.alg !== 'RS256' || typeof header?.kid !== 'string') throw new AccessDenied('Unsupported token');

  const fetcher = opts.fetchKeys ?? defaultFetcher;
  let keys: Jwk[];
  try { keys = await getKeys(team, fetcher); } catch { throw new AccessDenied('Cannot load Access keys', 403); }
  let jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) {
    // key rotation: refresh once
    try { keys = await getKeys(team, fetcher, true); } catch { throw new AccessDenied('Cannot load Access keys', 403); }
    jwk = keys.find((k) => k.kid === header.kid);
  }
  if (!jwk || jwk.kty !== 'RSA') throw new AccessDenied('Unknown signing key');

  const key = await crypto.subtle.importKey(
    'jwk', { kty: 'RSA', n: jwk.n, e: jwk.e, alg: 'RS256', ext: true },
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify'],
  );
  const ok = await crypto.subtle.verify(
    'RSASSA-PKCS1-v1_5', key, b64urlToBytes(parts[2]), new TextEncoder().encode(`${parts[0]}.${parts[1]}`),
  );
  if (!ok) throw new AccessDenied('Bad token signature');

  const now = opts.now ?? Math.floor(Date.now() / 1000);
  if (payload.iss !== `https://${team}`) throw new AccessDenied('Wrong issuer');
  const audClaim: unknown = payload.aud;
  const audOk = Array.isArray(audClaim) ? audClaim.includes(aud) : audClaim === aud;
  if (!audOk) throw new AccessDenied('Wrong audience');
  if (typeof payload.exp !== 'number' || payload.exp <= now) throw new AccessDenied('Token expired');
  if (typeof payload.nbf === 'number' && payload.nbf > now + 60) throw new AccessDenied('Token not yet valid');
  if (typeof payload.iat === 'number' && payload.iat > now + 300) throw new AccessDenied('Token issued in the future');

  const email = typeof payload.email === 'string' ? payload.email.toLowerCase() : '';
  const sub = typeof payload.sub === 'string' ? payload.sub : '';
  if (!email && !sub) throw new AccessDenied('Token has no identity');

  const allow = (env.ACCESS_ALLOWED_EMAILS ?? '').split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);
  if (allow.length && !allow.includes(email)) throw new AccessDenied('Not on the allow-list');

  return { email: email || sub, sub };
}

/** Local-dev escape hatch: only when DEV_BYPASS_ACCESS=1 AND the request really is to localhost. Never in production. */
export function devBypass(env: AccessEnv, requestUrl: string): Identity | null {
  if (env.DEV_BYPASS_ACCESS !== '1') return null;
  const host = new URL(requestUrl).hostname;
  if (host === 'localhost' || host === '127.0.0.1' || host === '[::1]') return { email: 'local-dev', sub: 'local-dev', devBypass: true };
  return null;
}

/** Authorise a request: Access JWT (or local dev bypass). Throws AccessDenied. */
export async function authorise(request: Request, env: AccessEnv, opts: { fetchKeys?: KeyFetcher; now?: number } = {}): Promise<Identity> {
  const bypass = devBypass(env, request.url);
  if (bypass) return bypass;
  return verifyAccessJwt(request.headers.get('Cf-Access-Jwt-Assertion'), env, opts);
}
