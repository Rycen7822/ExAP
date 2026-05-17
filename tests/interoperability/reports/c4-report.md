# ExAP C4 Interoperability Report

Generated: 2026-05-17T17:28:22.043100+00:00
Level: C4
Git commit: `c5087c6`
ExAP version: `0.2.0-draft`
Scenarios: `/home/xu/project/exap/ExAP/tests/interoperability/scenarios`
Binding matrix: http+a2a, http+mcp, http+mcp+a2a, http+mcp+local
Summary: 4/4 scenarios PASS; comparator guard PASS

| Scenario | Bindings | Status | Check count |
|---|---|---:|---:|
| C4-00 HTTP + MCP + Local process wait equivalence | http+mcp+local | PASS | 15 |
| C4-01 HTTP + A2A email priority equivalence | http+a2a | PASS | 14 |
| C4-02 HTTP SSE + MCP progress stream recovery equivalence | http+mcp | PASS | 13 |
| C4-03 HTTP + MCP + A2A cross-binding error mapping | http+mcp+a2a | PASS | 11 |

## Details

### C4-00. HTTP + MCP + Local process wait equivalence

Path: `tests/interoperability/scenarios/00_http_mcp_process_wait.json`
Bindings: http, mcp, local
Status: PASS

| Check | Status | Expected | Actual |
|---|---:|---|---|
| version equivalent | PASS | present and equivalent | ["'0.2.0-draft'", "'0.2.0-draft'", "'0.2.0-draft'"] |
| profile equivalent | PASS | present and equivalent | ["'deep-learning-training'", "'deep-learning-training'", "'deep-learning-training'"] |
| delivery_mode equivalent | PASS | present and equivalent | ["'wait'", "'wait'", "'wait'"] |
| content_mode equivalent | PASS | present and equivalent | ["'structured'", "'structured'", "'structured'"] |
| contract_id equivalent | PASS | present and equivalent | ["'act_process_wait_001'", "'act_process_wait_001'", "'act_process_wait_001'"] |
| attention_id equivalent | PASS | present and equivalent | ["'attn_gpu_idle_001'", "'attn_gpu_idle_001'", "'attn_gpu_idle_001'"] |
| return_reason equivalent | PASS | present and equivalent | ["'attention'", "'attention'", "'attention'"] |
| event.type equivalent | PASS | present and equivalent | ["'exap.attention.triggered'", "'exap.attention.triggered'", "'exap.attention.triggered'"] |
| event.status equivalent | PASS | present and equivalent | ["'triggered'", "'triggered'", "'triggered'"] |
| event.rule_id equivalent | PASS | present and equivalent | ["'rule_gpu_idle'", "'rule_gpu_idle'", "'rule_gpu_idle'"] |
| event.evidence_count equivalent | PASS | present and equivalent | ['2', '2', '2'] |
| ack_status equivalent | PASS | present and equivalent | ["'acknowledged'", "'acknowledged'", "'acknowledged'"] |
| http request transcript present | PASS | non-empty requests | 4 |
| mcp request transcript present | PASS | non-empty requests | 4 |
| local request transcript present | PASS | non-empty requests | 3 |

#### Normalized transcripts

- `http`: `{"ack_status": "acknowledged", "attention_id": "attn_gpu_idle_001", "binding": "http", "content_mode": "structured", "contract_id": "act_process_wait_001", "delivery_mode": "wait", "errors": [], "event": {"attention_id": "attn_gpu_idle_001", "evidence_count": 2, "payload_keys": ["summary"], "rule_id": "rule_gpu_idle", "status": "triggered", "type": "exap.attention.triggered"}, "profile": "deep-learning-training", "return_reason": "attention", "state_transitions": [{"action": "create", "contract_id": "act_process_wait_001", "from": null, "to": "active"}], "status": "active", "transport": "http_webhook", "version": "0.2.0-draft"}`
- `mcp`: `{"ack_status": "acknowledged", "attention_id": "attn_gpu_idle_001", "binding": "mcp", "content_mode": "structured", "contract_id": "act_process_wait_001", "delivery_mode": "wait", "errors": [], "event": {"attention_id": "attn_gpu_idle_001", "evidence_count": 2, "payload_keys": ["summary"], "rule_id": "rule_gpu_idle", "status": "triggered", "type": "exap.attention.triggered"}, "profile": "deep-learning-training", "return_reason": "attention", "state_transitions": [{"action": "create", "contract_id": "act_process_wait_001", "from": null, "to": "active"}], "status": "active", "transport": "mcp", "version": "0.2.0-draft"}`
- `local`: `{"ack_status": "acknowledged", "attention_id": "attn_gpu_idle_001", "binding": "local", "content_mode": "structured", "contract_id": "act_process_wait_001", "delivery_mode": "wait", "errors": [], "event": {"attention_id": "attn_gpu_idle_001", "evidence_count": 2, "payload_keys": ["summary"], "rule_id": "rule_gpu_idle", "status": "triggered", "type": "exap.attention.triggered"}, "profile": "deep-learning-training", "return_reason": "attention", "state_transitions": [{"action": "create", "contract_id": "act_process_wait_001", "from": null, "to": "active"}], "transport": "local_stdio", "version": "0.2.0-draft"}`

