# k6 performance verification plan

Status: PLANNED, **NOT_RUN**.

## Controlled execution
Run against local or dedicated staging environment with synthetic data only. Confirm permission and resource budgets before any load against shared endpoints.

| Scenario | Purpose | Required result |
|---|---|---|
| smoke | One virtual user, core API health | Stable response schema, low error rate |
| load | Expected sustained traffic | Error rate, p95 latency and throughput measured |
| stress | Find degraded behavior | Controlled resource consumption, documented knee point |
| spike | Abrupt concurrency change | Recovery time and error behavior |
| soak | Long-running stability | Memory growth, connection leaks, error drift |

## Evidence to capture
Git SHA, container image digests, hardware/resources, runtime versions, dataset size, duration, virtual users, request metrics, p95/p99, errors, CPU/memory and DB pool usage. Thresholds must be set from defined baseline/SLO and enforced by k6 exit status; do not invent universal latency limits.

## Release condition
No k6 PASS claim until results, commands, configuration and exact commit evidence are attached to SBP-003. A partially executed scenario must be marked PARTIAL, not PASS.
