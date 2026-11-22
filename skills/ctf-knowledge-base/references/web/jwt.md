# JWT and token claims

Authorized CTF and owned-lab use only.

## Signals

- A token has three dot-separated base64url segments: header, payload, and signature.
- Authorization depends on a token field rather than a server-side session.
- The challenge supplies a signing key, a public key, JWKS material, source code, or a token minting endpoint.
- The same token is accepted by more than one service, audience, role, or environment.

## First decode, then reason

Decode the header and payload without trusting them. Base64url decoding is reversible; it is not verification.

```bash
python -c "import base64,sys; s=sys.argv[1].split('.')[1]; print(base64.urlsafe_b64decode(s + '='*(-len(s)%4)))" "$TOKEN"
```

Record:

| Field | Question |
|---|---|
| `alg` | Which algorithm does the verifier actually accept and enforce? |
| `typ`, `cty` | Is the token intended for the same parser and content type? |
| `kid` | Is it a key selector, a filename, a database lookup, or attacker-controlled? |
| `jku`, `jwk`, `x5u` | Can token metadata redirect key discovery or inject a key? |
| `iss`, `aud`, `sub` | Which trust boundary and identity does the verifier require? |
| `iat`, `nbf`, `exp` | Are time checks enabled, and against which clock? |
| role or scope claims | Are claims consumed directly or mapped to server-side authority? |

Line breaks, whitespace, duplicate JSON keys, and alternate encodings may be normalized differently by the issuer, verifier, or downstream service. Treat parser disagreement as a hypothesis to test, not an automatic result.

## Source-led workflow

1. Locate every token consumer and identify the exact library and version.
2. Confirm how the verifier obtains the key and whether it binds `alg` to that key type.
3. List claims used for authorization and whether any claim is trusted across audiences.
4. Test one boundary at a time with a token minted for a local challenge account.
5. Verify the server-side effect with a harmless marker, such as access to a challenge-only profile page.
6. Capture the token, decoded fields, verifier response, and the source path that explains the behavior.

## Common weakness classes

| Class | Review question | Evidence |
|---|---|---|
| Algorithm confusion | Can an asymmetric public key be interpreted as an HMAC secret? | Verifier rejects or accepts a locally minted token under controlled conditions |
| Missing signature check | Is the signature verified before claims are used? | Source path and a modified token that reaches a marker endpoint |
| Weak or leaked secret | Is the key weak, embedded, or derivable from supplied material? | Offline derivation in the isolated challenge environment |
| Key identifier injection | Is `kid` used in a path, query, URL, or key lookup? | Controlled `kid` causes a distinct, observable key-selection path |
| Remote key metadata | Are `jku` or `x5u` fetched without allowlisting? | Request log from an authorized local issuer |
| Claim confusion | Are roles, audiences, or issuers compared with the wrong context? | Cross-service response difference |
| Expiry or revocation | Are `exp`, `nbf`, revocation, or token version checks enforced? | Time-bounded replay test in the lab |
| Parser differential | Do gateway and backend parse duplicate keys or encodings differently? | Both parser outputs and the resulting authorization decision |

Do not brute-force a production or public token secret. Any secret recovery must target keys supplied for the CTF challenge or explicitly authorized offline material.

## Verification standard

- The token was generated or modified only inside the authorized challenge environment.
- The algorithm expected by the verifier is stated from source or configuration.
- The key source and trust decision are explained.
- A negative control fails for the wrong reason, not merely because of a typo.
- The positive control changes one relevant field and reaches a non-destructive marker.
- Version-specific behavior is recorded.

## Pivot

Use [PHP source audit](php-audit.md) when the token path crosses PHP session or signature code. Use [SSRF](ssrf.md) when key discovery involves a server-side URL fetch. Route the surrounding web workflow to `ctf-web` and authentication-specific review to `broken-authentication`.
