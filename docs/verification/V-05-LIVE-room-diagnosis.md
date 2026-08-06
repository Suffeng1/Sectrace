# V-05-LIVE room lifecycle diagnosis

Date: 2026-08-05

## Human evidence

The operator observed that Manager accepted an invitation to the Leader DM and
then immediately left, while Commander remained joined. This is recorded as
**Manager auto-leaves Leader DM**. No repeated invitation or S01 submission was
attempted. Screenshot identifiers are intentionally neither transcribed nor
reproduced.

## Bounded diagnosis

Installed public lifecycle guidance defines the Leader DM as Team Admin and
Leader only. Manager delegation uses a different three-party Leader Room:
Manager, Global Admin, and Leader. That Leader Room is the Team Leader Worker's
standard room.

The observed departure is therefore consistent with the documented room
topology: Manager is not expected to persist in the Leader DM. The exact
Manager remains Running on openclaw with non-empty Matrix user and room fields.
Its public status exposes no leave-reason or room-policy field, so no more
specific reason is available without inspecting prohibited Matrix identifiers
or credentials.

## V-05 impact and alternatives

Inviting Manager to Leader DM cannot repair Manager delegation. The required
Manager-owned evidence must use the existing Leader Room path. If that path
cannot be observed or used, V-05 remains incomplete.

The supported fallback is Team Admin assigning S01 directly to Commander in
Leader DM. This can exercise Leader-to-Team collaboration and the human
approval gate, but it does not prove Manager-owned task creation and routing,
so the deviation must remain explicit in final evidence.
