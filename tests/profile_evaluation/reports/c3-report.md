# ExAP C3 Profile Evaluation Report

Generated: 2026-05-17T17:28:21.993891+00:00
Level: C3
Git commit: `c5087c6`
ExAP version: `0.2.0-draft`
Fixtures: `/home/xu/project/exap/ExAP/tests/fixtures/profile-transcripts`
Summary: 6/6 transcripts PASS; coverage PASS

| Transcript | Status | Step count |
|---|---:|---:|
| C3-DL-00 `tests/fixtures/profile-transcripts/deep-learning-training/00_gpu_idle_positive.json` | PASS | 13 |
| C3-DL-01 `tests/fixtures/profile-transcripts/deep-learning-training/01_cuda_oom_positive.json` | PASS | 13 |
| C3-DL-02 `tests/fixtures/profile-transcripts/deep-learning-training/02_capability_mismatch_negative.json` | PASS | 6 |
| C3-MAIL-00 `tests/fixtures/profile-transcripts/email-priority/00_important_sender_positive.json` | PASS | 13 |
| C3-MAIL-01 `tests/fixtures/profile-transcripts/email-priority/01_semantic_match_positive.json` | PASS | 13 |
| C3-MAIL-02 `tests/fixtures/profile-transcripts/email-priority/02_capability_mismatch_negative.json` | PASS | 6 |

## Coverage

| Mechanism | Status |
|---|---:|
| capability_mismatch | PASS |
| cooldown | PASS |
| debounce | PASS |
| dedupe_suppression | PASS |
| delivery_report_output | PASS |
| event_condition | PASS |
| evidence_policy_output | PASS |
| field_filter | PASS |
| hysteresis | PASS |
| semantic_match | PASS |
| signal_condition | PASS |

## Transcript Details

### C3-DL-00. deep-learning GPU idle positive

Path: `tests/fixtures/profile-transcripts/deep-learning-training/00_gpu_idle_positive.json`
Status: PASS
Coverage: cooldown, debounce, dedupe_suppression, delivery_report_output, event_condition, evidence_policy_output, field_filter, hysteresis, signal_condition

| Check | Status | Expected | Actual |
|---|---:|---|---|
| fixture schema-valid | PASS | no fixture schema errors |  |
| profile required params resolved | PASS | all required params/defaults present |  |
| profile parameter bindings applied | PASS | bound paths equal params/defaults |  |
| expected coverage is derived from contract/transcript/output | PASS | declared mechanisms have evidence |  |
| effective contract schema-valid | PASS | no schema errors |  |
| effective contract semantic-valid | PASS | no semantic errors |  |
| effective contract capability-compatible | PASS | no compatibility errors |  |
| expected Attention Events schema-valid | PASS | non-empty schema-valid events |  |
| suppressed/internal events are machine-assertable | PASS | reason and dedupe_key present | [{"reason": "cooldown_window", "dedupe_key": "act_process_wait_001:rule_gpu_idle", "window": "PT10M", "count": 1}] |
| state transitions are machine-assertable | PASS | contract_id/from/to/action present | [{"contract_id": "act_process_wait_001", "from": "active", "to": "active", "action": "rule_evaluated", "rule_state": "matched"}] |
| delivery reports are machine-assertable | PASS | mode/transport/success present | [{"contract_id": "act_process_wait_001", "attention_id": "attn_gpu_idle_001", "mode": "blocking_wait", "transport": "mcp", "attempt": 1, "success": true}] |
| expected outputs align with input transcript | PASS | event/evidence/payload values come from transcript |  |
| input transcript is ordered | PASS | monotonic step order | [0, 1, 2, 3] |

### C3-DL-01. deep-learning CUDA OOM positive

Path: `tests/fixtures/profile-transcripts/deep-learning-training/01_cuda_oom_positive.json`
Status: PASS
Coverage: cooldown, debounce, dedupe_suppression, delivery_report_output, event_condition, evidence_policy_output, field_filter, hysteresis, signal_condition

