import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { authorise, verifyAccessJwt, _clearKeyCache, AccessDenied, devBypass } from '../functions/_lib/access.ts';
import { withAccess } from '../functions/_lib/guard.ts';
import { makeKey, signJwt, TEAM, AUD } from './helpers.ts';

const NOW = 1_800_000_000;
const env = { ACCESS_TEAM_DOMAIN: TEAM, ACCESS_AUD: AUD };
const good = (over: Record<string, unknown> = {}) => ({ iss: `https://${TEAM}`, aud: [AUD], email: 'me@example.com', sub: 'u1', iat: NOW - 10, nbf: NOW - 10, exp: NOW + 3600, ...over });

beforeEach(() => _clearKeyCache());

async function setup() {
  const real = await makeKey();
  const fetchKeys = async () => [{ kid: 'k1', kty: 'RSA', n: real.jwk.n, e: real.jwk.e }];
  return { real, fetchKeys };
}

const denied = (p: Promise<unknown>) => assert.rejects(p, (e: unknown) => e instanceof AccessDenied && (e as AccessDenied).status === 403);

test('valid token is accepted and identity returned', async () => {
  const { real, fetchKeys } = await setup();
  const who = await verifyAccessJwt(await signJwt(real.priv, good()), env, { fetchKeys, now: NOW });
  assert.equal(who.email, 'me@example.com');
});

test('missing token -> 403', async () => {
  const { fetchKeys } = await setup();
  await denied(verifyAccessJwt(null, env, { fetchKeys, now: NOW }));
});

test('forged token (signed with a different key) -> 403', async () => {
  const { fetchKeys } = await setup();
  const attacker = await makeKey();
  await denied(verifyAccessJwt(await signJwt(attacker.priv, good()), env, { fetchKeys, now: NOW }));
});

test('tampered payload keeps old signature -> 403', async () => {
  const { real, fetchKeys } = await setup();
  const t = await signJwt(real.priv, good({ email: 'someone@else.com' }));
  const [h, , s] = t.split('.');
  const forgedPayload = Buffer.from(JSON.stringify(good({ email: 'admin@evil.com' }))).toString('base64url');
  await denied(verifyAccessJwt(`${h}.${forgedPayload}.${s}`, env, { fetchKeys, now: NOW }));
});

test('alg "none" and HS256 are refused', async () => {
  const { fetchKeys } = await setup();
  const h = Buffer.from(JSON.stringify({ alg: 'none', kid: 'k1' })).toString('base64url');
  const p = Buffer.from(JSON.stringify(good())).toString('base64url');
  await denied(verifyAccessJwt(`${h}.${p}.AAAA`, env, { fetchKeys, now: NOW }));
  const h2 = Buffer.from(JSON.stringify({ alg: 'HS256', kid: 'k1' })).toString('base64url');
  await denied(verifyAccessJwt(`${h2}.${p}.AAAA`, env, { fetchKeys, now: NOW }));
});

test('wrong audience, wrong issuer, expired, not-yet-valid -> 403', async () => {
  const { real, fetchKeys } = await setup();
  for (const over of [{ aud: ['other'] }, { iss: 'https://evil.example.com' }, { exp: NOW - 1 }, { nbf: NOW + 1000 }]) {
    await denied(verifyAccessJwt(await signJwt(real.priv, good(over)), env, { fetchKeys, now: NOW }));
  }
});

test('garbage and malformed tokens -> 403', async () => {
  const { fetchKeys } = await setup();
  for (const t of ['', 'abc', 'a.b', 'a.b.c', '....', '<script>.x.y']) await denied(verifyAccessJwt(t, env, { fetchKeys, now: NOW }));
});

test('unconfigured deployment fails closed', async () => {
  const { real, fetchKeys } = await setup();
  const t = await signJwt(real.priv, good());
  await denied(verifyAccessJwt(t, {}, { fetchKeys, now: NOW }));
  await denied(verifyAccessJwt(t, { ACCESS_TEAM_DOMAIN: TEAM }, { fetchKeys, now: NOW }));
});

test('email allow-list is enforced when set', async () => {
  const { real, fetchKeys } = await setup();
  const t = await signJwt(real.priv, good());
  await verifyAccessJwt(t, { ...env, ACCESS_ALLOWED_EMAILS: 'ME@example.com, other@x.com' }, { fetchKeys, now: NOW });
  await denied(verifyAccessJwt(t, { ...env, ACCESS_ALLOWED_EMAILS: 'other@x.com' }, { fetchKeys, now: NOW }));
});

test('key fetch failure fails closed', async () => {
  const { real } = await setup();
  await denied(verifyAccessJwt(await signJwt(real.priv, good()), env, { fetchKeys: async () => { throw new Error('net'); }, now: NOW }));
});

test('dev bypass: only with the flag AND a localhost host', async () => {
  assert.equal(devBypass({ DEV_BYPASS_ACCESS: '1' }, 'http://localhost:8788/admin/roadmap')?.email, 'local-dev');
  assert.equal(devBypass({ DEV_BYPASS_ACCESS: '1' }, 'https://190-expanded.com/admin/roadmap'), null);
  assert.equal(devBypass({ DEV_BYPASS_ACCESS: '1' }, 'https://localhost.evil.com/admin'), null);
  assert.equal(devBypass({}, 'http://localhost:8788/admin'), null);
  assert.equal(devBypass({ DEV_BYPASS_ACCESS: 'true' }, 'http://localhost:8788/admin'), null);
});

test('authorise(): bypass flag on a production host still needs a real token', async () => {
  const { fetchKeys } = await setup();
  const req = new Request('https://190-expanded.com/api/admin/roadmap');
  await denied(authorise(req, { ...env, DEV_BYPASS_ACCESS: '1' }, { fetchKeys, now: NOW }));
});

test('middleware guard returns 403 JSON without calling the handler', async () => {
  const { fetchKeys } = await setup();
  let called = false;
  const res = await withAccess(new Request('https://190-expanded.com/api/admin/roadmap', { method: 'POST' }), { DB: null as any, ASSETS: null as any, ...env },
    async () => { called = true; return new Response('ok'); }, { fetchKeys, now: NOW });
  assert.equal(res.status, 403);
  assert.equal(called, false);
  assert.match(String((await res.json() as any).error), /Missing Access token/);
});

test('middleware guard passes a valid token through with identity', async () => {
  const { real, fetchKeys } = await setup();
  const t = await signJwt(real.priv, good());
  const req = new Request('https://190-expanded.com/api/admin/roadmap', { headers: { 'Cf-Access-Jwt-Assertion': t } });
  const res = await withAccess(req, { DB: null as any, ASSETS: null as any, ...env }, async (who) => new Response(who.email), { fetchKeys, now: NOW });
  assert.equal(await res.text(), 'me@example.com');
});
