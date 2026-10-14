# Operations guide

## Database migrations

Schema changes are managed with Alembic (`server/migrations`).

- On startup the server applies pending migrations automatically.
- A database created before Alembic is stamped at baseline `0001` and then upgraded; a new database is stamped at head.
- Run manually: `cd server && python -m app.migrate`.
- Add a change: edit `app/models.py`, then `alembic revision --autogenerate -m "describe change"`, review the generated file, commit it. `tests/test_migrations.py` fails if models and migrations drift.
- Take a backup before upgrading production (below). Downgrades are not guaranteed to preserve data.

## Backup and restore

Back up **both** of these together; one without the other is not recoverable:

1. **The database.**
   - SQLite: stop writes (or use `sqlite3 open_agent_email.db ".backup backup.db"`), then copy the file.
   - PostgreSQL: `pg_dump --format=custom "$DATABASE_URL" > backup.dump`.
2. **`SMTP_CONFIG_ENCRYPTION_KEY`** (and `SMTP_CONFIG_ENCRYPTION_KEY_PREVIOUS` during a rotation). SMTP relay passwords and webhook signing secrets are encrypted with it; a restored database without the key fails startup by design.

Message bodies and attachments live in the database, so they are covered by the database backup.

Restore:

1. Stop the service.
2. Restore the database (`cp backup.db ...` or `pg_restore --clean --dbname "$DATABASE_URL" backup.dump`).
3. Set the same `SMTP_CONFIG_ENCRYPTION_KEY`.
4. Start the service; migrations run, then check `GET /ready`.
5. Verify: sign in, open an inbox, send a test webhook (`POST /v1/webhooks/{id}/test`).

Rehearse a restore into a scratch environment on a schedule; an untested backup is not evidence.

## Encryption key rotation

1. Generate a new Fernet key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
2. Set `SMTP_CONFIG_ENCRYPTION_KEY=<new>` and `SMTP_CONFIG_ENCRYPTION_KEY_PREVIOUS=<old>`; restart. Startup re-encrypts every stored secret with the new key.
3. Confirm `/ready` is healthy and a webhook test succeeds, then remove the previous-key setting and restart.
4. Back up the new key with the database.

## Review approval links and expiry

- Approval links need a public `https` `PUBLIC_BASE_URL` reachable by the reviewer and an enabled upstream SMTP relay (Settings → SMTP). The reviewer email is sent directly through the relay, not through the inbox's own outbound queue, so it is never itself held for review.
- Link tokens are stored hashed in `review_link_tokens`; the raw token exists only in the email. Expired rows are harmless and can be deleted at any time: `DELETE FROM review_link_tokens WHERE expires_at < now()`.
- `GET /ready` does not depend on the notification path; a failed or skipped notification is logged (`review_notifications`) and the review simply waits in the dashboard.
- The expiry sweeper runs every 60 seconds in each API process and is safe with several instances: each review is resolved through a compare-and-set, so it is decided once. Auto-resolutions appear in the review history as reviewer `system:expiry` and emit `email.review_approved` / `email.review_rejected` webhooks.
- Choose the expiry action deliberately. The default is reject; `approve` sends held mail without a human decision once the window passes.

## Scheduled sending

`send_at` (UTC, at most 90 days ahead) on send/reply defers submission. A scheduled message has status `scheduled`; trashing it before submission (`DELETE /v1/agents/{email}/messages/{id}`) cancels it. With the approval gate on, the message is held for review first and the deferral is honored on approval. Delivery time is best-effort within the worker poll interval, and a message whose time passes while the service is down is sent on recovery.
