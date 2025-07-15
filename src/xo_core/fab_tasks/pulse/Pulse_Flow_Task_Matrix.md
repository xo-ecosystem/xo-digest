# 🧭 Pulse Flow Task Matrix

| Module         | Task             | Description                                | Status             | Category   |
|----------------|------------------|--------------------------------------------|--------------------|------------|
| pulse_tasks    | sync             | Sync local pulses with XO node             | ✅ Active           | Core       |
| pulse_tasks    | archive_all      | Archive all pulses to Arweave              | ✅ Active           | Core       |
| pulse_tasks    | new              | Create a new pulse post                    | ✅ Active           | Content    |
| pulse_tasks    | sign             | Sign a pulse post using Vault              | ✅ Active           | Security   |
| pulse_tasks    | publish          | Publish a pulse to explorer or IPFS        | ✅ Active           | Core       |
| pulse_tasks    | delete           | Delete a pulse from local and remote stores| 🧪 Experimental    | Maintenance|
| summary_tasks  | generate_digest  | Generate digest from recent pulses         | 🛠️ In Progress      | Digest     |
| validate_tasks | validate_all     | Validate pulse formats and schema          | ✅ Active           | Validation |
| summary_tasks  | export_summary   | Export summarized pulse metadata           | 🧪 Experimental     | Digest     |
| docgen_tasks   | generate_docs    | Generate Markdown documentation for tasks  | ✅ Active           | Info       |

---

## ✅ Next TODOs for Pulse Flow Tasks (Prioritized)

1. [ ] Finalize `pulse_tasks.delete` — Confirm deletion workflow with Vault sync and backup check.
2. [ ] Implement `pulse_tasks.rename` — Safe renaming logic for existing pulses (with validation).
3. [ ] Add `pulse_tasks.clone` — Enable duplicating a pulse with a new UUID or name.
4. [ ] Improve `summary_tasks.generate_digest` — Add filters (by tag/date) and summary depth levels.
5. [ ] Add `validate_tasks.lint_all` — Lint MDX and frontmatter for formatting issues.
6. [ ] Write tests for `docgen_tasks.generate_docs` — Ensure documentation stays up-to-date.
7. [ ] Create `pulse_tasks.schedule` — Automate scheduled pulse publishing with timestamp control.
8. [ ] Add `summary_tasks.compare_digests` — Compare current and previous digest entries for change tracking.