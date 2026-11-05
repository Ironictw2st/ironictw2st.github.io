import { adminCreate, adminList } from '../../../_lib/handlers.ts';
import { toCtx } from '../../../_lib/route.ts';
import type { Env } from '../../../_lib/types.ts';

type C = { request: Request; env: Env; data: Record<string, unknown> };
export const onRequestGet = (c: C) => adminList(toCtx(c));
export const onRequestPost = (c: C) => adminCreate(toCtx(c));
