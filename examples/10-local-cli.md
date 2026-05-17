# Local CLI Example

## Start provider

```bash
exapd --config exapd.toml
```

## Discover capabilities

```bash
exapctl discover --provider http://127.0.0.1:8765/exap
```

## Create contract

```bash
exapctl contract create examples/01-process-wait-contract.json
```

## Wait without polling

```bash
exapctl wait act_process_wait_001 --until attention,completed,expired --timeout P1D
```

## Acknowledge and revoke

```bash
exapctl ack attn_gpu_idle_001 --action seen
exapctl contract revoke act_process_wait_001 --reason task_completed
```