### C4-01. HTTP + A2A email priority equivalence

Path: `tests/interoperability/scenarios/01_http_a2a_email_priority.json`
Bindings: http, a2a
Status: PASS

| Check | Status | Expected | Actual |
|---|---:|---|---|
| version equivalent | PASS | present and equivalent | ["'0.2.0-draft'", "'0.2.0-draft'"] |
| profile equivalent | PASS | present and equivalent | ["'email-priority'", "'email-priority'"] |
| delivery_mode equivalent | PASS | present and equivalent | ["'wait'", "'wait'"] |
| content_mode equivalent | PASS | present and equivalent | ["'structured'", "'structured'"] |
| draft_status equivalent | PASS | present and equivalent | ["'draft'", "'draft'"] |
| contract_id equivalent | PASS | present and equivalent | ["'act_email_priority_001'", "'act_email_priority_001'"] |
| attention_id equivalent | PASS | present and equivalent | ["'attn_mail_urgent_001'", "'attn_mail_urgent_001'"] |
| return_reason equivalent | PASS | present and equivalent | ["'attention'", "'attention'"] |
| event.type equivalent | PASS | present and equivalent | ["'exap.attention.triggered'", "'exap.attention.triggered'"] |
| event.status equivalent | PASS | present and equivalent | ["'triggered'", "'triggered'"] |
| event.rule_id equivalent | PASS | present and equivalent | ["'rule_urgent_work_email'", "'rule_urgent_work_email'"] |
| event.evidence_count equivalent | PASS | present and equivalent | ['2', '2'] |
| http request transcript present | PASS | non-empty requests | 3 |
| a2a request transcript present | PASS | non-empty requests | 3 |

#### Normalized transcripts

- `http`: `{"attention_id": "attn_mail_urgent_001", "binding": "http", "content_mode": "structured", "contract_id": "act_email_priority_001", "delivery_mode": "wait", "errors": [], "event": {"attention_id": "attn_mail_urgent_001", "evidence_count": 2, "payload_keys": ["email"], "rule_id": "rule_urgent_work_email", "status": "triggered", "type": "exap.attention.triggered"}, "profile": "email-priority", "return_reason": "attention", "state_transitions": [{"action": "create", "contract_id": "act_email_priority_001", "from": null, "to": "active"}], "transport": "http_webhook", "version": "0.2.0-draft"}`
- `a2a`: `{"attention_id": "attn_mail_urgent_001", "binding": "a2a", "content_mode": "structured", "contract_id": "act_email_priority_001", "delivery_mode": "wait", "errors": [], "event": {"attention_id": "attn_mail_urgent_001", "evidence_count": 2, "payload_keys": ["email"], "rule_id": "rule_urgent_work_email", "status": "triggered", "type": "exap.attention.triggered"}, "profile": "email-priority", "return_reason": "attention", "state_transitions": [{"action": "create", "contract_id": "act_email_priority_001", "from": null, "to": "active"}], "transport": "a2a", "version": "0.2.0-draft"}`

### C4-02. HTTP SSE + MCP progress stream recovery equivalence

Path: `tests/interoperability/scenarios/02_stream_push_recovery.json`
Bindings: http, mcp
Status: PASS

| Check | Status | Expected | Actual |
|---|---:|---|---|
| version equivalent | PASS | present and equivalent | ["'0.2.0-draft'", "'0.2.0-draft'"] |
| profile equivalent | PASS | present and equivalent | ["'deep-learning-training'", "'deep-learning-training'"] |
| delivery_mode equivalent | PASS | present and equivalent | ["'stream'", "'stream'"] |
| content_mode equivalent | PASS | present and equivalent | ["'structured'", "'structured'"] |
| contract_id equivalent | PASS | present and equivalent | ["'act_process_wait_001'", "'act_process_wait_001'"] |
| attention_id equivalent | PASS | present and equivalent | ["'attn_gpu_idle_001'", "'attn_gpu_idle_001'"] |
| stream_id equivalent | PASS | present and equivalent | ["'stream_act_process_wait_001'", "'stream_act_process_wait_001'"] |
| frame_types equivalent | PASS | present and equivalent | ["['keepalive', 'event', 'error']", "['keepalive', 'event', 'error']"] |
| event.type equivalent | PASS | present and equivalent | ["'exap.attention.triggered'", "'exap.attention.triggered'"] |
| event.status equivalent | PASS | present and equivalent | ["'triggered'", "'triggered'"] |
| push_success equivalent | PASS | present and equivalent | ['True', 'True'] |
| http request transcript present | PASS | non-empty requests | 3 |
| mcp request transcript present | PASS | non-empty requests | 3 |

