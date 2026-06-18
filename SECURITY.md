# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Credential Handling

All Azure credentials are loaded exclusively from environment variables or a `.env` file. The `.env` file is listed in `.gitignore`. No credentials are included in any report output, log line, or exception message.

## Reporting a Vulnerability

Open a GitHub issue with label `security`. Describe the vulnerability type and affected component. Do not include exploit code in public issues. Response target: 72 hours.

## Dependency Security

Dependencies are pinned in `requirements.txt`. Run `pip install --upgrade` periodically and review the changelog of each dependency before upgrading. The CI pipeline runs on pinned versions.

## Read-Only Azure Access

All Azure API calls are read-only GET requests. The required role (`Cost Management Reader`) grants no write access to any Azure resource.
