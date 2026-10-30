---
name: python-release
description: "Release tested, reviewed Python projects to Google Cloud: use for GKE Kubernetes workloads or Cloud Run functions deployed with the Cloud Run API, with repository discovery, credential-free quality gates, Secret Manager IAM validation, human-approved deployment, smoke tests, and scoped rollback. Do NOT use for AWS, Azure, Terraform provisioning, arbitrary scripts, functions created or managed through the Cloud Functions v2 API (`gcloud functions deploy`), or releases that include database migrations."
---

# Python Release (GCP-only)

**Contract:** Release an existing, reviewed Python application to GKE or Cloud Run functions. Never provision a GCP project/cluster, rotate credentials, make a service public, mutate database schema, or deploy to an unapproved destination. Do not assume the presence of credentials. Release operations are side effects: a matching human approval is **mandatory** before any build/push/deploy/traffic or infrastructure mutation, even in staging. Functions owned by the Cloud Functions v2 API are out of scope: detect them in Discovery and STOP; never redeploy them through `gcloud run deploy` or switch their managing API.

**Bundled files:** This skill depends on the scripts, references, and templates listed in section 5, resolved relative to this skill's directory. If any referenced file is missing, STOP and report which one; do not improvise a substitute.

## 1. Discovery: identify code and target before any action

1. **Load the release config.** Read the committed `deploy/release.<environment>.yaml` (schema: `templates/release-config.example.yaml`) **from the candidate commit** with `git show <SHA>:deploy/release.<environment>.yaml`, not from the working tree. It is the source of truth for project, region, target, resource identity, release branch, runtime and deploy identities, source/entrypoint/base image or image repository/cluster/namespace/Deployment/container, ingress and invoker model, health check, limits/scaling, secrets-map path, and rollback notes. Validate it, then ask the human **only for missing fields**. Mark any value supplied in chat as `operator-supplied` in the Preview Plan and recommend committing it. **Never invent values.** If no config file exists, ask for all fields once, then offer a filled-in config file for the user to review and commit.
2. Read `AGENTS.md`, `CLAUDE.md`, Git branch/status/commit, `pyproject.toml`, `uv.lock`, `requirements*.txt`, `Dockerfile`, `main.py`, `src/`, `tests/`, `.github/workflows/`, `deploy/`, Kubernetes manifests and infrastructure configuration. **Do not execute repository scripts during discovery.**
3. **Verify that the commit was reviewed.** Resolve the candidate to a full 40-character SHA. Run `git fetch origin <release_branch>`, then `git merge-base --is-ancestor <SHA> origin/<release_branch>`. If the SHA is not reachable from the release branch, STOP: unmerged or local-only commits are never released. Check branch protection (required reviews) with `gh api repos/{owner}/{repo}/branches/<release_branch>/protection` when available. If protection cannot be confirmed, show it as an unverified risk in the Preview Plan.
4. **Establish the baseline**, meaning the commit currently running in the target. Read it from the deployed image tag/label or revision annotation. If it cannot be determined, use the SHA's first parent on the release branch and say so in the plan.
5. **Database migrations:** list files changed between baseline and SHA (`git diff --name-only <baseline> <SHA>`). If any are migrations (for example `alembic/versions/`, `*/migrations/*.py`, `*.sql` under migration or schema directories, or new `op.`/`migrations.` operations), or the baseline is unknown and migration directories exist, **STOP and hand off** to a human-owned migration process. Do not deploy app code that depends on an unapplied schema change.
6. Run `python3 scripts/inspect_project.py <repo>` from this skill directory (read-only `ast`, `tomllib`, file inspection). Record package/runtime and whether the app uses FastAPI/Flask/Django/Uvicorn, `functions_framework`, HTTP/CloudEvent functions, async workers, or a batch script; flag ambiguity.
7. Confirm a unique deployment target: `gke` (container/workload) **or** `cloud-run-function` (HTTP/event handler), and environment `dev|staging|production`. If the architecture cannot support that target, STOP and explain. Plain batch jobs and arbitrary Python scripts are not automatically valid HTTP functions or GKE services.
8. **Cloud Functions v2 ownership (cloud-run-function only):** if `gcloud functions describe <name> --gen2 --region <region>` finds the resource, it is managed by the Cloud Functions v2 API. STOP: this skill does not release it.

