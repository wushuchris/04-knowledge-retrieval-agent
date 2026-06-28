---
title: NimbusNote Knowledge Base — Customer Support Playbook
---

# Customer Support Playbook

This playbook outlines common customer support procedures for NimbusNote Knowledge Base (fictional demo content).

## Enterprise Onboarding

- Kickoff: Assign a Customer Success Manager (CSM) and schedule a kickoff meeting to map user roles, SSO setup, and export/import requirements.
- Data migration: Use the enterprise import tool to bulk-upload documents. Validate mapping and permissions in a staging workspace.
- Training: Provide a two-week onboarding program including admin training, user webinars, and handoff documentation.

## Password Reset

- Self-service: Users can reset passwords via the `Forgot password` flow which sends a time-limited link (expires in 1 hour).
- Verification: For enterprise accounts with SSO, password resets are managed by the identity provider; support should verify SSO status before assisting.

## Support Escalation

- Tier 1: Basic account and usage questions handled by support agents within 24 hours.
- Tier 2: Technical issues (API, ingestion errors) escalated to engineering with a 48-hour SLA for initial response.
- Tier 3: Security incidents or data-loss events trigger the incident response playbook and immediate CSM notification.

## Best Practices

- Collect logs (timestamped, anonymized IDs) and screenshots when opening support tickets.
- Reproduce issues in a staging workspace before applying fixes to production customer data.

This document is fictional and designed to provide realistic retrieval targets for demo testing.
