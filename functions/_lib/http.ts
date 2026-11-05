import { MAX_BODY_BYTES, ValidationError } from './validate.ts';
import { AccessDenied } from './access.ts';

export const SECURITY_HEADERS: Record<string, string> = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'same-origin',
  'Cache-Control': 'no-store',
};

export function json(data: unknown, status = 200, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...SECURITY_HEADERS, ...extra },
  });
}

export function errorResponse(e: unknown): Response {
  if (e instanceof AccessDenied) return json({ error: e.message }, e.status);
  if (e instanceof ValidationError) return json({ error: e.message, field: e.field }, 400);
  return json({ error: 'Server error' }, 500); // never leak internals
}

/** Same-site check used by every state-changing request (also called directly by body-less DELETE). */
export function assertSameSite(request: Request): void {
  const origin = request.headers.get('Origin');
  if (origin !== null && origin !== new URL(request.url).origin) throw new AccessDenied('Cross-origin request refused', 403);
  const site = request.headers.get('Sec-Fetch-Site');
  if (site !== null && site !== 'same-origin' && site !== 'none') throw new AccessDenied('Cross-site request refused', 403);
}

/**
 * CSRF / request-shape guard for every state-changing request:
 *  - JSON content type only (a cross-site form cannot send it without a CORS preflight, which we never grant)
 *  - Origin / Sec-Fetch-Site, when the browser sends them, must be this site
 *  - body size capped
 * Combined with the Access cookie (SameSite) and the JWT check this leaves no ambient-credential path.
 */
export async function readJsonBody(request: Request): Promise<unknown> {
  assertSameSite(request);
  const ct = (request.headers.get('Content-Type') ?? '').toLowerCase();
  if (!ct.startsWith('application/json')) throw new ValidationError('content-type', 'Content-Type must be application/json');
  const len = Number(request.headers.get('Content-Length') ?? '0');
  if (len > MAX_BODY_BYTES) throw new ValidationError('body', 'Request body too large');
  const text = await request.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) throw new ValidationError('body', 'Request body too large');
  try { return JSON.parse(text); } catch { throw new ValidationError('body', 'Body is not valid JSON'); }
}
