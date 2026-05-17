# ExAP Reference Smoke Report

Generated: 2026-05-17T17:28:22.199142+00:00
Level: R4 smoke
Git commit: `c5087c6`
ExAP version: `0.2.0-draft`
Provider adapter: `reference.exapd.provider:ReferenceProviderAdapter`
Targets: openapi, mcp, a2a, operations
Summary: 4/4 targets PASS

| Target | Status | Step count |
|---|---:|---:|
| openapi | PASS | 3 |
| mcp | PASS | 3 |
| a2a | PASS | 3 |
| operations | PASS | 4 |

## Details

### openapi

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| OpenAPI includes lifecycle smoke endpoints | PASS | ['/exap/attention/{attention_id}/ack', '/exap/capability', '/exap/contracts', '/exap/contracts/{contract_id}', '/exap/contracts/{contract_id}/status', '/exap/contracts/{contract_id}/wait'] | ['/exap/attention/{attention_id}/ack', '/exap/capability', '/exap/contracts', '/exap/contracts/{contract_id}', '/exap/contracts/{contract_id}/status', '/exap/contracts/{contract_id}/wait'] |
| reference provider passes shared C2 runner | PASS | 10/10 C2 cases PASS | 10/10 C2 cases PASS |
| HTTP create/wait/status/ack/revoke smoke | PASS | all status=200 with result | {"create": 200, "wait": 200, "status": 200, "ack": 200, "revoke": 200} |

### mcp

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| MCP exposes six lifecycle tools | PASS | ['exap_attention_ack', 'exap_contract_create', 'exap_contract_revoke', 'exap_discover', 'exap_status', 'exap_wait'] | ['exap_attention_ack', 'exap_contract_create', 'exap_contract_revoke', 'exap_discover', 'exap_status', 'exap_wait'] |
| MCP tool calls return ExAP result envelopes | PASS | all content.result present | {"create": true, "wait": true, "status": true, "ack": true, "revoke": true} |
| MCP capability resource is readable | PASS | cap_local_process_001 | cap_local_process_001 |

### a2a

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| A2A card exposes create/wait/ack/revoke skills | PASS | four ExAP skills | ['ack_attention_event', 'create_attention_contract', 'revoke_attention_contract', 'wait_for_attention'] |
| A2A text/plain returns validate-only draft | PASS | draft and no active contract | {"skill": "create_attention_contract", "state": "completed", "artifacts": [{"mediaType": "application/exap+json", "data": {"contract_id": "act_email_priority_001", "status": "draft", "effective_contract": {"exap_version": "0.2.0-draft", "contract_id": "act_email_priority_001", "created_at": "2026-05-16T09:00:00+09:00", "consumer": {"consumer_id": "app:desktop-assistant", "type": "application", "display_name": "Desktop Assistant", "capabilities": {"push": true, "ack": true}}, "provider": {"provider_id": "mail-provider", "type": "connector", "version": "0.2.0"}, "environment_ref": "exap://personal/workspace/default", "intent": "notify me about urgent approval requests", "scope": {"subjects": [ |
| A2A structured JSON creates active contract and returns ExAP artifacts | PASS | completed application/exap+json artifacts | {"create": "completed", "wait": "completed", "ack": "completed", "revoke": "completed"} |

### operations

Status: PASS

| Step | Status | Expected | Actual |
|---|---:|---|---|
| /healthz returns expected body | PASS | {"status": "ok", "component": "exapd", "version": "0.2.0-draft"} | {"status": "ok", "component": "exapd", "version": "0.2.0-draft"} |
| /readyz returns ready body | PASS | {"status": "ready", "capabilities_loaded": 2} | {"status": "ready", "capabilities_loaded": 2, "contracts": 0} |
| /metrics exposes expected metric names | PASS | metric tokens present | # HELP exap_contracts_total Number of contracts in memory.
# TYPE exap_contracts_total gauge
exap_contracts_total 0
# HELP exap_audit_records_total Number of lifecycle requests recorded.
# TYPE exap_audit_records_total counter
exap_audit_records_total 0
 |
| DLQ query returns empty queue object | PASS | {"items": [], "count": 0} | {"items": [], "count": 0} |

## Rerun

```bash
python reference/smoke/run_reference_smoke.py --target all --report /home/xu/project/exap/ExAP/reference/smoke/reports/reference-smoke-report.md
```
