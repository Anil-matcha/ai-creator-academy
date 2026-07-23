# B2B Corporate Headshot Proposal & Intake Template

Use this proposal document, client intake form schema, and privacy agreement to pitch and onboard corporate team clients.

---

## 💼 B2B Corporate Pricing Matrix

| Package Tier | Pricing | Employee Volume | Turnaround | Features Included |
|---|---|---|---|---|
| **Startup Team Pass** | **$399** | Up to 10 Employees | 48 Hours | 3 Style Options / Person, Brand Color Match, 1 Revision |
| **Corporate Standard** | **$799** | Up to 25 Employees | 24 Hours | 5 Style Options / Person, Custom Brand Match, 2 Revisions |
| **Enterprise Unlimited** | **$1,499** | Up to 50 Employees | 12 Hours SLA | Priority SLA, Unlimited Revisions, GDPR Data Purge Cert |

*Additional Team Members: **$25 per person**.*

---

## 📋 Employee Intake Form Schema

Provide this 4-step intake form to client HR departments for employee self-service:

```yaml
Intake_Form_Fields:
  - Field_1:
      label: "Full Employee Name"
      type: "text"
      required: true
  - Field_2:
      label: "Corporate Title"
      type: "text"
      required: true
  - Field_3:
      label: "Wardrobe Style Preference"
      type: "select"
      options:
        - "Executive Suit & Blazer (Formal)"
        - "Business Casual Blazer & Shirt (Modern)"
        - "Tech Sweater / Turtleneck (Casual)"
      required: true
  - Field_4:
      label: "Upload 3 Selfies (Well-lit, Front & 3/4 View)"
      type: "file_upload"
      max_files: 5
      allowed_types: ["jpg", "png", "heic"]
      required: true
```

---

## 🔒 Enterprise Data Privacy & GDPR Agreement

1. **Selfie Data Handling:** Source selfies provided by client employees are used solely for identity vector extraction and generation of authorized corporate headshots.
2. **Automated Data Purge:** All raw employee selfie uploads and facial embeddings are permanently deleted from agency servers within **7 business days** of final deliverable approval.
3. **No Model Training:** Client photos will never be used to train public AI models or shared with third-party data brokers.
4. **Delivery Security:** Final high-resolution headshot bundles are delivered via encrypted, password-protected cloud download folders.
