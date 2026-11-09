---
name: chemo-reminder-dashboard
description: Build, update and operate a protocol-based chemotherapy tracking, reminder and live-dashboard system for a hematology clinical pharmacist (UKALL 2011 Regimens A, B, C). Use whenever the user uploads chemotherapy protocols or patient record sheets (PDF, Word, Excel, photos), registers or updates patients, asks for a chemo schedule, MAR, treatment calendar or roadmap, 7-day reminder emails, dose checks (BSA, mg/mL, discrepancies, modifications), postponements, drug shortages, or changes to the chemo dashboard. Trigger even if the user only says "chemo board", "chemo tracker", "MAR", "reminder system", or names a patient on the board.
---

# Chemotherapy reminder system and live dashboard

The system is a single self-contained HTML dashboard, published as a claude.ai artifact, that holds the patient register, schedules, reminders, pharmacy stock and references. The pharmacist edits it in the page and presses **Save changes**; the page republishes itself. Viewers without edit rights see a read-only copy.

Bundled here:
- `assets/` – dashboard code (`app.js`, `style.css`, `head.html`), reference page images with drug highlights (`refs.json`), protocol digest (`protocols.json`), an empty register.
- `scripts/build_dashboard.py` – build the HTML from a register, or rebuild a saved board with the current code.
- `scripts/extract_register.py` – pull the register out of a saved board (with `--summary` to see recent edits).
- `scripts/schedule_engine.py` – daily reminder check (what goes in today's email, what was missed).
- `scripts/qa_smoke.py` – headless check: every tab opens, no errors, no phone overflow.
- `references/data-model.md`, `references/dashboard-spec.md`, `references/email-template.md`.

## Standing decisions (from the pharmacist; keep unless told otherwise)

1. **Always continue from the latest saved board.** Before any change: read the artifact, run `extract_register.py --summary`, and build on that register. Never overwrite the pharmacist's edits; changes are cumulative. Re-read just before publishing and stop if it changed.
2. **Patients are Confirmed by default.** No approval checklist unless the user sets a patient to *Awaiting approval* (Edit → Status). Then the checklist and Approvals tab appear; approving needs the approver's name. Dosing changes do not silently reset a confirmed patient; they add a review note.
3. **Past doses are Given by default**, labelled "Given (default)", unless held, cancelled, recorded as *Not given*, or a dose discrepancy is open. A Settings toggle turns this off.
4. **Seven days everywhere**: reminders 7 days ahead, roadmap, calendar week, MAR default range and patient views all span today + 7.
5. **BSA = (4W + 7) / (90 + W)** (Furqan and Haque, weight in kg, as specified by the pharmacist). A manual BSA correction with a reason takes precedence until the next weight. Recalculate only when the weight is at least as recent as the BSA in use; otherwise keep the BSA and flag it. Keep every old value in the measurement history and flag disagreements with the record. (The same expression is also cited as the Costeff formula; mention once if attribution matters.)
6. **Shortages**: a drug marked Unavailable under any protocol checklist is flagged on every upcoming dose of that drug. *Not verified* is never treated as unavailable.
7. **Email** contains only patient name, MRN, drug, dose (mg, plus mL when a concentration is saved) and week, for confirmed patients.
8. **mL** only from a concentration entered in the Concentrations tab (mL = mg ÷ mg/mL). Never assume a vial strength.
9. **Readability**: keep text large (17.5 px base) and the week timeline as day cards plus a vertical dose timeline.

## Clinical safety rules (always)

- Hospital protocol files are the source for schedules and doses. Never invent doses, days, or calculation rules; never substitute a protocol.
- Different drugs in one phase keep their own days. A postponement moves only that dose unless the user asks to move later doses.
- Never auto-change a prescribed dose. Discrepancies need a named clinician's authorization; modifications record original, new, direction, date, reason, person and documentation.
- When reading record sheets: preserve names exactly (Arabic as written), never fill blanks, and flag anything illegible, assumed (e.g. a year inferred from weekdays) or conflicting as a data conflict or review note.
- Prefer the most recent dated value; keep history; if two sources conflict, flag rather than pick silently.
- Patient names and MRNs are on the board: remind once that the link should stay private unless hospital policy allows sharing. Never store patient details in memory.
- Never claim an email was sent unless Gmail confirmed it.

## Workflows

**Change the dashboard (features or data)**
1. `Artifact` read → `python scripts/extract_register.py <index.html> /tmp/reg.json --summary`.
2. Code changes: edit `assets/app.js` / `assets/style.css` (keep `__HEAD__`; no literal `</script` in JS). Data changes: edit the register (or seed phases, see data-model.md).
3. `python scripts/build_dashboard.py --register /tmp/reg.json --out <file>` (or `--from-html` for code-only updates).
4. Test: `python scripts/qa_smoke.py <file>`, plus targeted Playwright checks of what changed (mock `window.claude.use` for artifact, user, downloads, sample).
5. Re-read the artifact; if unchanged, publish to the same URL. First publish declares capabilities `{artifact:{}, downloads:true, sample:{}, user:{}}`; later publishes may omit them to keep the stored set.
6. Report what changed, anything flagged for the pharmacist, and the test result.

**New protocol upload**: extract drugs, doses, units, route, days per drug, cycle length, supportive care and labs into the protocol digest; list unclear items as protocol questions; add schedule templates only for what the document states. Render the relevant pages for References.

**New patient from a record sheet**: transcribe the sheet into `record.entries`; set demographics as written; find the current phase and day 1 from the last documented treatment; seed the phase; mark documented doses; add review notes for every assumption. Status Confirmed unless told otherwise.

**Daily reminder**: `python scripts/schedule_engine.py /tmp/reg.json --today YYYY-MM-DD` → build the email per `references/email-template.md`; draft or send via Gmail only if connected and confirmed.

## Feature map
See `references/dashboard-spec.md` for every tab (Overview roadmap, MAR, Calendar, Patients and journey, Pharmacy, Protocols, References, Email, Log, Settings, Assistant) and `references/data-model.md` for the register.
