# Packet analysis workflow

Authorized CTF and owned-lab use only.

## Objective

Use Wireshark or tshark to move from a packet capture to a reproducible evidence trail: capture summary, conversations, protocol hierarchy, filtered streams, extracted objects, and a final interpretation.

## Baseline with tshark

```bash
tshark -r capture.pcapng -q -z io,phs
tshark -r capture.pcapng -q -z endpoints,ip
tshark -r capture.pcapng -q -z conv,tcp
```

Flags and statistic names vary by version. Check `tshark -h` and the installed protocol dissectors.

## Analysis order

1. Identify capture interfaces, duration, packet count, and truncation.
2. Review protocol hierarchy and endpoint/conversation counts.
3. Find unusual ports, DNS names, certificate metadata, or repeated payloads.
4. Follow one conversation and keep the stream number.
5. Extract application objects only after identifying their protocol and destination.
6. Correlate packet timestamps with logs or challenge events.
7. Preserve a minimal filter and the exact fields used for each conclusion.

## Display filters

```bash
tshark -r capture.pcapng -Y 'http.request' \
  -T fields -e frame.number -e ip.src -e ip.dst -e http.host -e http.request.uri

tshark -r capture.pcapng -Y 'dns' \
  -T fields -e frame.number -e dns.qry.name -e dns.a

tshark -r capture.pcapng -Y 'tls.handshake.extensions_server_name' \
  -T fields -e frame.number -e tls.handshake.extensions_server_name
```

Start with a broad filter and narrow it. A filter that accidentally excludes the relevant packet can hide the answer.

## Follow streams and export objects

```bash
tshark -r capture.pcapng -q -z follow,tcp,ascii,0
tshark -r capture.pcapng --export-objects http,exported-http
```

Check the stream number, direction, and decoded bytes. Exported objects must be treated as untrusted content. Store them in a dedicated directory and inspect type and size before opening.

## Protocol-specific questions

| Protocol | Useful checks |
|---|---|
| DNS | Query names, response codes, TXT records, retries, tunneling-like payloads |
| HTTP | Methods, hosts, paths, headers, chunking, cookies, uploads, encoded bodies |
| TLS | SNI, certificates, handshake failures, provided session or key-log artifacts |
| SMB/FTP/SMTP | Authentication exchanges, file transfer names, command sequences |
| USB/HID | Device descriptors, report lengths, timing, axis/button changes |
| Custom TCP/UDP | Framing, length fields, compression, encryption, repeated handshakes |

Do not attempt to decrypt traffic merely because a capture exists. Use a key log or test key supplied with the challenge, and only within the authorized environment.

## Evidence standard

- Capture hash and basic capture metadata.
- Version of Wireshark/tshark.
- Exact display filter or stream number.
- Relevant packet numbers and extracted object hashes.
- A rendered/decoded view plus a second check where possible.
- The boundary between observed traffic and inferred intent.

## Pivot

Use `ctf-forensics` for disk, memory, or broader evidence handling. Route application-level findings to the matching web or malware skill. Use `wireshark-analysis` for an authorized non-CTF capture workflow.
