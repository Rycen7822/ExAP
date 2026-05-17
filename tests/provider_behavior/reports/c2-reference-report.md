# ExAP C2 Provider Behavior Report

Generated: 2026-05-17T17:28:20.755532+00:00
Level: C2
Git commit: `c5087c6`
ExAP version: `0.2.0-draft`
Adapter: `reference.exapd.provider:ReferenceProviderAdapter`
Summary: 10/10 cases PASS

| Case | Status | Step count |
|---|---:|---:|
| C2-00 discover capability | PASS | 5 |
| C2-01 contract.create validate_only | PASS | 3 |
| C2-02 contract.create activate and idempotency | PASS | 4 |
| C2-03 contract get list status | PASS | 4 |
| C2-04 contract update pause resume revoke | PASS | 6 |
| C2-05 wait timeout attention interrupted | PASS | 4 |
| C2-06 stream.open frames | PASS | 2 |
| C2-07 attention ack actions | PASS | 5 |
| C2-08 observation.query pagination | PASS | 2 |
| C2-09 error mapping | PASS | 5 |

## Case Details

### C2-00. discover capability

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.discover schema-valid success envelope | PASS | valid success response | valid |
| discover returns package version | PASS | 0.2.0-draft in exap_versions | ['0.2.0-draft'] |
| discover exposes signals/events/operators/delivery/profiles | PASS | non-empty capability surfaces | {"signals": true, "event_types": true, "profiles": true, "rule_capabilities": true, "delivery_capabilities": true} |
| exap.discover schema-valid success envelope | PASS | valid success response | valid |
| discover profile filter returns mail capability | PASS | cap_mail_001 | cap_mail_001 |

### C2-01. contract.create validate_only

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.contract.create schema-valid success envelope | PASS | valid success response | valid |
| validate_only returns draft effective contract | PASS | draft and same contract_id | {"contract_id": "act_process_wait_001", "status": "draft", "effective_contract": {"exap_version": "0.2.0-draft", "contract_id": "act_process_wait_001", "created_at": "2026-05-16T12:00:00+09:00", "consumer": {"consumer_id": "agent:codex-local", "type": "agent", "display_name": "Codex local agent", "capabilities": {"blocking_wait": true, "mcp": true}}, "provider": {"provider_id": "local-process-provider", "type": "local_daemon", "version": "0.2.0"}, "environment_ref": "exap://local/machine/worksta |
| validate_only does not mutate provider state | PASS | contract count 0 | 0 |

### C2-02. contract.create activate and idempotency

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.contract.create schema-valid success envelope | PASS | valid success response | valid |
| exap.contract.create schema-valid success envelope | PASS | valid success response | valid |
| idempotent create returns same contract_id | PASS | act_process_wait_001 twice | act_process_wait_001, act_process_wait_001 |
| created contract is active | PASS | active | {"contract_id": "act_process_wait_001", "status": "active", "version": "1", "recent_events": []} |

### C2-03. contract get list status

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.contract.get schema-valid success envelope | PASS | valid success response | valid |
| exap.contract.list schema-valid success envelope | PASS | valid success response | valid |
| exap.status schema-valid success envelope | PASS | valid success response | valid |
| get/list/status agree on contract_id | PASS | same contract_id across methods | {"get": "act_process_wait_001", "list_count": 1, "status": "act_process_wait_001"} |

### C2-04. contract update pause resume revoke

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.contract.create schema-valid success envelope | PASS | valid success response | valid |
| exap.contract.update schema-valid success envelope | PASS | valid success response | valid |
| exap.contract.pause schema-valid success envelope | PASS | valid success response | valid |
| exap.contract.resume schema-valid success envelope | PASS | valid success response | valid |
| exap.contract.revoke schema-valid success envelope | PASS | valid success response | valid |
| update/pause/resume/revoke statuses are deterministic | PASS | active -> paused -> active -> revoked | ["active", "paused", "active", "revoked"] |

### C2-05. wait timeout attention interrupted

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.wait schema-valid success envelope | PASS | valid success response | valid |
| exap.wait schema-valid success envelope | PASS | valid success response | valid |
| exap.wait schema-valid success envelope | PASS | valid success response | valid |
| wait covers timeout attention interrupted | PASS | three return reasons and valid event | valid |

### C2-06. stream.open frames

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.stream.open schema-valid success envelope | PASS | valid success response | valid |
| stream metadata and keepalive/event/error frames | PASS | metadata plus keepalive/event/error | {"metadata": {"contract_id": "act_process_wait_001", "stream_id": "stream_act_process_wait_001", "status": "active", "cursor": "cursor_start"}, "frame_types": ["keepalive", "event", "error"], "event_errors": []} |

### C2-07. attention ack actions

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.attention.ack schema-valid success envelope | PASS | valid success response | valid |
| exap.attention.ack schema-valid success envelope | PASS | valid success response | valid |
| exap.attention.ack schema-valid success envelope | PASS | valid success response | valid |
| exap.attention.ack schema-valid success envelope | PASS | valid success response | valid |
| ack actions map to stable statuses | PASS | {"seen": "acknowledged", "snooze": "snoozed", "dismiss": "dismissed", "escalate": "escalated"} | {"seen": "acknowledged", "snooze": "snoozed", "dismiss": "dismissed", "escalate": "escalated"} |

### C2-08. observation.query pagination

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.observation.query schema-valid success envelope | PASS | valid success response | valid |
| observation.query returns schema-valid paginated items | PASS | one gpu.util.percent item | [{"observation_id": "obs_gpu_util_001", "subject_ref": "exap://local/gpu/0", "signal": "gpu.util.percent", "value": 4.2, "observed_at": "2026-05-16T12:07:00+09:00", "source": "reference-process-provider"}] |

### C2-09. error mapping

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| exap.contract.get maps error ExAP-4040 | PASS | code=-32004, exap_code=ExAP-4040, retryable present | {"code": -32004, "data": {"exap_code": "ExAP-4040", "field": "params.contract_id", "retryable": false}, "message": "Contract not found"} |
| exap.contract.create maps error ExAP-4006 | PASS | code=-32602, exap_code=ExAP-4006, retryable present | {"code": -32602, "data": {"exap_code": "ExAP-4006", "field": "params.contract", "retryable": false}, "message": "Contract is not compatible with provider capability"} |
| exap.contract.create maps error ExAP-4006 | PASS | code=-32602, exap_code=ExAP-4006, retryable present | {"code": -32602, "data": {"exap_code": "ExAP-4006", "field": "params.contract", "retryable": false}, "message": "Contract is not compatible with provider capability"} |
| exap.contract.create maps error ExAP-4006 | PASS | code=-32602, exap_code=ExAP-4006, retryable present | {"code": -32602, "data": {"exap_code": "ExAP-4006", "field": "params.contract", "retryable": false}, "message": "Contract is not compatible with provider capability"} |
| exap.contract.update maps error ExAP-4090 | PASS | code=-32009, exap_code=ExAP-4090, retryable present | {"code": -32009, "data": {"exap_code": "ExAP-4090", "field": "params.expected_version", "retryable": true}, "message": "Contract version conflict"} |

## Rerun

```bash
python tests/provider_behavior/run_c2.py --adapter reference.exapd.provider:ReferenceProviderAdapter --report /home/xu/project/exap/ExAP/tests/provider_behavior/reports/c2-reference-report.md
```
