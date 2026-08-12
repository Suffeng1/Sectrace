# R-09B9 Matrix send-control recovery

- Date: 2026-08-11
- Result: `STOPPED_COMPOSER_DRAFT_ABSENT`
- Matrix sends/retries: zero / zero
- Approval/Audit calls: zero / zero

The authorized scope was to preserve the existing composed JSON, identify the
actual visible Element send control, and activate it once without retyping.

The first read-only browser projection found that the active Element page had
changed to `Leader DM: sectrace-commander`; it contained no target composer text,
no matching event, and no send control. Sending there was prohibited.

The browser returned to the known Commander room route and reloaded once. The
correct title was restored, but the room composer was empty and the timeline still
contained zero `tr_s01_s09live` markers. The prior unsent draft did not survive the
room transition/reload.

Because the ticket explicitly prohibited re-entering the body, work stopped. No
text was entered, no send control was activated, no Matrix event was created, and
the pending trace was not approved. Temporary browser scripts were removed.

Current canonical state remains `tr_s01_s09live` / `rp_tr_s01_s09live` at
`pending_approval`. A new explicit authorization is required to re-enter the same
fixed JSON and perform one bounded send action in the now-correct Commander room.
