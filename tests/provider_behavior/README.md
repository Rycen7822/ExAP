# ExAP C2 Provider Behavior Suite

This suite runs black-box lifecycle behavior checks against a provider adapter.

Current adapters:

- `tests.provider_behavior.fake_provider:FakeProviderAdapter`
- `reference.exapd.provider:ReferenceProviderAdapter`

Run:

```bash
python tests/provider_behavior/run_c2.py --adapter tests.provider_behavior.fake_provider:FakeProviderAdapter --report tests/provider_behavior/reports/c2-report.md
python tests/provider_behavior/run_c2.py --adapter reference.exapd.provider:ReferenceProviderAdapter --report tests/provider_behavior/reports/c2-reference-report.md
```
