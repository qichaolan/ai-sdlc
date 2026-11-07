# GCP and Docker signals

Things worth looking at for each review area. A signal is a reason to look closer, not a finding. Confirm it applies to this system before reporting it, and don't treat this list as complete. Platform defaults change, so check current documentation when a finding depends on one.

## Authentication

- JWTs that are decoded without verifying the signature, or verified without checking `iss`, `aud`, and `exp`. An audience check is what stops a token issued for another service from working here.
- Firebase or Google ID tokens parsed by hand rather than verified with the SDK.
- Identity read from client-settable headers, such as `X-Forwarded-User`, `X-Goog-Authenticated-User-Email`, or `X-CloudTasks-*`. On a path that doesn't pass through the component that sets or strips them, a caller can forge them. If IAP is in use, the app should validate the signed `X-Goog-IAP-JWT-Assertion`.
- Pub/Sub push, Cloud Tasks, and Cloud Scheduler targets that accept requests without validating the OIDC token and its audience.
- Webhooks with no signature check, or a check that isn't constant-time or that signs a re-serialized body.
- Route exemptions that are too broad, health or debug routes that return real data, and auth middleware registered after the routes it should cover.

## Authorization and tenant isolation

- Queries by primary key alone, such as `get(id)` with no owner or tenant condition.
- A tenant ID taken from the request body or path instead of the verified token.
- Firestore rules that are permissive or unused because the backend uses the Admin SDK, which bypasses rules entirely, so the backend must enforce access itself.
- Cloud SQL row-level security that a connection pool or superuser role silently bypasses.
- Jobs, exports, and reports that run as a service identity without carrying over the requesting user's scope.
- Signed URLs and GCS object names that are guessable, long-lived, or issued without an ownership check.
- Cache keys that omit the tenant or user.
- Mass assignment, where a client can set fields such as `role`, `tenant_id`, or `is_admin`.

## Injection and unsafe execution

- SQL or BigQuery text built with string formatting, including sort columns and table names that can't be parameterized.
- `subprocess` with `shell=True`, `exec`, `eval`, unsafe `pickle` or YAML loading, and templates rendered from user input.
- Paths built from user input or archive entries, and upload handling that trusts the filename or content type.
- Any server-side fetch of a user-influenced URL. On GCP the prize is usually `http://metadata.google.internal` or `169.254.169.254`, which returns service account tokens. The required `Metadata-Flavor: Google` header limits simple SSRF but doesn't help if the attacker controls headers or the fetch forwards them. Robust defenses resolve the hostname and check the resulting address, re-check after redirects, cover IPv6 and alternate address forms, and guard against DNS rebinding.
- Prompt injection, where LLM output reaches tools, queries, or commands with the service's privileges.

## Secrets and IAM

- Credentials in source, git history, `.env` files, CI config, Terraform state, or image layers. A secret deleted in a later layer or commit still exists in the earlier one.
- Secrets in plain Cloud Run environment variables, which anyone able to view the service configuration can read. Secret Manager references avoid this.
- Runtime workloads using the default compute service account, which often holds project Editor.
- Primitive roles (`roles/owner`, `roles/editor`) or broad predefined roles on application identities.
- Project-level `secretAccessor` grants when per-secret bindings would do.
- Downloaded service account key files where attached identities or Workload Identity Federation would work.
- `serviceAccountUser` or `serviceAccountTokenCreator` grants, which let the holder act as a more powerful identity.

## Network and data exposure

- Cloud Run or Cloud Functions granting `allUsers` the invoker role when the service isn't meant to be public. Deploy flags such as `--allow-unauthenticated` are the usual source.
- The default `*.run.app` URL staying reachable behind a load balancer, which bypasses Cloud Armor and IAP. Check the ingress setting and whether the default URL is disabled.
- Cloud SQL with a public IP, especially authorized networks containing `0.0.0.0/0`.
- GCS buckets or objects granted to `allUsers` or `allAuthenticatedUsers`. The second means any Google account, not your users.
- Firewall rules opening admin or database ports to `0.0.0.0/0`.
- Admin consoles, `/metrics`, `/debug`, API docs, profilers, or actuator endpoints exposed in production.
- Verbose errors, permissive CORS with credentials, and responses that serialize whole database objects.

## Docker, dependencies, and deployment

**Image contents**
- `COPY . .` without a suitable `.dockerignore`, which can pull in `.env`, `.git`, and keys.
- Secrets passed through `ARG` or `ENV`, which persist in image metadata. BuildKit secret mounts avoid this.
- Single-stage builds that ship compilers and package managers to production.
- `latest` or unpinned base images, end-of-life base images, and images that haven't been rebuilt in a long time.

**Runtime privileges.** Weigh these by platform. Cloud Run's sandbox makes `--privileged` and host mounts irrelevant and lowers the impact of running as root, while they can be critical on Compute Engine, GKE, or Docker Compose.
- No `USER`, so the container runs as root.
- `privileged: true`, added capabilities, `hostNetwork`, or host path mounts.
- A mounted `/var/run/docker.sock`, which is effectively root on the host.
- Compose `ports` publishing databases or caches on all interfaces. Docker's published ports can also bypass host firewall rules such as `ufw`.

**Dependencies**
- Known vulnerabilities in code that is actually reachable. Prioritize those over the raw scanner count.
- Missing lockfiles, unmaintained packages, and install steps that run unpinned scripts.

**Pipeline**
- CI authenticating with a long-lived service account key rather than federation.
- GitHub Actions using `pull_request_target` with untrusted code, third-party actions pinned to movable tags, or overly broad `GITHUB_TOKEN` permissions.
- Deploy identities with project-wide admin rights, and the ability to reach production without review.
- Artifact Registry repositories that are public or that production pulls from by mutable tag rather than digest.

## Abuse protection and logging

- No rate limit on login, password reset, OTP, signup, or expensive endpoints.
- In-memory rate limiting on a service with multiple instances, where each instance counts separately.
- Limits keyed on the leftmost `X-Forwarded-For` value, which the client controls.
- Missing request body limits, timeouts on outbound calls, pagination caps, or upload size limits.
- Cloud Run with no sensible `max-instances`, or paid APIs such as LLMs with no per-user quota, so abuse turns directly into cost.
- Tokens, passwords, API keys, or personal data in application logs, or request bodies and headers logged wholesale.
- No record of authentication failures, permission denials, or admin actions. Cloud Audit Data Access logs are mostly off by default, so sensitive data reads may leave no trace.

## Read-only evidence

Run these only with the user's approval, and confirm the project first. The output can include sensitive values, so redact them in your report.

```bash
gcloud run services describe SERVICE --region REGION --format=yaml  # can print env var values
gcloud run services get-iam-policy SERVICE --region REGION
gcloud projects get-iam-policy PROJECT
gcloud iam service-accounts keys list --iam-account SA_EMAIL
gcloud secrets get-iam-policy SECRET
gcloud sql instances describe INSTANCE
gcloud storage buckets get-iam-policy gs://BUCKET
gcloud compute firewall-rules list
```

Don't run `gcloud secrets versions access` or anything that creates a token or key. You can review who has access to a secret without reading it.

For images and code, use whichever of these are already installed. They are local or read-only, though dependency audits send package names to their advisory service.

```bash
docker history --no-trunc IMAGE
docker image inspect IMAGE
gitleaks detect --redact   # includes git history
trivy image IMAGE
trivy config .
hadolint Dockerfile
semgrep scan               # some rule configs download from or report to the registry
pip-audit
npm audit
govulncheck ./...
```
