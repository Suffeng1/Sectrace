# SecTrace HiClaw resources

This directory contains the repository-safe Worker prompts, Worker resources,
and Team resource validated after H-01 proved the installed AgentTeams schema.

## Safety boundary

- Never commit credentials, local configuration, provider details, or copied runtime secrets.
- Reference environment variable names only; values remain operator-managed outside Git.
- Worker prompts and resource files use synthetic or de-identified data only.
- Workers expose analysis and advice, never shell execution, scanning, account changes, deletion, or remediation APIs.
- High-risk response plans remain pending human approval and cannot be marked executed.

Do not guess or extend Worker YAML fields beyond the recorded H-01 compatibility
evidence. See `docs/runtime/hiclaw-compatibility.md`.
