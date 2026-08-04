# SecTrace HiClaw resources

This directory will contain repository-safe Worker and Team resources after H-01 proves the installed AgentTeams schema.

## Safety boundary

- Never commit credentials, local configuration, provider details, or copied runtime secrets.
- Reference environment variable names only; values remain operator-managed outside Git.
- Worker prompts and resource files use synthetic or de-identified data only.
- Workers expose analysis and advice, never shell execution, scanning, account changes, deletion, or remediation APIs.
- High-risk response plans remain pending human approval and cannot be marked executed.

Do not guess Worker YAML fields before H-01 compatibility evidence exists.