## 2. Host prerequisites, identity and access (read-only)

From the approved operator/CI executor, run `bash scripts/preflight.sh <target>` with explicit environment variables (see script). Verify `python3`, `git`, `gcloud`, `curl`; plus `docker`, `kubectl`, `gke-gcloud-auth-plugin` for GKE; Git SHA, reviewed-commit reachability, and a clean release checkout whose `HEAD` equals the candidate SHA. Check CLI versions, expected GCP project, ability to obtain a GCP access token **without printing it**, read permissions for the target, registry/namespace, and GKE RBAC via `kubectl auth can-i` when relevant.

- **Allowed authentication:** short-lived Workload Identity Federation/OIDC in CI, or already authorized `gcloud auth` credentials. If `GOOGLE_APPLICATION_CREDENTIALS` is set, verify only that its credential configuration file exists and is private; do not require, generate, or display a service-account private key. ADC and `gcloud` authentication are distinct; a valid ADC file alone does not prove that `gcloud` can deploy.
- **CI deploy identity and runtime identity are separate.** Check effective role/access scope; IAM checks that cannot be verified cause a STOP, not a guessed grant. A readable IAM policy does not prove effective access in the presence of inherited/conditional policies.
- Never enable APIs, grant IAM, create clusters, configure billing, or relax ingress on your own. Private GKE control planes require an approved runner network path.

## 3. Secrets isolation (never read values)

1. Define mappings in `templates/secrets-map.example.json` format at the path named in the release config: environment-variable or file-mount name → `projects/PROJECT_ID/secrets/SECRET_NAME` + pinned numeric version; set target, environment, and expected runtime principal. **No secret values in the map.** Validate shape with `python3 scripts/check_secrets.py <map.json> --offline`.
2. Run `python3 scripts/check_secrets.py <map.json>` in authenticated preflight. It checks secret resource existence and the secret-level `roles/secretmanager.secretAccessor` IAM binding for the expected runtime principal. This is an explicit-binding baseline, not a complete effective-permission proof (policy inheritance/conditions and Kubernetes workload identity must be separately confirmed); fail closed on inability to inspect/confirm. **Never invoke `gcloud secrets versions access`.**
3. For Cloud Run functions inject only references: `--update-secrets="DATABASE_URL=my-db-secret:3"` (additive; avoids wiping unrelated bindings). `--set-secrets` replaces all secret bindings and requires explicit full-manifest approval. For GKE use Workload Identity Federation for GKE and the Secret Manager add-on/CSI `SecretProviderClass` file mounts; do not put credentials in Kubernetes Secret YAML, Deployment `env` `value:`, build args, or images. See `references/secrets.md`.
4. No `env`, `printenv`, `set -x`, secret value echoing, token dumps, Kubernetes Secret `data` output, unredacted traceback/log uploads, or `curl` verbose trace. Redact credential-like data from diagnostics; fail closed if redaction is uncertain.

## 4. Multi-phase release lifecycle (mandatory)

The human approves a release candidate whose quality gates have **already run** on the exact SHA. Order: Plan → Gates → Approve → Deploy → Verify → Rollback/Report.

**A — Plan (no mutation):** Complete Discovery (section 1), preflight (section 2), and secret validation (section 3). Determine deployment identity, immutable artifact target, intended infrastructure diff, scale/cost/network changes, all secret names and paths, prior image/revision, and rollback strategy.

