"""Reviewed public-skill quality and UI presentation catalog.

This module is the source of truth for public discovery metadata. Update the
catalog when a public skill is added or its scope changes, then run:

    python scripts/apply_skill_quality.py --write
    python scripts/generate_agent_metadata.py --write
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillQuality:
    display_name: str
    short_description: str
    default_prompt: str
    description: str
    risk: str
    tags: tuple[str, ...]
    allowed_tools: tuple[str, ...]


_COMMON_CTF_TOOLS = (
    "Bash",
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Task",
    "WebFetch",
    "WebSearch",
)
_COMMON_WEB_TOOLS = (
    "Bash",
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Task",
    "WebFetch",
    "WebSearch",
)


QUALITY: dict[str, SkillQuality] = {
    "ctf-ai-ml": SkillQuality(
        display_name="CTF AI/ML",
        short_description="Solve ML, LLM, and adversarial AI CTF challenges.",
        default_prompt=(
            "Use $ctf-ai-ml to analyze this CTF AI/ML challenge, identify the vulnerable "
            "model behavior, and propose a reproducible solve path."
        ),
        description=(
            "Solve CTF challenges where machine learning or LLMs are the main obstacle, including "
            "adversarial examples, model extraction, prompt injection, membership inference, and model "
            "or adapter analysis."
        ),
        risk="offensive",
        tags=("ctf", "ai", "ml", "llm", "adversarial"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-crypto": SkillQuality(
        display_name="CTF Crypto",
        short_description="Break RSA, ECC, PRNG, ciphers, and crypto math challenges.",
        default_prompt=(
            "Use $ctf-crypto to analyze this CTF cryptography challenge and derive the flag from the "
            "supplied artifacts."
        ),
        description=(
            "Solve cryptography-first CTF challenges involving RSA, ECC, lattices, PRNGs, hashes, "
            "signatures, and block or stream cipher weaknesses. Do not use when crypto is incidental "
            "to a web or binary exploitation path."
        ),
        risk="offensive",
        tags=("ctf", "crypto", "rsa", "ecc", "lattice"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-forensics": SkillQuality(
        display_name="CTF Forensics",
        short_description="Analyze disk, memory, network, and signal CTF artifacts.",
        default_prompt=(
            "Use $ctf-forensics to analyze these CTF forensic artifacts and recover the evidence needed "
            "to answer the challenge."
        ),
        description=(
            "Analyze CTF disk images, memory dumps, PCAPs, logs, stego media, PDFs, registries, audio, "
            "and signal captures to recover evidence and flags. Use when forensic artifact analysis is "
            "the primary task."
        ),
        risk="offensive",
        tags=("ctf", "forensics", "disk", "memory", "stego"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-malware": SkillQuality(
        display_name="CTF Malware",
        short_description="Analyze malware, C2 traffic, obfuscation, and IOCs.",
        default_prompt=(
            "Use $ctf-malware to analyze this CTF malware sample or traffic capture and extract behavior, "
            "configuration, and indicators."
        ),
        description=(
            "Analyze CTF malware, obfuscated scripts, PE/.NET samples, C2 traffic, YARA matches, shellcode, "
            "and anti-analysis behavior. Use when understanding malicious code or infrastructure is the "
            "main task."
        ),
        risk="offensive",
        tags=("ctf", "malware", "reverse", "network", "ioc"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-misc": SkillQuality(
        display_name="CTF Misc",
        short_description="Triage encoding, jail, RF, and cross-category CTF puzzles.",
        default_prompt=(
            "Use $ctf-misc to triage this cross-category CTF challenge and test the most likely encoding, "
            "jail, RF, or puzzle path."
        ),
        description=(
            "Solve cross-category CTF puzzles such as encodings, pyjails, bash jails, RF/SDR, esoteric "
            "languages, games, and unusual sandboxes. Prefer a more specific CTF skill when the dominant "
            "category is clear."
        ),
        risk="offensive",
        tags=("ctf", "jail", "encoding", "rf", "misc"),
        allowed_tools=_COMMON_CTF_TOOLS + ("Skill",),
    ),
    "ctf-osint": SkillQuality(
        display_name="CTF OSINT",
        short_description="Investigate public sources, geolocation, and identities.",
        default_prompt=(
            "Use $ctf-osint to investigate this CTF OSINT question using lawful public sources and "
            "document each source."
        ),
        description=(
            "Investigate CTF questions using public sources, geolocation, reverse image search, DNS, "
            "username enumeration, archives, and social media. Use only for lawful public-source research "
            "and competition-scoped targets."
        ),
        risk="offensive",
        tags=("ctf", "osint", "geolocation", "social-media", "dns"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "ctf-pwn": SkillQuality(
        display_name="CTF Pwn",
        short_description="Exploit memory corruption, ROP, heap, and kernel targets.",
        default_prompt=(
            "Use $ctf-pwn to develop and validate an exploit for this CTF binary or service in its isolated "
            "challenge environment."
        ),
        description=(
            "Exploit CTF native binaries and services after the bug is understood, covering stack, heap, "
            "format-string, ROP, kernel, seccomp, and sandbox-escape paths. Use ctf-reverse first when the "
            "main blocker is understanding the binary."
        ),
        risk="offensive",
        tags=("ctf", "pwn", "binary", "exploitation", "kernel"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-reverse": SkillQuality(
        display_name="CTF Reverse",
        short_description="Reverse binaries, firmware, VMs, and obfuscated code.",
        default_prompt=(
            "Use $ctf-reverse to reverse this CTF target, recover its logic or key material, and document "
            "the solve path."
        ),
        description=(
            "Reverse CTF binaries, firmware, APKs, WASM, bytecode, custom VMs, and obfuscated loaders to "
            "recover logic or keys. Use ctf-pwn when exploitation is already the main task."
        ),
        risk="offensive",
        tags=("ctf", "reverse", "binary", "firmware", "wasm"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-web": SkillQuality(
        display_name="CTF Web",
        short_description="Exploit web, API, auth, and client-side CTF targets.",
        default_prompt=(
            "Use $ctf-web to analyze this CTF web target, identify the exploitable flaw, and validate the "
            "flag path."
        ),
        description=(
            "Exploit CTF web, API, browser, authentication, template, upload, and smart-contract surfaces "
            "including XSS, SQLi, SSTI, SSRF, XXE, JWT, and request smuggling."
        ),
        risk="offensive",
        tags=("ctf", "web", "api", "auth", "exploitation"),
        allowed_tools=_COMMON_CTF_TOOLS,
    ),
    "ctf-writeup": SkillQuality(
        display_name="CTF Writeup",
        short_description="Turn a solved CTF challenge into a clear technical writeup.",
        default_prompt=(
            "Use $ctf-writeup to turn the supplied CTF solution into a reproducible, evidence-backed "
            "writeup."
        ),
        description=(
            "Turn a solved CTF challenge into a concise, reproducible writeup covering the objective, "
            "evidence, solve path, commands, failed approaches, flag, and lessons learned."
        ),
        risk="safe",
        tags=("ctf", "writeup", "documentation", "reporting"),
        allowed_tools=("Read", "Write", "Edit", "Glob", "Grep"),
    ),
    "ctf-knowledge-base": SkillQuality(
        display_name="CTF Knowledge Base",
        short_description="Navigate curated CTF topics, writeups, and tooling.",
        default_prompt=(
            "Use $ctf-knowledge-base to find the most relevant authorized CTF technique, case "
            "pattern, or tool workflow in the indexed corpus."
        ),
        description=(
            "Navigate a curated CTF knowledge base covering web exploitation, PHP audit and "
            "deserialization, SQLi, SSRF, SSTI, file inclusion/upload, steganography, tool "
            "workflows, and writeup retrieval."
        ),
        risk="offensive",
        tags=("ctf", "knowledge-base", "web", "stego", "tooling"),
        allowed_tools=("Read", "Glob", "Grep", "Bash"),
    ),
    "solve-challenge": SkillQuality(
        display_name="CTF Challenge Router",
        short_description="Triage an unknown CTF challenge and route it correctly.",
        default_prompt=(
            "Use $solve-challenge to triage this unfamiliar CTF challenge and route it to the narrowest "
            "specialized skill."
        ),
        description=(
            "Triage an unfamiliar CTF bundle, remote service, or suspicious file, identify the dominant "
            "category, and route to the narrowest specialized CTF skill. Use after the category is known "
            "only to select a skill."
        ),
        risk="offensive",
        tags=("ctf", "triage", "routing", "methodology"),
        allowed_tools=_COMMON_CTF_TOOLS + ("Skill",),
    ),
    "api-fuzzing-bug-bounty": SkillQuality(
        display_name="API Fuzzing Bug Bounty",
        short_description="Test REST, SOAP, and GraphQL APIs for security flaws.",
        default_prompt=(
            "Use $api-fuzzing-bug-bounty to assess this explicitly authorized API target for security flaws "
            "with the API fuzzing workflow."
        ),
        description=(
            "Test explicitly authorized REST, SOAP, and GraphQL APIs for authentication, authorization, "
            "input handling, rate-limit, and business-logic flaws during bug bounty or penetration testing."
        ),
        risk="offensive",
        tags=("api", "web", "fuzzing", "bug-bounty", "graphql"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "aws-penetration-testing": SkillQuality(
        display_name="AWS Penetration Testing",
        short_description="Assess AWS IAM, S3, Lambda, and metadata attack paths.",
        default_prompt=(
            "Use $aws-penetration-testing to assess this explicitly authorized AWS environment and stay "
            "within the approved read-only or mutating scope."
        ),
        description=(
            "Assess explicitly authorized AWS environments for IAM, S3, Lambda, metadata-service, credential, "
            "persistence, and privilege-escalation risks. Scope every active or mutating action to written "
            "permission."
        ),
        risk="high",
        tags=("cloud", "aws", "iam", "s3", "lambda"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "broken-authentication": SkillQuality(
        display_name="Broken Authentication",
        short_description="Find authentication, session, and account recovery flaws.",
        default_prompt=(
            "Use $broken-authentication to review this explicitly authorized application for authentication, "
            "session, and account-takeover weaknesses."
        ),
        description=(
            "Assess authentication, session management, password recovery, MFA, token handling, and "
            "account-takeover risks in explicitly authorized web applications."
        ),
        risk="offensive",
        tags=("web", "authentication", "session", "owasp"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "ethical-hacking-methodology": SkillQuality(
        display_name="Ethical Hacking Methodology",
        short_description="Plan and run a full authorized penetration testing lifecycle.",
        default_prompt=(
            "Use $ethical-hacking-methodology to plan this authorized penetration test from scoping through "
            "reporting and cleanup."
        ),
        description=(
            "Plan and execute the full authorized penetration testing lifecycle from scoping and "
            "reconnaissance through validation, reporting, remediation, and cleanup."
        ),
        risk="offensive",
        tags=("methodology", "reconnaissance", "reporting", "penetration-testing"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "file-path-traversal": SkillQuality(
        display_name="File Path Traversal",
        short_description="Find and validate file path traversal vulnerabilities.",
        default_prompt=(
            "Use $file-path-traversal to test this explicitly authorized target for file path traversal and "
            "document safe evidence."
        ),
        description=(
            "Identify, validate, and explain file path traversal vulnerabilities in explicitly authorized "
            "applications, including encoding bypasses, absolute paths, and restricted-file-read impact."
        ),
        risk="offensive",
        tags=("web", "path-traversal", "file-read", "owasp"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "html-injection-testing": SkillQuality(
        display_name="HTML Injection Testing",
        short_description="Test applications for HTML injection and content spoofing.",
        default_prompt=(
            "Use $html-injection-testing to test this explicitly authorized application for HTML injection "
            "and content-spoofing impact."
        ),
        description=(
            "Test explicitly authorized web applications for HTML injection, content spoofing, phishing "
            "surfaces, form injection, and sanitization gaps. Pair with XSS testing when script execution is "
            "also in scope."
        ),
        risk="offensive",
        tags=("web", "html-injection", "xss", "phishing"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "idor-testing": SkillQuality(
        display_name="IDOR Testing",
        short_description="Find broken object-level authorization and IDOR flaws.",
        default_prompt=(
            "Use $idor-testing to test this explicitly authorized web or API surface for IDOR and broken "
            "object-level authorization."
        ),
        description=(
            "Find and validate broken object-level authorization in explicitly authorized web and API "
            "targets, including identifier enumeration, tenant boundaries, and horizontal or vertical access."
        ),
        risk="offensive",
        tags=("web", "idor", "authorization", "api"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "linux-privilege-escalation": SkillQuality(
        display_name="Linux Privilege Escalation",
        short_description="Enumerate and exploit Linux privilege escalation paths.",
        default_prompt=(
            "Use $linux-privilege-escalation to enumerate privilege escalation paths on this explicitly "
            "authorized Linux host."
        ),
        description=(
            "Enumerate and validate Linux privilege escalation paths on explicitly authorized hosts, covering "
            "sudo, SUID, capabilities, cron, services, credentials, containers, and kernel exposure."
        ),
        risk="high",
        tags=("linux", "privilege-escalation", "post-exploitation"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "metasploit-framework": SkillQuality(
        display_name="Metasploit Framework",
        short_description="Use Metasploit modules, payloads, and sessions safely.",
        default_prompt=(
            "Use $metasploit-framework against this explicitly authorized target and validate the selected "
            "module safely."
        ),
        description=(
            "Use Metasploit Framework for explicitly authorized assessments, including module selection, "
            "target validation, payload configuration, session handling, and evidence capture."
        ),
        risk="high",
        tags=("tooling", "metasploit", "exploitation", "payload"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "pentest-checklist": SkillQuality(
        display_name="Pentest Checklist",
        short_description="Plan, execute, and close out authorized penetration tests.",
        default_prompt=(
            "Use $pentest-checklist to build a scoped checklist and evidence plan for this authorized "
            "penetration test."
        ),
        description=(
            "Plan, scope, execute, and close out an authorized penetration test with coverage tracking, "
            "evidence standards, risk communication, cleanup, and remediation follow-up."
        ),
        risk="offensive",
        tags=("methodology", "checklist", "reporting", "scoping"),
        allowed_tools=("Read", "Write", "Edit", "Glob", "Grep"),
    ),
    "pentest-commands": SkillQuality(
        display_name="Pentest Commands",
        short_description="Look up authorized penetration testing commands quickly.",
        default_prompt=(
            "Use $pentest-commands to find the appropriate authorized penetration testing command for this "
            "task and explain its safety constraints."
        ),
        description=(
            "Look up common authorized penetration testing commands for reconnaissance, enumeration, web "
            "testing, exploitation, and post-exploitation without replacing a focused workflow skill."
        ),
        risk="offensive",
        tags=("reference", "commands", "tooling", "pentesting"),
        allowed_tools=("Read", "Glob", "Grep"),
    ),
    "privilege-escalation-methods": SkillQuality(
        display_name="Privilege Escalation Methods",
        short_description="Compare Linux and Windows privilege escalation techniques.",
        default_prompt=(
            "Use $privilege-escalation-methods to compare and prioritize privilege escalation paths on this "
            "explicitly authorized Linux or Windows host."
        ),
        description=(
            "Compare Linux and Windows privilege escalation techniques for explicitly authorized "
            "post-exploitation, from enumeration and local misconfiguration to validated administrative "
            "access."
        ),
        risk="high",
        tags=("linux", "windows", "privilege-escalation", "post-exploitation"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "red-team-tools": SkillQuality(
        display_name="Red Team Tools",
        short_description="Select and chain reconnaissance and security tooling.",
        default_prompt=(
            "Use $red-team-tools to select and chain tools for this explicitly authorized engagement."
        ),
        description=(
            "Select and chain reconnaissance, vulnerability discovery, and bug-bounty tooling for an "
            "explicitly authorized engagement. Use when tool choice or workflow comparison is the main "
            "question."
        ),
        risk="offensive",
        tags=("reconnaissance", "tooling", "bug-bounty", "red-team"),
        allowed_tools=("Read", "Glob", "Grep", "WebFetch", "WebSearch"),
    ),
    "scanning-tools": SkillQuality(
        display_name="Scanning Tools",
        short_description="Choose and run authorized network and vulnerability scanners.",
        default_prompt=(
            "Use $scanning-tools to select and run scanners against only this explicitly authorized scope."
        ),
        description=(
            "Choose and operate network, web, wireless, and vulnerability scanners for explicitly authorized "
            "assessments, including scope controls, safe defaults, result validation, and evidence capture."
        ),
        risk="offensive",
        tags=("network", "scanning", "vulnerability-assessment", "tooling"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "shodan-reconnaissance": SkillQuality(
        display_name="Shodan Reconnaissance",
        short_description="Assess exposure through Shodan search and host intelligence.",
        default_prompt=(
            "Use $shodan-reconnaissance to assess this explicitly authorized organization's public exposure "
            "in Shodan."
        ),
        description=(
            "Use Shodan to map an explicitly authorized organization's internet exposure, identify services "
            "and versions, and pivot into validated reconnaissance without treating search results as "
            "permission to test."
        ),
        risk="offensive",
        tags=("reconnaissance", "shodan", "osint", "exposure"),
        allowed_tools=("Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch"),
    ),
    "smtp-penetration-testing": SkillQuality(
        display_name="SMTP Penetration Testing",
        short_description="Assess SMTP relays, users, authentication, and configuration.",
        default_prompt=(
            "Use $smtp-penetration-testing to assess this explicitly authorized SMTP service for "
            "configuration and authentication weaknesses."
        ),
        description=(
            "Assess explicitly authorized SMTP services for relay behavior, user enumeration, authentication "
            "weaknesses, TLS configuration, and mail-routing exposure."
        ),
        risk="offensive",
        tags=("smtp", "email", "network", "authentication"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "sql-injection-testing": SkillQuality(
        display_name="SQL Injection Testing",
        short_description="Validate SQL injection manually and reason about impact.",
        default_prompt=(
            "Use $sql-injection-testing to validate suspected SQL injection in this explicitly authorized "
            "application with minimal-impact evidence."
        ),
        description=(
            "Validate SQL injection manually in explicitly authorized applications, reason from input to "
            "query behavior, and demonstrate impact with safe evidence and remediation guidance."
        ),
        risk="offensive",
        tags=("web", "sql-injection", "database", "owasp"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "sqlmap-database-pentesting": SkillQuality(
        display_name="SQLMap Database Pentesting",
        short_description="Use SQLMap for authorized SQL injection validation.",
        default_prompt=(
            "Use $sqlmap-database-pentesting against this explicitly authorized endpoint with conservative, "
            "scoped SQLMap options."
        ),
        description=(
            "Use SQLMap for explicitly authorized SQL injection discovery and validation, with scoped "
            "requests, conservative tampering, evidence capture, and minimal data extraction."
        ),
        risk="offensive",
        tags=("web", "sql-injection", "sqlmap", "tooling"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "ssh-penetration-testing": SkillQuality(
        display_name="SSH Penetration Testing",
        short_description="Assess SSH configuration, credentials, tunnels, and exposure.",
        default_prompt=(
            "Use $ssh-penetration-testing to assess this explicitly authorized SSH service and document "
            "configuration and access risks."
        ),
        description=(
            "Assess explicitly authorized SSH services for weak configuration, credential exposure, "
            "authentication issues, tunneling paths, and post-access risk."
        ),
        risk="offensive",
        tags=("ssh", "network", "credentials", "tunneling"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "top-web-vulnerabilities": SkillQuality(
        display_name="Top Web Vulnerabilities",
        short_description="Map common web vulnerabilities to impact and remediation.",
        default_prompt=(
            "Use $top-web-vulnerabilities to triage these authorized web findings against common "
            "vulnerability and remediation guidance."
        ),
        description=(
            "Use a taxonomy of common web vulnerabilities for triage, impact assessment, and remediation "
            "planning. Prefer a specific active-testing skill once the vulnerability class is known."
        ),
        risk="reference",
        tags=("web", "owasp", "reference", "remediation"),
        allowed_tools=("Read", "Glob", "Grep", "WebFetch", "WebSearch"),
    ),
    "windows-privilege-escalation": SkillQuality(
        display_name="Windows Privilege Escalation",
        short_description="Enumerate and exploit Windows privilege escalation paths.",
        default_prompt=(
            "Use $windows-privilege-escalation to enumerate privilege escalation paths on this explicitly "
            "authorized Windows host."
        ),
        description=(
            "Enumerate and validate Windows privilege escalation paths on explicitly authorized hosts, "
            "covering tokens, services, scheduled tasks, ACLs, credentials, and local misconfigurations."
        ),
        risk="high",
        tags=("windows", "privilege-escalation", "post-exploitation"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "wireshark-analysis": SkillQuality(
        display_name="Wireshark Analysis",
        short_description="Analyze packet captures and investigate network behavior.",
        default_prompt=(
            "Use $wireshark-analysis to analyze this packet capture for the requested security investigation "
            "and preserve evidence."
        ),
        description=(
            "Analyze packet captures with Wireshark and tshark for explicitly authorized investigations, "
            "including protocol filtering, traffic reconstruction, credential exposure, and evidence capture."
        ),
        risk="offensive",
        tags=("network", "pcap", "wireshark", "forensics"),
        allowed_tools=("Bash", "Read", "Write", "Edit", "Glob", "Grep"),
    ),
    "wordpress-penetration-testing": SkillQuality(
        display_name="WordPress Penetration Testing",
        short_description="Assess WordPress plugins, themes, users, and configuration.",
        default_prompt=(
            "Use $wordpress-penetration-testing to assess this explicitly authorized WordPress installation "
            "for common configuration and component weaknesses."
        ),
        description=(
            "Assess explicitly authorized WordPress installations for core, plugin, theme, user, "
            "authentication, upload, and configuration weaknesses without relying on destructive exploitation."
        ),
        risk="offensive",
        tags=("web", "wordpress", "cms", "plugins"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "xss-html-injection": SkillQuality(
        display_name="XSS and HTML Injection",
        short_description="Test reflected, stored, and DOM XSS and HTML injection.",
        default_prompt=(
            "Use $xss-html-injection to test this explicitly authorized application for XSS and HTML "
            "injection with safe proof."
        ),
        description=(
            "Test explicitly authorized web applications for reflected, stored, and DOM-based XSS and HTML "
            "injection, including browser context, payload validation, impact, and remediation."
        ),
        risk="offensive",
        tags=("web", "xss", "html-injection", "client-side"),
        allowed_tools=_COMMON_WEB_TOOLS,
    ),
    "agentic-actions-auditor": SkillQuality(
        display_name="Agentic Actions Auditor",
        short_description="Audit AI-agent GitHub Actions for trust and permission flaws.",
        default_prompt=(
            "Use $agentic-actions-auditor to audit this GitHub Actions setup for AI-agent trust, permission, "
            "and secret-handling flaws."
        ),
        description=(
            "Audit GitHub Actions workflows that invoke AI agents for trust-boundary, permission, "
            "prompt-injection, secret-exposure, and supply-chain risks. Focus on CI/CD evidence and remediation."
        ),
        risk="safe",
        tags=("github-actions", "ci-cd", "ai-agents", "supply-chain", "audit"),
        allowed_tools=("Bash", "Read", "Grep", "Glob", "WebFetch"),
    ),
    "burpsuite-project-parser": SkillQuality(
        display_name="Burp Suite Project Parser",
        short_description="Search Burp projects for HTTP evidence and findings.",
        default_prompt=(
            "Use $burpsuite-project-parser to search this Burp Suite project for the requested HTTP evidence "
            "and summarize the findings."
        ),
        description=(
            "Search and explore Burp Suite project files from the command line to recover HTTP history, "
            "response evidence, site maps, and audit findings. Passive local analysis only."
        ),
        risk="safe",
        tags=("burp-suite", "http", "evidence", "parsing"),
        allowed_tools=("Bash", "Read"),
    ),
    "semgrep-rule-creator": SkillQuality(
        display_name="Semgrep Rule Creator",
        short_description="Write and validate custom Semgrep security rules.",
        default_prompt=(
            "Use $semgrep-rule-creator to create and validate Semgrep rules for the requested vulnerability "
            "pattern."
        ),
        description=(
            "Create, test, and refine custom Semgrep rules for security vulnerabilities and bug patterns in "
            "source code. Use for static-analysis detection work, not live target exploitation."
        ),
        risk="safe",
        tags=("semgrep", "sast", "static-analysis", "rules"),
        allowed_tools=("Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch"),
    ),
}
