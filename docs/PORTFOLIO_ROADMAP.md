# Secure Backend Platform — portfolio roadmap

Status: **DRAFT / NOT VERIFIED**. Current repository name: `TESENA_pohovor`; proposed name: `secure-backend-platform`.

## Scope and provenance
- Separate features inherited from the upstream Full Stack FastAPI Template from demonstrably original work.
- Do not claim production security or successful tests without exact-commit evidence.
- Avoid duplicating Backend Factory: this repository demonstrates application architecture, API security, performance and observability; Backend Factory demonstrates AI-assisted software delivery and governance.

## Release milestones
| Release | Goal | Required evidence |
| --- | --- | --- |
| 0.1 | Ownership, licensing and secret-history audit | Reviewed provenance and redacted secrets; credential rotation if needed |
| 0.2 | Architecture + IT analysis | C4 context/container/component diagrams, ADRs, data flows, STRIDE model |
| 0.3 | Reproducible backend and security verification | Clean-clone startup, real pytest/API/authorization tests and scan results |
| 0.4 | k6 performance tests | Isolated smoke/load/stress/spike/soak; latency, errors, resource metrics |
| 0.5 | Observability and CI | Prometheus/Grafana dashboards, enforced CI gates and immutable evidence |
| 1.0 | Portfolio release | Demo, screenshots, runbook, documented limitations and all P0/P1 gates PASS |

## Release blockers
- [ ] P0: Ownership/upstream attribution and licensing established.
- [ ] P0: No unresolved active secrets in repo/history.
- [ ] P0: Backend and DB start from clean checkout.
- [ ] P0: Authentication, authorization and key API paths tested.
- [ ] P1: Architecture and threat model match implementation.
- [ ] P1: k6 performance scenarios actually executed.
- [ ] P1: CI blocks incomplete evidence.
- [ ] P1: README distinguishes IMPLEMENTED from PLANNED.

## Tasks
GitHub Issues are the work tracker; each issue should contain acceptance criteria and tested commit SHA. Updating this checklist requires verifiable output, not just closing an issue.
