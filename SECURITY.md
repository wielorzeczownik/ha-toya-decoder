# Security Policy

## Supported versions

Only the latest release receives security fixes.

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately via [GitHub Security Advisories](https://github.com/wielorzeczownik/ha-toya-decoder/security/advisories/new).

Include as much detail as possible:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive a response within **7 days**. If the issue is confirmed, a fix will be released as soon as possible and you will be credited in the release notes (unless you prefer to remain anonymous).

## Scope

This integration communicates with local TOYA decoder devices on your network. The attack surface includes:

- Authentication and credential handling for the TOYA API
- HTTP communication with the decoder
- Data returned by the TOYA API

Issues related to the TOYA decoder firmware or the upstream TOYA GO API are out of scope.

## Security notes

- Credentials are stored by Home Assistant using its standard secrets mechanism.
