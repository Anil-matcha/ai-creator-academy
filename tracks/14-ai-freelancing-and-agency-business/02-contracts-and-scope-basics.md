# Module 2: Contracts & Scope Basics

> Structuring bulletproof Master Services Agreements (MSA), Statements of Work (SOW), revision caps, milestone payment schedules, and AI copyright/IP assignment clauses.

---

## 🎯 Why Standard Contracts Fail for AI Agencies

Traditional creative contracts assume human labor, manual camera shoots, and clear linear timelines. When managing AI creation pipelines, traditional contract templates leave massive legal loopholes:

1. **The Revision Trap:** Clients assuming that because *"AI generates images in seconds,"* they can demand 50 infinite variations for free.
2. **The Prompt IP Confusion:** Clients demanding full ownership of your internal prompt libraries, ComfyUI workflows, and LoRA weights.
3. **The AI Copyright Ambiguity:** Misunderstandings around U.S. Copyright Office rulings on AI-generated assets and commercial usage guarantees.

To protect your agency margin and sanity, every client relationship must be governed by two legally binding agreements:
* **Master Services Agreement (MSA):** Sets global legal terms (liability, payment terms, confidentiality, governing law).
* **Statement of Work (SOW):** Defines specific deliverables, timelines, milestone fees, and strict revision boundaries for a specific project.

---

## 🔒 The 5 Mandatory Contract Clauses for AI Creators

### 1. Revision Caps & Scope Creep Shield
Scope creep is the single biggest threat to agency profit. Define *exactly* what constitutes a valid revision vs. an out-of-scope change order:

> **Clause 4.2 — Scope of Revisions:**  
> *"The agreed Contract Value includes exactly two (2) rounds of revisions per deliverable. A 'Revision' is strictly limited to minor adjustments in color grading, background lighting adjustments, contrast correction, or minor masking fixes. Any request by Client for structural prompt re-engineering, model replacement, pose changes, or fundamental style alterations following sign-off of the initial Brief shall be classified as an Out-of-Scope Change Order, billed at Agency's standard rate of $150.00 per hour."*

---

### 2. Milestone Payment Structure & Payment Lock
Never initiate GPU renders or prompt execution without non-refundable upfront cash. A standard milestone structure ensures positive cash flow:

```
+-----------------------------------------------------------------------------+
|                        MILESTONE PAYMENT SCHEDULE                           |
+-----------------------------------------------------------------------------+
| MILESTONE 1: 50% Non-Refundable Deposit Upon Contract Signing               |
| • Unlocks compute resources, model selection, and initial draft generation. |
|                                                                             |
| MILESTONE 2: 25% Upon First Watermarked Draft Review                        |
| • Delivered as low-res watermarked proofs for Client feedback sign-off.     |
|                                                                             |
| MILESTONE 3: 25% Upon Final Asset Handover                                  |
| • Unlocks un-watermarked 8k master files & commercial usage license.        |
+-----------------------------------------------------------------------------+
```

> [!WARNING]
> **Never Deliver Final Un-Watermarked Master Files Prior to 100% Payment Clearance.** Delivering un-watermarked assets early removes all payment leverage and leads to delayed accounts receivable.

---

### 3. AI Copyright & Intellectual Property Assignment
Address copyright law regarding AI-generated media clearly to set realistic expectations and protect client commercial rights:

> **Clause 8.1 — Intellectual Property & AI Commercial License:**  
> *"Upon receipt of full payment, Agency grants to Client an exclusive, perpetual, worldwide commercial usage license to use, display, distribute, and monetize the final delivered media assets. Client acknowledges that deliverables utilize state-of-the-art Generative AI models (e.g., FLUX, Runway, ElevenLabs) operating under commercial enterprise tier agreements. Agency warrants that its prompt workflows and post-processing methods do not incorporate confidential third-party trade secrets or trademarked visual assets without authorization."*

---

### 4. Background Proprietary IP Reservation
Protect your internal workflow assets so clients cannot steal your technical stack:

> **Clause 8.4 — Agency Background Technology:**  
> *"Agency retains all right, title, and interest in and to its pre-existing tools, proprietary prompt libraries, ComfyUI node graphs, LoRA model weights, workflow scripts, and background automation technology ('Agency Background IP'). Nothing in this Agreement shall be construed as transferring ownership of Agency Background IP to Client."*

---

### 5. Client Input Warranty & Indemnification
Ensure the client is legally responsible if they provide trademarked or copyrighted reference photos:

> **Clause 9.3 — Client Data & Input Warranty:**  
> *"Client represents and warrants that all logos, brand guidelines, reference images, trademarks, and employee headshots provided to Agency for AI model input do not infringe upon any third-party intellectual property or privacy rights. Client agrees to defend, indemnify, and hold harmless Agency against any claims arising from Client-provided inputs."*

---

## 🛑 Common Scope Creep Scenarios & Exact Client Responses

| Scope Creep Scenario | Client Request | Contract Defense & Exact Response |
|---|---|---|
| **Endless Variations** | *"Can we try 30 more variations of this lighting setup?"* | *"We’d love to explore those new variations! As per Clause 4.2 of our SOW, our 2 included revision rounds are complete. I can send over an Out-of-Scope Change Order for $450 to cover 15 additional variations."* |
| **Workflow Source Files** | *"Send over all raw JSON prompts and node graphs so our team can run them internally."* | *"Our final 8k deliverables are fully licensed to you upon final payment! However, as outlined in Clause 8.4, our internal ComfyUI node graphs and prompt libraries are proprietary Agency Background IP and are not included in this deliverable."* |
| **Late Payment Delay** | *"Our accounting department pays Net-60. Send the HD files now and we’ll pay next month."* | *"We completely understand corporate AP cycles! Per our agreement, high-resolution un-watermarked master files are released immediately upon final invoice clearance. Let us know as soon as the wire goes through!"* |

---

## 🛠️ Step-by-Step Action Plan

1. **Adopt the Master Agreement:** Download [`templates/freelance-client-contract.md`](templates/freelance-client-contract.md) to customize your agency agreement.
2. **Set Rigid Revision Limits:** Always state revision limits in writing in your initial project proposal.
3. **Use Watermarked Proofing:** Deliver low-resolution watermarked previews prior to final milestone release.
4. **Review Client Performance Dashboard:** View the client metrics dashboard report graphic:
   ![Client Metrics Dashboard](templates/examples/client-dashboard-metrics.jpg)
   *Watch the analytics motion video loop ([client-dashboard-motion.mp4](templates/examples/client-dashboard-motion.mp4) / [.gif](templates/examples/client-dashboard-motion.gif)).*

---

## 💡 Key Takeaways
- Always enforce a 50% non-refundable deposit before starting any GPU render or prompt pipeline.
- Separate final output licensing (transferred to client) from internal prompt graphs and workflow IP (retained by agency).
- Explicitly define revision parameters to prevent scope creep from destroying your net margin.
