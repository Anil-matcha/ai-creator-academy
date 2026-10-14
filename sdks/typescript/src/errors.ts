/** An API or transport error. The bearer token is never included. */
export class AgentEmailError extends Error {
  readonly status: number | undefined;
  readonly detail: unknown;
  constructor(message: string, opts: { status?: number; detail?: unknown } = {}) {
    super(message);
    this.name = "AgentEmailError";
    this.status = opts.status;
    this.detail = opts.detail;
  }
}

/** Raised when a webhook delivery fails signature or timestamp verification. */
export class WebhookSignatureError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WebhookSignatureError";
  }
}
