# Register data model

The dashboard keeps everything in one JSON object (the "register"), embedded in the page as
`<script id="data">`. Saving from the page republishes the whole HTML with the updated register.
`scripts/extract_register.py` pulls it out; `scripts/build_dashboard.py` puts it back with the current code.

## Top level
| Key | Meaning |
|---|---|
| `settings.lead` | Reminder lead in days (7). Emails list doses exactly this many days ahead |
| `settings.runway` | Days shown on roadmap, calendar week, MAR default range, patient "Next 7 days" (7) |
| `settings.autoConfirmPast` | true: past doses become "Given (default)" unless marked otherwise |
| `settings.bsaFormula` | `{expr, source, by, at, verified}`. Current: `(4*W+7)/(90+W)` (Furqan and Haque, as specified by the hospital pharmacist) |
| `protocols[]` | Protocol digest: `{id, regimen, phase, weeks, file, who, rows:[[drug,dose,route,schedule]], support, labs, flags:[{text,resolved,answer}], reviewed}` |
| `stock{protocolId:{drug:{state,note,by,at}}}` | Pharmacy checklist. state: `available`, `unavailable`, `unverified` (default) |
| `formulary{drug:{conc,unit,form,na,source,by,at}}` | Concentration for mL volumes. Empty by default; `na` = oral solid |
| `patients[]` | See below |
| `sent_log[]` | `{eventId, patient, drug, date, sentOn, method:'gmail'|'manual'}` |
| `mailEdits{sendDate:{text,by,at}}` | Hand-edited email text |
| `audit[]` | `{at, patient, text}` – never edited or deleted |
| `rev`, `savedAt`, `demoSeed` | Save counter, timestamp, the register to restore with "Reset" |

## Patient
`code` (internal id, e.g. PT-01), `name` (as written, Arabic kept), `mrn`, `age` (text), `ageYears` (number for IT methotrexate bands), `sex`, `weight`, `height`, `bsa` (used for dosing), `weightAsOf`/`heightAsOf`/`bsaAsOf`, `bsaSource`, `diagnosis`, `protocol` (as written), `admission`, `registered`, `status` (`active`, `delayed`, `held`, `completed`, `off`).

- `verification.first = {by, at}` present → **Confirmed**. Absent → **Awaiting approval** (checklist shown). Default for every patient is Confirmed.
- `checklist[]` `{text, done, kind:'std'|'flag', note}` – record-review notes; ticking only matters while awaiting approval.
- `phases[]` `{id, tpl, reg, label, weeks, start, cycles, superseded}`; `events[]` – one per dose or oral course.
- `measurements[]` `{date|label, weight, height, bsa, bsaMethod, source}` – history, never overwritten.
- `conflicts[]` `{kind, text, at, resolved, resolution, by}` – data needing manual verification.
- `modLog[]` dose modifications; `postponements[]`; `protocolChanges[]`; `record{source, entries[]}` (transcribed record sheet); `history[]`.

## Event (dose)
`id, phaseId, tpl, phase, drug, cls, route, day, week, date, end (courses), kind ('dose'|'course'), len, dose{basis:'bsa'|'age', per, unit, cap, text}, remind (false = home oral), state, actualDate, origDate, reason, auto (given by default), noAuto, postponed, mod{value,unit,reason,by,date}, entered{value,ml,source,by,at}, discAuth{...}, verified, note, derived`.

States: `scheduled`, `delayed` (postponed if `postponed`), `administered` (`auto` = by default), `notgiven`, `held`, `cancelled`, `superseded` (protocol change), `documented`/`unrecorded` (import states, auto-confirmed once past).

## Seeding new patients from records
Instead of `events`, give `seedPhases:[{tpl, start, cycles}]` and optional `seedOps`:
`{op:'document'|'given', drug, day, actual, note}`, `{op:'delay', drug, day, to, shift, reason}`.
Template ids: A-IND, A-CONS, A-IM1, A-DI, A-MNT, B-IND, B-CONS, B-IM, B-DI, B-MNT, C-CONS, C-CAP, C-DI, C-MNT.
Day 1 = first day of the phase; week = template start week + floor((day−1)/7). Count back from a known week to find day 1
(e.g. maintenance week 62 on 7 Nov 2026 → day 260 → day 1 = 21 Feb 2026).
