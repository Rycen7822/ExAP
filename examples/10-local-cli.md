# Local CLI Example

## Start provider

```bash
eapd --config eapd.toml
```

## Discover capabilities

```bash
eapctl discover --provider http://127.0.0.1:8765/eap
```

## Create contract

```bash
eapctl contract create examples/01-process-wait-contract.json
```

## Wait without polling

```bash
eapctl wait act_process_wait_001 --until attention,completed,expired --timeout P1D
```

## Acknowledge and revoke

```bash
eapctl ack attn_gpu_idle_001 --action seen
eapctl contract revoke act_process_wait_001 --reason task_completed
```
