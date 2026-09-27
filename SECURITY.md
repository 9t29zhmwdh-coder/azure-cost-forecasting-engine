# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅ Yes    |
| Older   | ❌ No     |

Security fixes are only applied to the latest release.

## Credential Handling

All Azure credentials are loaded exclusively from environment variables or a `.env` file. The `.env` file is listed in `.gitignore`. No credentials are included in any report output, log line, or exception message.

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, report it privately via [GitHub Security Advisory](https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine/security/advisories/new) or contact the maintainer via the GitHub profile.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

A response within **48 hours** is the target, and the issue will be worked on promptly.

## Dependency Security

Dependencies are pinned in `requirements.txt`. Run `pip install --upgrade` periodically and review the changelog of each dependency before upgrading. The CI pipeline runs on pinned versions.

## Read-Only Azure Access

All Azure API calls are read-only GET requests. The required role (`Cost Management Reader`) grants no write access to any Azure resource.
