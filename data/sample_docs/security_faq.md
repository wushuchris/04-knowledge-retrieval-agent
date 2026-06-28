---
title: NimbusNote Knowledge Base — Security FAQ
---

# Security FAQ

Fictional security and compliance guidance for the NimbusNote Knowledge Base demo.

## Security Controls

- Encryption: Data is encrypted at rest and in transit using industry-standard TLS and AES-256 (demo description).
- Access Controls: Role-based access control (RBAC) is available for workspace admins, editors, and viewers.

## Single Sign-On (SSO)

- Supported providers: SAML 2.0 and OIDC integrations are supported for enterprise workspaces.
- Setup: Admins configure SSO in `Settings → Security → SSO` and test with a staging identity provider before enabling for all users.

## Audit Logs

- Events: Audit logs record key events such as logins, document exports, permission changes, and sharing link creations.
- Retention: Audit logs are retained for 365 days for enterprise plans and are downloadable as CSV for compliance reviews.

## Document Sharing Permissions (security perspective)

- Least privilege: Recommend granting `view` rather than `edit` where possible and using time-limited links for external sharing.
- Revocation: Admins can revoke shared links and remove collaborators at any time; revocations are recorded in audit logs.

This FAQ is fictional and safe for public demo use; use it to test security-related retrieval queries.