| Check | Status | Expected | Actual |
|---|---:|---|---|
| fixture schema-valid | PASS | no fixture schema errors |  |
| profile required params resolved | PASS | all required params/defaults present |  |
| profile parameter bindings applied | PASS | bound paths equal params/defaults |  |
| expected coverage is derived from contract/transcript/output | PASS | declared mechanisms have evidence |  |
| effective contract schema-valid | PASS | no schema errors |  |
| effective contract semantic-valid | PASS | no semantic errors |  |
| effective contract capability-compatible | PASS | no compatibility errors |  |
| expected Attention Events schema-valid | PASS | non-empty schema-valid events |  |
| suppressed/internal events are machine-assertable | PASS | reason and dedupe_key present | [{"reason": "cooldown_window", "dedupe_key": "act_process_wait_001:rule_cuda_oom", "window": "PT10M", "count": 1}] |
| state transitions are machine-assertable | PASS | contract_id/from/to/action present | [{"contract_id": "act_process_wait_001", "from": "active", "to": "active", "action": "rule_evaluated", "rule_state": "matched"}] |
| delivery reports are machine-assertable | PASS | mode/transport/success present | [{"contract_id": "act_process_wait_001", "attention_id": "attn_cuda_oom_001", "mode": "blocking_wait", "transport": "mcp", "attempt": 1, "success": true}] |
| expected outputs align with input transcript | PASS | event/evidence/payload values come from transcript |  |
| input transcript is ordered | PASS | monotonic step order | [0, 1, 2, 3] |

### C3-DL-02. deep-learning capability mismatch negative

Path: `tests/fixtures/profile-transcripts/deep-learning-training/02_capability_mismatch_negative.json`
Status: PASS
Coverage: capability_mismatch, cooldown, debounce, event_condition, field_filter, hysteresis, signal_condition

| Check | Status | Expected | Actual |
|---|---:|---|---|
| fixture schema-valid | PASS | no fixture schema errors |  |
| profile required params resolved | PASS | all required params/defaults present |  |
| profile parameter bindings applied | PASS | bound paths equal params/defaults |  |
| expected coverage is derived from contract/transcript/output | PASS | declared mechanisms have evidence |  |
| capability mismatch is detected | PASS | compatibility errors present | scope subject type not in capability process; scope subject type not in capability gpu; scope signal not in capability process.status; scope signal not in capability process.exit_code; scope signal not in capability process.cpu.percent; scope signal not in capability process.memory.rss_mb; scope signal not in capability gpu.util.percent; scope signal not in capability gpu.memory.used_mb; scope signal not in capability log.line; scope signal not in capability disk.free_gb; scope event not in capability process.exited; scope event not in capability log.line.appended; scope event not in capability file.created; rule rule_process_exited event not in capability process.exited; rule rule_gpu_idle signal not in capability gpu.util.percent; rule rule_gpu_idle signal not in capability process.status; rule rule_gpu_idle operator not in capability lt; rule rule_gpu_idle aggregate not in capability  |
| negative transcript emits no attention event | PASS | no expected attention events | 0 |

### C3-MAIL-00. email important sender positive

Path: `tests/fixtures/profile-transcripts/email-priority/00_important_sender_positive.json`
Status: PASS
Coverage: cooldown, debounce, dedupe_suppression, delivery_report_output, event_condition, evidence_policy_output, field_filter, semantic_match, signal_condition

