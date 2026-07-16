# Security and sensitive-data reporting

## Supported code

Security reports should address the current `main` branch. This research software is not approved for clinical operation or for processing identifiable health information in an uncontrolled environment.

## Report privately

Use the repository host's private security-advisory channel for vulnerabilities, exposed credentials, or accidentally published sensitive data. Do not open a public issue containing patient information, a secret, a private link, or the contents of a restricted artifact.

Include a concise description, affected file or component, reproduction steps using non-sensitive inputs, and potential impact. Redact secrets and patient information from screenshots, logs, and attachments.

## Immediate handling

If sensitive content is discovered:

1. Stop further distribution or processing of the affected material.
2. Do not copy the value into a public issue, commit, or chat transcript.
3. Revoke or rotate an exposed credential through its provider.
4. Preserve only the minimum non-sensitive evidence needed for investigation.
5. Notify the repository maintainers through the private reporting channel.

## Scope boundary

Dataset-access questions and scientific-method discussions are not security vulnerabilities. They may be raised through normal repository discussion only when no private data or credentials are included. The complete data boundary is documented in [`docs/privacy_and_data_boundary.md`](docs/privacy_and_data_boundary.md).