**B — Credential-free quality gates (before approval):** Check out the candidate SHA in a disposable, isolated runner/container with no GCP production credentials, safe mounts and appropriately limited network. A virtualenv alone is not a sandbox. Never execute untrusted generated code on production or alongside deploy credentials. Use `uv sync --locked` where `uv.lock` exists, or an approved reproducible equivalent. Run Ruff lint + format check, mypy, pytest with statement and branch coverage, the project's own gate scripts, and relevant security/dependency scans.

- **Thresholds come from the project.** Use its configured settings (`[tool.mypy]`, `[tool.coverage.report] fail_under`, the project's coverage gate scripts, Ruff config, CI workflow). Only when the project configures **no** coverage threshold, use ≥85% statement coverage plus meaningful branch tests.
- **Block only on new failures compared with the baseline** (section 1.4). Run the same checks on the baseline in the same sandbox, or reuse its recorded CI results for that SHA. These **block** release:
  - a configured threshold the candidate misses;
  - lint or type errors not present at baseline;
  - test failures not present at baseline;
  - coverage below the baseline when no threshold is configured;
  - any gate that could not be run.

  Pre-existing failures that are unchanged are **reported as debt** in the Preview Plan, not fixed and not blocking. Never weaken or skip a check to pass.
- If the baseline cannot be checked out or run, every failure blocks.

**C — Preview and halt for human:** Emit a human-readable **Preview Plan** with:
- project, environment, target, source commit, baseline commit;
- reviewed-commit evidence (reachable from `origin/<release_branch>`, branch protection status);
- **gate results**: pass/fail per check, coverage numbers vs. threshold and baseline, new failures, and pre-existing debt;
- affected resources, scale and cost risk, authentication/ingress, and secret references only;
- `operator-supplied` config values, the rollback procedure, and unverified risks.

Do not show an approval keyword if any gate is blocking; report the blockers instead. Otherwise show the exact keyword:

```text
APPROVE <target> <environment> <full-40-character-Git-SHA>
```

Do not infer approval from a prompt to "deploy" or from test success. Wait for the exact keyword in an explicit human response, scoped to the current plan/commit. If the plan, target, commit, config, or resources change, rerun the affected phases and get a fresh approval. In CI use a protected GitHub Environment requiring reviewers and a matching approval input for the current SHA; never trigger deployment from an untrusted PR.

**D — Deploy:** Only with current approval. Confirm the checkout `HEAD` still equals the approved SHA and that it is still reachable from `origin/<release_branch>`.
- **GKE:** build an immutable Git-SHA-tagged image from the approved SHA, push to Artifact Registry, and deploy the pushed digest; scope updates to a single named Deployment and verify readiness.
- **Cloud Run functions:** `gcloud run deploy --source ... --function ... --base-image ... --no-allow-unauthenticated --update-secrets=...`. For existing services, capture the prior traffic state, deploy a tagged `--no-traffic` revision, then obtain a **separate** promotion approval (`PROMOTE <target> <environment> <full-40-character-Git-SHA>`) before shifting traffic. `--no-traffic` is rejected when creating a new service; a first deploy needs its own explicit approval in the plan.

**E — Verify:** Wait for rollout/revision Ready, inspect redacted startup/CrashLoop/permission/timeout diagnostics, and run an authenticated `curl` smoke test against the health check from the release config, with a bounded timeout and expected status. Do not invoke a state-changing event handler as a smoke test without a safe test event. Confirm resource limits, logs, and current traffic; a successful CLI exit alone is not success.

**F — Rollback or report:**
- **GKE:** restore only the previously captured image or reviewed Deployment revision.
- **Cloud Run:** restore the saved exact traffic allocation, not blindly `LATEST=100`.
- Never use `git reset --hard`, delete resources, reverse database migrations, or change other operators' deployments. If a safe rollback cannot be proved, STOP and escalate with explicit remediation commands. Record actual executed commands and success/failure; never claim checks were performed when they were unavailable.

## 5. Executable templates and commands

| Path | Purpose |
| --- | --- |
| `scripts/preview.py --target gke\|cloud-run-function --environment dev\|staging\|production --config RELEASE.yaml --secrets-map MAP.json --gates GATES.json` | Plain-text Preview Plan, including gate results, + exact approval keyword (omitted when gates block), without reading secret values. |
| `scripts/preflight.sh gke\|cloud-run-function` | Binary/auth/Git/reviewed-commit/target read-only check. |
| `scripts/inspect_project.py PATH` | AST/manifest classification, without imports/execution. |
| `scripts/check_secrets.py MAP.json [--offline]` | Validate mappings and per-secret IAM policy without reading values. |
| `scripts/approve.sh TARGET ENVIRONMENT SHA APPROVAL` | Exact-match keyword check (human identity/CI environment protections must also be enforced). |
| `scripts/smoke.sh URL EXPECTED_STATUS [AUDIENCE]` | Private authenticated HTTP smoke test (never logs token or response body). |
| `scripts/rollback_gke.sh FAILED_IMAGE PREVIOUS_IMAGE` | Guarded, target-scoped GKE image restoration; requires compatibility checks and verification. |
| `scripts/rollback_cloud_run.py SNAPSHOT ...` | Guarded restoration of a saved Cloud Run traffic allocation. |
| `references/gke.md` | Deployment/rollback commands for a reviewed target workload. |
| `references/cloud-run-functions.md` | Source deployment, revision verification, traffic restore commands. |
| `references/secrets.md` | Secret Manager injection patterns for both targets. |
| `templates/release-config.example.yaml` | Schema for the committed `deploy/release.<environment>.yaml`; identifiers and references only, never secret values. |
| `templates/release.yml` | GitHub Actions template; copy/adapt and configure required reviewers. No workflow is safe to run before project-specific configuration. |
| `templates/secrets-map.example.json` | Reference schema; substitute real secret names and principals only, never values. |

Example commands — only in project-specific approved CI, after gates and approval:

```bash
# Cloud Run function (existing service), preserving unrelated existing secret bindings.
# Withhold --allow-unauthenticated unless separately authorized.
gcloud run deploy "$FUNCTION_NAME" --project "$GCP_PROJECT_ID" --region "$GCP_REGION" \
  --source "$FUNCTION_SOURCE" --function "$FUNCTION_ENTRYPOINT" \
  --base-image "$FUNCTION_BASE_IMAGE" --service-account "$FUNCTION_RUNTIME_SERVICE_ACCOUNT" \
  --update-secrets="DATABASE_URL=${DATABASE_SECRET_NAME}:${DATABASE_SECRET_VERSION}" \
  --no-allow-unauthenticated --no-traffic --tag "$CANDIDATE_TAG"

# GKE, after selecting the approved context and recording the existing image
kubectl -n "$GKE_NAMESPACE" set image \
  "deployment/$GKE_DEPLOYMENT" "$GKE_CONTAINER=$APPROVED_IMAGE_DIGEST"
kubectl -n "$GKE_NAMESPACE" rollout status "deployment/$GKE_DEPLOYMENT" --timeout=5m
```

## 6. Final release report

When requested, output structured JSON with `{skill_id, version, target, environment, git_sha, baseline_sha, reviewed_commit, release_config, approval, preflight, tests, coverage, gate_debt, migrations, secrets_verified, artifact, rollout, smoke, rollback, actual_changes, unverified_risks}`; report `not_run`, `not_approved`, or `not_deployed` where applicable. Never include credential values, access tokens, secret payloads, or entire environment dumps.

**References:** Google Cloud Run deploy functions, Secrets, GKE CSI, and rollout documentation linked in `references/*.md`. Integrate with `python-project-setup`, `python-development`, `python-testing`, and `python-code-review` if installed; do not duplicate those skills' full instructions.