| Check | Status | Expected | Actual |
|---|---:|---|---|
| fixture schema-valid | PASS | no fixture schema errors |  |
| profile required params resolved | PASS | all required params/defaults present |  |
| profile parameter bindings applied | PASS | bound paths equal params/defaults |  |
| expected coverage is derived from contract/transcript/output | PASS | declared mechanisms have evidence |  |
| effective contract schema-valid | PASS | no schema errors |  |
| effective contract semantic-valid | PASS | no semantic errors |  |
| effective contract capability-compatible | PASS | no compatibility errors |  |
| expected Attention Events schema-valid | PASS | non-empty schema-valid events |  |
| suppressed/internal events are machine-assertable | PASS | reason and dedupe_key present | [{"reason": "cooldown_window", "dedupe_key": "act_email_priority_001:thr_8291", "window": "PT10M", "count": 1}] |
| state transitions are machine-assertable | PASS | contract_id/from/to/action present | [{"contract_id": "act_email_priority_001", "from": "active", "to": "active", "action": "rule_evaluated", "rule_state": "matched"}] |
| delivery reports are machine-assertable | PASS | mode/transport/success present | [{"contract_id": "act_email_priority_001", "attention_id": "attn_mail_urgent_001", "mode": "blocking_wait", "transport": "http_webhook", "attempt": 1, "success": true}] |
| expected outputs align with input transcript | PASS | event/evidence/payload values come from transcript |  |
| input transcript is ordered | PASS | monotonic step order | [0, 1, 2, 3] |

### C3-MAIL-01. email semantic match positive

Path: `tests/fixtures/profile-transcripts/email-priority/01_semantic_match_positive.json`
Status: PASS
Coverage: cooldown, debounce, dedupe_suppression, delivery_report_output, event_condition, evidence_policy_output, field_filter, semantic_match, signal_condition

| Check | Status | Expected | Actual |
|---|---:|---|---|
| fixture schema-valid | PASS | no fixture schema errors |  |
| profile required params resolved | PASS | all required params/defaults present |  |
| profile parameter bindings applied | PASS | bound paths equal params/defaults |  |
| expected coverage is derived from contract/transcript/output | PASS | declared mechanisms have evidence |  |
| effective contract schema-valid | PASS | no schema errors |  |
| effective contract semantic-valid | PASS | no semantic errors |  |
| effective contract capability-compatible | PASS | no compatibility errors |  |
| expected Attention Events schema-valid | PASS | non-empty schema-valid events |  |
| suppressed/internal events are machine-assertable | PASS | reason and dedupe_key present | [{"reason": "cooldown_window", "dedupe_key": "act_email_priority_001:semantic:approval_needed", "window": "PT10M", "count": 1}] |
| state transitions are machine-assertable | PASS | contract_id/from/to/action present | [{"contract_id": "act_email_priority_001", "from": "active", "to": "active", "action": "rule_evaluated", "rule_state": "matched"}] |
| delivery reports are machine-assertable | PASS | mode/transport/success present | [{"contract_id": "act_email_priority_001", "attention_id": "attn_mail_semantic_001", "mode": "blocking_wait", "transport": "http_webhook", "attempt": 1, "success": true}] |
| expected outputs align with input transcript | PASS | event/evidence/payload values come from transcript |  |
| input transcript is ordered | PASS | monotonic step order | [0, 1, 2] |

### C3-MAIL-02. email capability mismatch negative

Path: `tests/fixtures/profile-transcripts/email-priority/02_capability_mismatch_negative.json`
Status: PASS
Coverage: capability_mismatch, cooldown, debounce, event_condition, signal_condition

| Check | Status | Expected | Actual |
|---|---:|---|---|
| fixture schema-valid | PASS | no fixture schema errors |  |
| profile required params resolved | PASS | all required params/defaults present |  |
| profile parameter bindings applied | PASS | bound paths equal params/defaults |  |
| expected coverage is derived from contract/transcript/output | PASS | declared mechanisms have evidence |  |
| capability mismatch is detected | PASS | compatibility errors present | scope subject type not in capability mailbox; scope signal not in capability mail.sender.relationship; scope signal not in capability mail.content.semantic_intent; scope signal not in capability mail.has_attachment; scope event not in capability mail.message.received; rule rule_urgent_work_email signal not in capability mail.content.semantic_intent; rule rule_urgent_work_email signal not in capability mail.sender.relationship; rule rule_urgent_work_email event not in capability mail.message.received |
| negative transcript emits no attention event | PASS | no expected attention events | 0 |

## Rerun

```bash
python tests/profile_evaluation/run_c3.py --fixtures tests/fixtures/profile-transcripts --report /home/xu/project/exap/ExAP/tests/profile_evaluation/reports/c3-report.md
```
