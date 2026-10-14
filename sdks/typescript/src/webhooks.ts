import { createHmac, timingSafeEqual } from "node:crypto";
import { WebhookSignatureError } from "./errors.js";

export const DEFAULT_TOLERANCE_SECONDS = 300;

export type HeaderSource = Headers | Record<string, string | string[] | undefined>;

export interface WebhookEvent<T = Record<string, unknown>> {
  id: string;
  type: string;
  timestamp: number;
  payload: T;
}

function header(headers: HeaderSource, name: string): string | undefined {
  if (typeof (headers as Headers).get === "function") return (headers as Headers).get(name) ?? undefined;
  const wanted = name.toLowerCase();
  for (const [key, value] of Object.entries(headers as Record<string, string | string[] | undefined>)) {
    if (key.toLowerCase() === wanted) return Array.isArray(value) ? value[0] : value;
  }
  return undefined;
}

/** Signature for one secret: HMAC-SHA256 over `<timestamp>.<event id>.<raw body>`, hex, prefixed `sha256=`. */
export function signWebhook(secret: string, timestamp: string | number, eventId: string, body: string | Uint8Array): string {
  const mac = createHmac("sha256", secret);
  mac.update(`${timestamp}.${eventId}.`);
  mac.update(body);
  return `sha256=${mac.digest("hex")}`;
}

/**
 * Verify a delivery and return the parsed event. Pass the RAW request body and the request headers
 * (`X-Webhook-Event-Id`, `X-Webhook-Timestamp`, `X-Webhook-Signature`). Pass several secrets while a
 * rotation is in flight; the server signs with both for 24 hours and any match is accepted.
 */
export function constructEvent<T = Record<string, unknown>>(
  body: string | Uint8Array,
  headers: HeaderSource,
  secrets: string | string[],
  opts: { toleranceSeconds?: number; now?: number } = {},
): WebhookEvent<T> {
  const eventId = header(headers, "x-webhook-event-id");
  const timestamp = header(headers, "x-webhook-timestamp");
  const signatureHeader = header(headers, "x-webhook-signature");
  if (!eventId || !timestamp || !signatureHeader) throw new WebhookSignatureError("Missing webhook signature headers");
  if (!/^\d{1,12}$/.test(timestamp)) throw new WebhookSignatureError("Invalid webhook timestamp");
  const tolerance = opts.toleranceSeconds ?? DEFAULT_TOLERANCE_SECONDS;
  const now = opts.now ?? Math.floor(Date.now() / 1000);
  if (Math.abs(now - Number(timestamp)) > tolerance) throw new WebhookSignatureError("Webhook timestamp is outside the allowed window");

  const secretList = (Array.isArray(secrets) ? secrets : [secrets]).filter(Boolean);
  if (secretList.length === 0) throw new WebhookSignatureError("No signing secret provided");
  const provided = signatureHeader.split(",").map((s) => s.trim()).filter(Boolean);
  const matched = secretList.some((secret) => {
    const expected = Buffer.from(signWebhook(secret, timestamp, eventId, body));
    // Check every provided value so timing does not reveal which one matched.
    return provided.reduce((hit, candidate) => {
      const given = Buffer.from(candidate);
      return (given.length === expected.length && timingSafeEqual(given, expected)) || hit;
    }, false);
  });
  if (!matched) throw new WebhookSignatureError("Webhook signature does not match");

  let payload: T;
  try {
    payload = JSON.parse(typeof body === "string" ? body : Buffer.from(body).toString("utf8")) as T;
  } catch {
    throw new WebhookSignatureError("Webhook body is not valid JSON");
  }
  return { id: eventId, type: header(headers, "x-webhook-event") ?? "", timestamp: Number(timestamp), payload };
}
