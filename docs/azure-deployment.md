# Controlled Azure deployment

The repository contains an unexecuted deployment path for Azure Container Apps. It uses GitHub OIDC, Azure Container Registry, a managed identity with `AcrPull`, Log Analytics, immutable commit-tagged images, multiple revisions and scale-to-zero.

No deployment result is claimed until the workflow has run, the endpoint has been tested, and the resulting revision/run links are recorded.

## Before the first run

1. Use the [cost worksheet](cost-worksheet.md) to check live prices, quotas and log retention for the selected subscription and region.
2. Create an Entra application or user-assigned identity with a federated credential restricted to this repository and the `azure-demo` GitHub environment. Grant only the resource-group permissions required by the templates and ACR build.
3. Configure the `azure-demo` environment with required reviewers. Add `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, and `AZURE_RESOURCE_GROUP` as environment variables.
4. Replace the fixture-token boundary with validated identity-provider claims before connecting real data. This deployment contains synthetic data only.
5. Run **Deploy controlled Azure demo** manually. Manual dispatch and environment review are intentional cost controls.

## Release and rollback

The workflow tests the commit, runs the deterministic release evaluation, builds in ACR, and deploys a candidate revision. Record its workflow URL, commit, revision, evaluation artifact and observed cost in a release evidence document.

For a rollback drill, list revisions and move all traffic to the last known compatible revision. Verify that its corpus, rules and schema remain compatible; an image rollback alone does not restore external state.

```powershell
az containerapp revision list --resource-group <group> --name <prefix>-api --output table
az containerapp ingress traffic set --resource-group <group> --name <prefix>-api --revision-weight <known-good>=100
```

Label deliberately injected failures as drills. Do not describe synthetic traffic as customer traffic or infer an availability SLA from a short run.

## Teardown

The templates are designed for a dedicated resource group. After preserving the deployment evidence, delete the explicitly named demo group through Azure Portal or the CLI and verify that billing resources are gone. Never substitute a shared resource group in the deletion command.
