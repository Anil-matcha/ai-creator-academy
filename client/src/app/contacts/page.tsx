"use client";

import { useCallback, useEffect, useState } from "react";
import { Contact, Agent } from "@/lib/types";
import { api } from "@/lib/api";
import { ContactRound, Pencil, Plus, Trash2, X } from "lucide-react";

const inputClass = "w-full rounded-md border border-[#30363d] bg-[#0d1117] px-3 py-2 text-xs text-[#e6edf3] outline-none focus:border-[#58a6ff]";
type ContactFields = Pick<Contact, "email" | "name" | "company" | "notes">;
const emptyFields: ContactFields = { email: "", name: "", company: "", notes: "" };

export default function ContactsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [agentEmail, setAgentEmail] = useState("");
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [fields, setFields] = useState<ContactFields>(emptyFields);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getAgents().then((items) => {
      setAgents(items);
      setAgentEmail(items[0]?.email ?? "");
    }).catch((err: unknown) => setError(err instanceof Error ? err.message : "Failed to load inboxes"));
  }, []);

  const loadContacts = useCallback(async () => {
    if (!agentEmail) { setContacts([]); setLoading(false); return; }
    try {
      setLoading(true);
      setContacts(await api.getContacts(agentEmail));
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load contacts");
    } finally { setLoading(false); }
  }, [agentEmail]);

  useEffect(() => { void loadContacts(); }, [loadContacts]);

  const resetForm = () => { setFields(emptyFields); setEditingId(null); };
  const editContact = (contact: Contact) => {
    setEditingId(contact.id);
    setFields({ email: contact.email, name: contact.name, company: contact.company, notes: contact.notes });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const saveContact = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!agentEmail) return;
    try {
      setSaving(true); setError(null);
      if (editingId) await api.updateContact(agentEmail, editingId, fields);
      else await api.createContact(agentEmail, fields);
      resetForm();
      await loadContacts();
    } catch (err: unknown) { setError(err instanceof Error ? err.message : "Could not save contact"); }
    finally { setSaving(false); }
  };

  const removeContact = async (contact: Contact) => {
    if (!agentEmail || !window.confirm(`Delete ${contact.name} (${contact.email})?`)) return;
    try { await api.deleteContact(agentEmail, contact.id); await loadContacts(); }
    catch (err: unknown) { setError(err instanceof Error ? err.message : "Could not delete contact"); }
  };

  const visibleContacts = contacts.filter((contact) =>
    `${contact.name} ${contact.email} ${contact.company}`.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-8">
      <header className="flex flex-col justify-between gap-4 border-b border-[#30363d] pb-6 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[#e6edf3]">Contacts</h1>
          <p className="mt-1 text-xs text-[#8b949e]">Keep a simple address book for each agent inbox.</p>
        </div>
        <label className="text-xs text-[#8b949e]">Inbox
          <select className={`${inputClass} mt-1 sm:w-80`} value={agentEmail} onChange={(event) => { setAgentEmail(event.target.value); resetForm(); }}>
            {agents.length === 0 && <option value="">No inboxes configured</option>}
            {agents.map((agent) => <option key={agent.id} value={agent.email}>{agent.display_name} · {agent.email}</option>)}
          </select>
        </label>
      </header>

      {error && <div role="alert" className="rounded-md border border-[#f85149]/40 bg-[#f85149]/10 px-4 py-3 text-xs text-[#ff7b72]">{error}</div>}

      {agentEmail && <form onSubmit={saveContact} className="space-y-4 rounded-lg border border-[#30363d] bg-[#161b22] p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-[#e6edf3]">{editingId ? "Edit contact" : "Add a contact"}</h2>
          {editingId && <button type="button" onClick={resetForm} className="flex items-center gap-1 text-xs text-[#8b949e] hover:text-white"><X className="h-3.5 w-3.5"/>Cancel edit</button>}
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="space-y-1 text-xs text-[#8b949e]">Name<input required maxLength={255} className={inputClass} value={fields.name} onChange={(e) => setFields({ ...fields, name: e.target.value })} /></label>
          <label className="space-y-1 text-xs text-[#8b949e]">Email<input required type="email" maxLength={255} className={inputClass} value={fields.email} onChange={(e) => setFields({ ...fields, email: e.target.value })} /></label>
          <label className="space-y-1 text-xs text-[#8b949e]">Company<input maxLength={255} className={inputClass} value={fields.company} onChange={(e) => setFields({ ...fields, company: e.target.value })} /></label>
          <label className="space-y-1 text-xs text-[#8b949e]">Notes<textarea maxLength={4000} rows={2} className={inputClass} value={fields.notes} onChange={(e) => setFields({ ...fields, notes: e.target.value })} /></label>
        </div>
        <button disabled={saving} className="inline-flex items-center gap-2 rounded-md bg-[#238636] px-3 py-2 text-xs font-medium text-white hover:bg-[#2ea043] disabled:opacity-50"><Plus className="h-3.5 w-3.5"/>{saving ? "Saving…" : editingId ? "Save contact" : "Add contact"}</button>
      </form>}

      <section className="overflow-hidden rounded-lg border border-[#30363d] bg-[#161b22]">
        <div className="flex flex-col justify-between gap-3 border-b border-[#30363d] p-4 sm:flex-row sm:items-center">
          <h2 className="text-sm font-semibold text-[#e6edf3]">Address book <span className="ml-1 text-xs font-normal text-[#8b949e]">{contacts.length}</span></h2>
          <input aria-label="Search contacts" placeholder="Search name, email, company" className={`${inputClass} sm:w-72`} value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        {loading ? <p className="p-8 text-center text-xs text-[#8b949e]">Loading contacts…</p>
          : visibleContacts.length === 0 ? <div className="p-10 text-center"><ContactRound className="mx-auto mb-2 h-6 w-6 text-[#8b949e]"/><p className="text-xs text-[#8b949e]">{contacts.length ? "No contacts match your search." : "No contacts saved for this inbox yet."}</p></div>
          : <div className="divide-y divide-[#30363d]">{visibleContacts.map((contact) => <article key={contact.id} className="flex items-start justify-between gap-4 px-4 py-3">
            <div className="min-w-0"><p className="truncate text-sm font-medium text-[#e6edf3]">{contact.name}</p><a className="mt-0.5 block truncate text-xs text-[#58a6ff] hover:underline" href={`mailto:${contact.email}`}>{contact.email}</a>{contact.company && <p className="mt-1 text-xs text-[#8b949e]">{contact.company}</p>}{contact.notes && <p className="mt-1 whitespace-pre-wrap text-xs text-[#8b949e]">{contact.notes}</p>}</div>
            <div className="flex shrink-0 gap-1"><button aria-label={`Edit ${contact.name}`} onClick={() => editContact(contact)} className="rounded p-2 text-[#8b949e] hover:bg-[#21262d] hover:text-white"><Pencil className="h-3.5 w-3.5"/></button><button aria-label={`Delete ${contact.name}`} onClick={() => void removeContact(contact)} className="rounded p-2 text-[#8b949e] hover:bg-[#3d1f1f] hover:text-[#ff7b72]"><Trash2 className="h-3.5 w-3.5"/></button></div>
          </article>)}</div>}
      </section>
      <p className="text-[11px] text-[#8b949e]">Contacts are stored per inbox. Saving a contact does not send email or start outreach.</p>
    </div>
  );
}
