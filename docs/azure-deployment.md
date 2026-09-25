# Zero-cost cloud and release evidence

PolicyDesk follows a strict **£0 external-services policy**. It does not provision Azure,
hosted inference, a paid registry, a database or any other metered cloud resource.

## Evidence that runs for free

The public repository uses standard GitHub-hosted Linux runners. GitHub documents that
standard Actions usage is free for public repositories. The workflows retain no build
artifacts or container images:

1. CI installs the project, runs Ruff and pytest, executes the frozen evaluation, compiles
   both Azure Bicep templates and builds the Docker image.
2. `Zero-cost deployment evidence` builds an immutable commit-tagged image, starts it in
   an ephemeral local container, and tests liveness, readiness, an authorised decision and
   cross-customer denial over a real HTTP socket.
3. The job summary records the commit and checks. The container and runner disappear at
   job completion.

This demonstrates packaging, automated release gates, health checks and access-boundary
smoke testing. It is not evidence of public hosting, production uptime, traffic, Azure
operations or customer use.

## Azure reference design

The repository retains Bicep for Container Apps, Azure Container Registry, managed
identity and Log Analytics. CI compiles it so syntax and module wiring cannot silently
rot. The former deployment workflow is retained as
[`docs/reference/deploy-azure.example.yml`](reference/deploy-azure.example.yml), outside
`.github/workflows`, so it cannot provision anything.

The reference design shows OIDC authentication, least-scope resource-group deployment,
immutable image tags, managed registry pull identity, revision capture and endpoint smoke
tests. The matching release record is under
[`docs/reference/azure-release-evidence-template.md`](reference/azure-release-evidence-template.md).
Both files are design evidence only.

## Why Azure is deliberately not run

Azure Cost Management budgets notify; they do not stop resource consumption. A free grant
or trial can also vary by account, region and previous usage. That cannot satisfy a strict
zero-spend requirement, so the portfolio makes no Azure deployment claim and requires no
Azure sign-in.

If an employer supplies a sandbox subscription later, the reference design can be
reviewed and adapted under that organisation's controls. That is outside this portfolio's
£0 evidence boundary.
