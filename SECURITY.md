# Security policy

## Authorized use

BaoanSkills is for CTF environments, owned systems, and engagements with
explicit written authorization. The repository does not grant permission to test
any third-party system.

## Reporting a repository vulnerability

Do not disclose live credentials, private target data, or a new exploitable issue
in a public GitHub issue. Use
[GitHub Security Advisories](https://github.com/baoan778/BaoanSkills/security/advisories/new)
when private reporting is available. Otherwise contact the maintainers privately
through the security contact configured on the repository hosting account. If no
private channel is available, open a minimal public issue asking for a private
contact method.

Include:

- affected file and version;
- impact and prerequisites;
- safe reproduction steps;
- whether credentials or personal data are exposed;
- suggested remediation.

## Secrets

If a real secret is committed, revoke it first, then remove it from history.
Deleting the file in a later commit is not sufficient. Run the repository secret
scan before every release.

## Scope

This policy covers the repository itself. It does not authorize testing systems
mentioned by skills, examples, or linked third-party projects.
