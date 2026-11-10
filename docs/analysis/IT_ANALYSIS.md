# IT analysis — Secure Backend Platform

**Status: draft.** Project: **Secure Backend Platform** (`secure-backend-platform`, repository rename pending from `TESENA_pohovor`). This document proposes acceptance criteria, not production features.

## Business objective
Present a credible, reproducible Python backend project illustrating security-aware architecture, data consistency, API design, CI quality gates and performance engineering.

## Stakeholders
Developer, code reviewer, security engineer and operator. The user-facing frontend is a demonstration client, not the core portfolio objective.

## Requirements
- SBP-F01: A clean clone starts backend, database and UI using documented configuration.
- SBP-F02: Authentication and authorization are exercised by real negative and positive tests.
- SBP-F03: Database migrations are deterministic and repeatable, including failure recovery.
- SBP-F04: k6 can execute smoke/load/stress/spike/soak against an isolated seeded service.
- SBP-F05: Metrics for request duration, throughput, errors and system availability are reproducible.
- SBP-F06: CI emits machine-verifiable evidence tied to a precise commit.
- SBP-N01: No secrets or organizational proprietary data in published sources.
- SBP-N02: Prefer lightweight architecture over microservices and unnecessary infrastructure.
- SBP-N03: Distinguish upstream template functionality from documented original additions.

## Risks and mitigation hypotheses
- Committed .env or deployment credentials → history audit, rotation, safer config samples.
- Improper object-level authorization → negative API tests and policy checks.
- Unbounded writes or expensive queries → limits, database constraints, load testing.
- Missing CI evidence → fail-closed validator, exact SHA matching.
- Template confusion → explicit attribution and original-work changelog.

## Acceptance
Each requirement links to a GitHub Issue and exact-commit evidence. Architecture must reflect running code, not a fictional intended deployment.
