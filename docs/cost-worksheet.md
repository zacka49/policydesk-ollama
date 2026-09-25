# Zero-spend policy

The portfolio author has set a hard requirement of **£0 external-service spend**.

| Capability | Zero-cost implementation | Paid path status |
|---|---|---|
| Source hosting and review | Public GitHub repositories | No paid plan required |
| CI and release checks | Standard GitHub-hosted runners for a public repository | Larger paid runners forbidden |
| Application serving evidence | Ephemeral Docker container inside GitHub Actions and local Docker | No persistent public endpoint |
| Azure skills | Bicep reference design compiled in CI | Azure resource creation disabled |
| Model inference | Deterministic offline path plus local CPU model pilots | Hosted inference forbidden |
| Demonstration | README visuals, reports and reproducible local walkthrough | No paid demo platform |
| Human feedback | Public GitHub issue form | No paid research panel |

The repository stores no Azure credentials and has no executable Azure deployment
workflow. The example workflow lives under `docs/reference`, where GitHub cannot dispatch
it. Azure templates remain useful code-review evidence and are compiled during CI.

This is stronger than relying on a cloud budget: Microsoft documents that Azure budget
alerts do not stop resources or consumption. If a future employer provides a controlled
sandbox, any deployment becomes a separate employer-funded exercise with a new approval.

GitHub's terms and pricing can change. The public-repository Actions entitlement was
checked on 25 September 2026. If it stops being free, disable the workflows and run the
same Docker and test commands locally.
