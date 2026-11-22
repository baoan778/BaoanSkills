# SSTI case family

Authorized CTF and owned-lab use only.

## What this family teaches

SSTI is a context problem. The same expression can be data, template source, or a value inside a template. The solve path begins with engine fingerprinting and ends only when the exact render context and an authorized sink are explained.

## Corpus anchors

- `WP汇总/ctfshow-SSTI.md`
- `WP汇总/ssti入门知识点.md`
- `SSTI.md`

Check paths in [the manifest](../archive/file-manifest.csv) before opening them.

## Context ladder

1. Is the user value inserted into a fixed template?
2. Can the user choose the template name or source?
3. Which delimiters and autoescape rules apply?
4. Which objects, globals, helpers, and filters are exposed?
5. Is a sandbox active, and what does it block?
6. Where does the rendered result go?

## Reasoning pattern

1. Send a harmless arithmetic probe in the syntax suggested by the engine.
2. Confirm whether the result is evaluated, escaped, or passed through.
3. Read the render code and reconstruct the actual template string.
4. Test a property or string marker with a local output.
5. Enumerate only the context needed for the challenge objective.
6. For a blind sink, use a local timing or file marker and stop at the first confirmation.

## Common traps

- Front-end templating can mimic server-side evaluation.
- A successful `{{7*7}}` may be a literal echo rather than SSTI.
- Autoescaping differs by context and engine version.
- A public sandbox-escape chain may target a different engine build.
- A template cache can preserve or leak state across requests.
- The output may be sent to a PDF, email, or log rather than the HTTP response.

## Next pivot

Use [SSTI](../web/ssti.md) for the detailed review, [Node prototype pollution](../web/node-prototype.md) for object-option gadgets, and `ctf-web` for the full challenge workflow.