#### Normalized transcripts

- `http`: `{"attention_id": "attn_gpu_idle_001", "binding": "http", "content_mode": "structured", "contract_id": "act_process_wait_001", "delivery_mode": "stream", "errors": [], "event": {"attention_id": "attn_gpu_idle_001", "evidence_count": 2, "payload_keys": ["summary"], "rule_id": "rule_gpu_idle", "status": "triggered", "type": "exap.attention.triggered"}, "frame_types": ["keepalive", "event", "error"], "profile": "deep-learning-training", "push_success": true, "state_transitions": [{"action": "create", "contract_id": "act_process_wait_001", "from": null, "to": "active"}], "stream_id": "stream_act_process_wait_001", "transport": "sse", "version": "0.2.0-draft"}`
- `mcp`: `{"attention_id": "attn_gpu_idle_001", "binding": "mcp", "content_mode": "structured", "contract_id": "act_process_wait_001", "delivery_mode": "stream", "errors": [], "event": {"attention_id": "attn_gpu_idle_001", "evidence_count": 2, "payload_keys": ["summary"], "rule_id": "rule_gpu_idle", "status": "triggered", "type": "exap.attention.triggered"}, "frame_types": ["keepalive", "event", "error"], "profile": "deep-learning-training", "push_success": true, "state_transitions": [{"action": "create", "contract_id": "act_process_wait_001", "from": null, "to": "active"}], "stream_id": "stream_act_process_wait_001", "transport": "mcp", "version": "0.2.0-draft"}`

### C4-03. HTTP + MCP + A2A cross-binding error mapping

Path: `tests/interoperability/scenarios/03_error_mapping_cross_binding.json`
Bindings: http, mcp, a2a
Status: PASS

| Check | Status | Expected | Actual |
|---|---:|---|---|
| version equivalent | PASS | present and equivalent | ["'0.2.0-draft'", "'0.2.0-draft'", "'0.2.0-draft'"] |
| profile equivalent | PASS | present and equivalent | ["'deep-learning-training'", "'deep-learning-training'", "'deep-learning-training'"] |
| delivery_mode equivalent | PASS | present and equivalent | ["'error'", "'error'", "'error'"] |
| content_mode equivalent | PASS | present and equivalent | ["'structured'", "'structured'", "'structured'"] |
| errors.code equivalent | PASS | present and equivalent | ['[-32004, -32602]', '[-32004, -32602]', '[-32004, -32602]'] |
| errors.exap_code equivalent | PASS | present and equivalent | ["['ExAP-4040', 'ExAP-4006']", "['ExAP-4040', 'ExAP-4006']", "['ExAP-4040', 'ExAP-4006']"] |
| errors.field equivalent | PASS | present and equivalent | ["['params.contract_id', 'params.contract']", "['params.contract_id', 'params.contract']", "['params.contract_id', 'params.contract']"] |
| errors.retryable equivalent | PASS | present and equivalent | ['[False, False]', '[False, False]', '[False, False]'] |
| http request transcript present | PASS | non-empty requests | 2 |
| mcp request transcript present | PASS | non-empty requests | 2 |
| a2a request transcript present | PASS | non-empty requests | 2 |

#### Normalized transcripts

- `http`: `{"binding": "http", "content_mode": "structured", "delivery_mode": "error", "errors": [{"code": -32004, "exap_code": "ExAP-4040", "field": "params.contract_id", "retryable": false}, {"code": -32602, "exap_code": "ExAP-4006", "field": "params.contract", "retryable": false}], "profile": "deep-learning-training", "state_transitions": [], "transport": "http_webhook", "version": "0.2.0-draft"}`
- `mcp`: `{"binding": "mcp", "content_mode": "structured", "delivery_mode": "error", "errors": [{"code": -32004, "exap_code": "ExAP-4040", "field": "params.contract_id", "retryable": false}, {"code": -32602, "exap_code": "ExAP-4006", "field": "params.contract", "retryable": false}], "profile": "deep-learning-training", "state_transitions": [], "transport": "mcp", "version": "0.2.0-draft"}`
- `a2a`: `{"binding": "a2a", "content_mode": "structured", "delivery_mode": "error", "errors": [{"code": -32004, "exap_code": "ExAP-4040", "field": "params.contract_id", "retryable": false}, {"code": -32602, "exap_code": "ExAP-4006", "field": "params.contract", "retryable": false}], "profile": "deep-learning-training", "state_transitions": [], "transport": "a2a", "version": "0.2.0-draft"}`

## Rerun

```bash
python tests/interoperability/run_c4.py --scenarios tests/interoperability/scenarios --report /home/xu/project/exap/ExAP/tests/interoperability/reports/c4-report.md
```
