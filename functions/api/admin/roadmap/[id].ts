import { adminDelete, adminUpdate } from '../../../_lib/handlers.ts';
import { toCtx } from '../../../_lib/route.ts';
import type { Env } from '../../../_lib/types.ts';

type C = { request: Request; env: Env; data: Record<string, unknown>; params: { id: string } };
export const onRequestPut = (c: C) => adminUpdate(toCtx(c), String(c.params.id));
export const onRequestDelete = (c: C) => adminDelete(toCtx(c), String(c.params.id));
