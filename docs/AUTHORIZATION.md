# Authorization and dual-use policy

These skills may describe offensive techniques. Their presence is not permission
to use them.

## Required preconditions

Before testing a system, confirm:

- the target is owned by the user, a CTF/lab environment, or covered by written
  authorization;
- the scope includes the exact host, path, account, and test type;
- destructive, persistence, denial-of-service, and data-access actions are
  explicitly allowed or excluded;
- credentials and extracted data are handled according to the engagement rules;
- disclosure and reporting requirements are understood.

## Agent behavior

When authorization is missing or ambiguous, do not run active testing. Ask for
scope confirmation or provide a defensive/planning alternative.

Stop immediately if:

- testing affects systems outside the approved scope;
- real user or customer data appears;
- availability degradation is observed;
- credentials are discovered outside the agreed handling process.

## Prohibited use

Do not use this repository to target third parties, conceal unauthorized access,
evade lawful controls, or distribute stolen data.
