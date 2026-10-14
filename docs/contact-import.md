# Structured contact import

`POST /v1/contacts/import` imports JSON contact rows into one explicitly selected inbox. The required `agent_email` body field identifies the target because this self-hosted server stores contacts per inbox, rather than in a separate account-wide contact identity table. Administrator credentials can select any inbox; an inbox API key can select only its own inbox and must have write scope.

The request accepts 1–1,000 rows and is limited to 1 MB. Each row requires `email` and may include `display_name`, `company`, `notes`, bounded flat scalar `metadata`, `suppressed`, and an engagement `stage` (`new`, `contacted`, `waiting`, or `closed`). `on_conflict` is `merge` by default or `skip`. Merge updates only fields present on the row and shallow-merges metadata. Duplicate addresses in a merge batch therefore update the row created earlier in that same batch; with skip mode they are skipped after the first create.

The response reports `created`, `updated`, `skipped`, and `failed` counts plus one outcome for every input row. Invalid rows fail independently, so valid rows in the batch are retained. A supplied `Idempotency-Key` replays the original result for an identical request.

Setting `suppressed: true` adds the address to that inbox's existing recipient suppression list, which blocks outbound mail. `false` does not remove a pre-existing suppression. Import does not send mail or record consent. A supplied `stage` creates or updates the existing separate engagement record; it does not create a new identity or stage table.

Imports create reversible batch records. Reversing a batch removes contacts created by it only when they have not since been edited; merged existing contacts and their field or stage updates are retained. Suppression entries created by an import are not removed by batch reversal.
