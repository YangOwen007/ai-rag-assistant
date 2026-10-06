# Security

This project currently supports a trusted private shared workspace. There are no user accounts or ownership checks. Access to the UI includes access to the full collection and deletion API. Do not expose it anonymously or use it for sensitive documents.

Report a suspected vulnerability using GitHub's private vulnerability reporting feature if enabled. If unavailable, open an issue requesting a private contact without including exploit payloads, credentials, or private documents. No response-time promise is made.

Never commit `.env` files, database files, dumps, logs, provider keys, or screenshots containing private source material. If a real key was committed, rotate/revoke it first; removing a file does not remove the key from history or invalidate it. History rewrites require a separate coordinated plan.

Use dependency audits and secret scans before releases. A clean scan is evidence about its coverage, not proof that all vulnerabilities or private data have been found. PDF parsing still requires process isolation and resource limits before untrusted public uploads.
