# Security Policy

## Reporting a vulnerability

Please report vulnerabilities privately through the future repository's GitHub
security advisory feature. Until the repository is published, contact the
maintainer directly and do not open a public issue containing exploit details.

## Security invariants

- Transcript text must never be evaluated by a shell.
- Review remains enabled unless the user explicitly supplies `--yes`.
- Temporary recordings are deleted by default.
- New network behavior must be explicit and documented.
- Agent permissions remain controlled by the target agent, not TermVoice.
