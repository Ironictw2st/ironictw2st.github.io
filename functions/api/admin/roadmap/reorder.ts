import { adminReorder } from '../../../_lib/handlers.ts';
import { toCtx } from '../../../_lib/route.ts';
import type { Env } from '../../../_lib/types.ts';

export const onRequestPost = (c: { request: Request; env: Env; data: Record<string, unknown> }) => adminReorder(toCtx(c));
