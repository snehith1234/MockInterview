MOCK INTERVIEW ASSESSMENT REPORT
========================================
Role: DevOps Engineer
Date: 6/26/2026

# Mock Interview Assessment Report

## 1. Interview Summary
- **Role:** DevOps Engineer  
- **Difficulty:** Mid  
- **Planned Duration:** 30 minutes  
- **Total Questions:** 21  
- **End Reason:** None  

**Overall Score (avg): 6.4/10**  
Across the interview, you demonstrated strong senior-level breadth in AWS, CI/CD, and production operations concepts. You consistently described sensible high-level workflows (promotion gates, rollback thinking, S3 security fundamentals, and incident triage). However, several answers lacked the *concrete operational details* interviewers expect at senior level—especially around **Windows/IIS troubleshooting**, **ordered first-checks**, **exact thresholds/criteria**, **rollback mechanics**, and **implementation-level specifics** (commands, log fields, query examples, and idempotent automation behavior). Your strongest moments were when you tied monitoring signals to deployment decisions and used HTTP semantics correctly (415/400) with a prevention mindset.

---

## 2. Score Breakdown
- **Overall Score:** **6.4/10**
- **Technical Accuracy:** **7.0/10**
- **Depth of Knowledge:** **6.2/10**
- **Communication & Clarity:** **6.6/10**
- **Problem-Solving Approach:** **6.8/10**
- **Role Relevance:** **5.8/10**

**Role relevance note:** The job requirements emphasize **Windows/IIS management + Bash + scripting depth**. Your IIS area was the most visibly under-specified, and Bash/XML/HTTP depth were not demonstrated with the level of detail expected.

---

## 3. Key Strengths (what the candidate did well)
1. **End-to-end production change ownership (conceptual completeness)**
   - In early questions, you connected CI/CD → IaC → deployment → monitoring/verification (CloudWatch Logs/Alarms, SNS, health checks).
2. **Deployment safety mindset**
   - You discussed go/no-go checks, pausing rollout, removing unhealthy instances, and rollback considerations rather than “just redeploy.”
3. **S3 security fundamentals were strong**
   - You covered SSE-KMS, HTTPS-only enforcement intent, versioning, lifecycle policies, and verification via CloudTrail/KMS signals.
4. **HTTP semantics and incident triage reasoning**
   - For 415/400, you correctly interpreted **415 as content-type/media mismatch** and used logs + correlation ideas to narrow root cause.
5. **Operationally aware validation and runbook thinking**
   - Your later incident questions included canary/ramp concepts and “don’t mask regression” intent.

---

## 4. Areas for Improvement (where the candidate was weak)
1. **Windows/IIS troubleshooting lacked the “ordered, concrete first checks”**
   - In Q10 you didn’t provide the requested structured checklist of the first 5 checks with specific logs/event sources and what you’d look for.
2. **Rollback/promotion mechanics were often high-level**
   - Multiple answers referenced rollback, but didn’t specify *exactly* what gets rolled back at each layer (app artifact vs ASG/launch template vs CFN/Terraform stack) and how you ensure idempotent, safe re-runs.
3. **Missing measurable criteria (thresholds/time windows)**
   - Go/no-go and “stop conditions” were frequently described qualitatively (e.g., “alarm fired,” “smoke tests failed”) without concrete thresholds, evaluation periods, or denominators for error rates.
4. **Automation idempotency and failure handling not fully operationalized**
   - In Linux patch automation questions (Q12–Q13), you described the shape but not the exact mechanisms (dry-run, package candidate comparison, transaction state handling, deterministic health pass/fail).
5. **Not enough implementation-level detail (commands/queries/log fields)**
   - Several questions asked for exact queries or evidence (Splunk/CloudWatch query examples, log fields, JSON schema). Your answers stayed at a “what to do” level rather than “how to do it.”

---

## 5. Question-by-Question Analysis

> **Scoring note:** Scores are based on the provided per-question evaluations (0–10).

### Q1
**Question:** Walk me through one recent production change you owned end-to-end for an AWS-based system (infra + CI/CD + deployment).  
**Score:** 6/10  
**Why asked:** Validate senior ownership across CI/CD, IaC, AWS components, and verification.  
**Good about answer:**
- Coherent end-to-end flow: Jenkins/GitLab, Terraform/CloudFormation, EC2/S3/IAM, CloudWatch/SNS.
- Mentioned safety practices like plan validation and post-release health checks.  
**Missing / improve:**
- Pipeline stages, promotion strategy, artifact immutability, and rollback mechanics were not concrete.
- Didn’t clearly separate “what you personally implemented” vs team work.
- Least-privilege and secrets handling were not evidenced with specifics.  
**Ideal answer (strong/perfect):**
- “I owned the full release: **build → unit/integration tests → Terraform plan → manual approval → apply → deploy app artifact → smoke tests → promote**.  
  - Rollback: if **ALB target health** or **p95 latency** crosses threshold for **10 minutes**, I **stop traffic** (remove from target group) and **redeploy previous immutable artifact**; if infra change is involved, I revert via **CloudFormation change set rollback** or **Terraform revert commit + apply** using the same remote state.  
  - Evidence: I used CloudWatch alarms (list names/metrics), and I verified **/healthz** returns 200 with readiness semantics.”

---

### Q2
**Question:** When that deployment went out, what exact “go/no-go” checks did you personally use?  
**Score:** 6/10  
**Why asked:** Senior-level operational rigor: thresholds, time windows, and decision logic.  
**Good:**
- Mentioned pipeline gate and production approval.
- Included monitoring-based rollback concept.  
**Missing:**
- No exact alarm names/metrics/thresholds/time windows.
- Rollback mechanics and whether it’s infra vs app rollback weren’t operationalized.  
**Ideal answer:**
- “Go/no-go checklist:  
  1) **No new CloudWatch alarm** in first **5 minutes**: `5xxErrorRate > 1%` for 3 datapoints (1-min).  
  2) **ALB target health**: unhealthy targets < **1%** and no target flapping for **10 minutes**.  
  3) **Synthetic /healthz**: 200 within **2s** and correct readiness headers.  
  4) **Deployment logs**: no config parse exceptions.  
  If fail: pause rollout, remove new instances from target group, redeploy previous artifact.”

---

### Q3
**Question:** When you saw first signs of unhealthy deployment, what was your production mindset/decision process?  
**Score:** 7/10  
**Why asked:** Incident triage and blast-radius control.  
**Good:**
- Good branching: pause/hold vs isolate vs rollback.
- Mentioned removing bad instances and stakeholder coordination.  
**Missing:**
- Thresholding logic/time-boxing not explicit.
- Partial rollout state detection not detailed.  
**Ideal answer:**
- “I time-boxed triage:  
  - **0–2 min:** stop further rollout + identify affected ASG/target group.  
  - **2–5 min:** compare error rate and latency for new version vs baseline using dimensions (target group, instance tags).  
  - **5–10 min:** if sustained regression, rollback artifact; if infra stack is in UPDATE_IN_PROGRESS, halt and wait/rollback change set.”

---

### Q4
**Question:** How did you implement rollback in practice?  
**Score:** 6/10  
**Why asked:** Deterministic rollback mechanics and idempotency.  
**Good:**
- Mentioned rollback levers across app and infra.
- Mentioned pausing pipeline and post-rollback validation.  
**Missing:**
- Not step-by-step mapping of what rolled back where.
- In-flight safety/idempotency and state handling not fully described.  
**Ideal answer:**
- “Rollback steps:  
  1) Freeze pipeline + acquire lock.  
  2) App rollback: redeploy previous immutable artifact to the same deployment controller.  
  3) Traffic rollback: revert ALB listener rules/weighted target groups to 100% previous.  
  4) Infra rollback (if needed): use **CloudFormation change set** to revert to last known-good stack template/parameters; ensure stack status is `*_COMPLETE`.  
  5) Validate: target health + /healthz + alarm stability for **N minutes**.”

---

### Q5
**Question:** Using Octopus/Bamboo to promote dev → staging → prod, how do you handle infra state and avoid partial updates?  
**Score:** 6/10  
**Why asked:** Promotion state persistence, drift detection, and guardrails.  
**Good:**
- Correctly emphasized blocking promotion when staging fails.
- Mentioned AWS signals (stack status, ASG LT version, target health).  
**Missing:**
- No concrete persisted state fields/records.
- Drift detection and Terraform state consistency not operationalized.  
**Ideal answer:**
- “Octopus deployment record stores: release id, artifact version, CFN change set id, expected ASG launch template version, and Terraform state reference.  
  Pre-deploy guardrail checks:  
  - CFN stack status is `UPDATE_COMPLETE` and not `*_IN_PROGRESS`.  
  - Terraform plan shows **no unexpected diffs** (or drift is reconciled).  
  - ASG instances are tagged with the expected version before promoting.”

---

### Q6
**Question:** In Octopus/Bamboo, how would you implement guardrails like “no deploy while AWS is in flight” and “match expected ASG/LT version”?  
**Score:** 6/10  
**Why asked:** Concrete pipeline implementation details.  
**Good:**
- Mentioned pre-deploy checks and AWS signals.  
**Missing:**
- Didn’t specify where/how in Octopus/Bamboo (step names, conditions).
- Terraform drift check and mapping release→LT version not concrete.  
**Ideal answer:**
- “I’d implement a **Pre-deploy script step** that reads the release manifest, then queries:  
  - CFN stack status via AWS SDK  
  - ASG launch template version via `DescribeAutoScalingGroups`  
  - target group health via ELBv2  
  If mismatch: fail step and block deployment conditionally.”

---

### Q7
**Question:** S3 security: encryption, versioning, lifecycle, access controls for static + sensitive uploads.  
**Score:** 7/10  
**Why asked:** AWS S3 security posture and compliance/cost tradeoffs.  
**Good:**
- Covered SSE-KMS, HTTPS-only intent, versioning, lifecycle, least privilege concept.
- Mentioned CloudTrail/KMS verification.  
**Missing:**
- TLS enforcement details and KMS key restriction conditions.
- Lifecycle policy design for different prefixes/retention.  
**Ideal answer:**
- “Bucket policy enforces `aws:SecureTransport=true` and denies non-TLS.  
  SSE-KMS uses a specific CMK with conditions like `kms:ViaService` and `kms:EncryptionContext`.  
  Lifecycle: static assets under `static/*` transition to IA; sensitive under `uploads/*` retains noncurrent versions for compliance and expires delete markers appropriately.  
  Alerts: CloudTrail `AccessDenied` spikes and KMS decrypt usage anomalies.”

---

### Q8
**Question:** Least-privilege IAM for the S3 bucket (static assets + sensitive uploads). Walk through policy design.  
**Score:** 6/10  
**Why asked:** IAM action/resource scoping and KMS permission granularity.  
**Good:**
- Separation of runtime vs CI/CD roles; prefix scoping intent.
- Mentioned KMS permission need.  
**Missing:**
- Specific IAM actions and correct ARN scoping (bucket vs object).
- KMS conditions and Deny patterns not explicit.  
**Ideal answer:**
- “Runtime role:  
  - `s3:GetObject` on `arn:aws:s3:::bucket/static/*`  
  - `s3:PutObject` only for `uploads/*` (if needed)  
  - `s3:ListBucket` only with `s3:prefix` condition  
  - KMS: allow `kms:Encrypt/Decrypt/GenerateDataKey*` only for the CMK ARN and with `kms:EncryptionContext` constraints.  
  CI/CD role gets write permissions to `static/*` and controlled access to `uploads/*` if required; runtime role is explicitly denied from other prefixes.”

---

### Q9
**Question:** Provision EC2 service behind ALB/target group using Terraform/CloudFormation. Walk through.  
**Score:** 7/10  
**Why asked:** Secure EC2 provisioning, networking, IAM, observability, and operational safety.  
**Good:**
- Strong structure: VPC/subnets/AMI/LT/ASG/target group/health checks/tags.
- Mentioned IMDSv2 and CloudWatch alarms.  
**Missing:**
- IAM action/condition specifics.
- Egress restrictions and operational rolling update details.  
**Ideal answer:**
- “I’d define:  
  - Security groups: inbound only from ALB SG; egress restricted via VPC endpoints/NAT.  
  - IAM: instance profile with exact actions + KMS conditions + Secrets Manager ARN scoping.  
  - ASG rolling update: health check grace period, instance refresh strategy, termination policies, and target group deregistration delay.  
  - Observability: structured logs, metric filters, and alarms with explicit thresholds.”

---

### Q10
**Question:** Windows Server/IIS intermittent 502/503 after deployment—what logs/metrics do you check first (ordered first 5 checks)?  
**Score:** 4/10  
**Why asked:** Critical JD area—Windows/IIS troubleshooting depth.  
**Good:**
- Mentioned pause rollout, compare with healthy server, and plausible causes (app pool, Event Viewer).  
**Missing:**
- Not an ordered “first 5 checks” list.
- Lacked IIS/WAS-specific log sources, event IDs, and concrete validation steps.  
**Ideal answer:**
- “First 5 checks (in order):  
  1) **IIS logs**: correlate timestamps with deploy; inspect `sc-status`, `substatus`, `time-taken`, `site`, `server-ip`.  
  2) **Event Viewer** → **WAS** and **W3SVC**: look for worker process crash/restart, binding failures.  
  3) **App Pool** settings: identity, pipeline mode, CLR version, rapid-fail protection, recycling schedule.  
  4) **Bindings/certificates**: verify host header/SNI mapping and certificate thumbprint; ensure private key access for app pool identity.  
  5) **Health endpoint + upstream**: confirm whether 502/503 is readiness failure vs upstream dependency; check target group health and upstream connectivity.”

---

### Q11
**Question:** If first checks don’t reveal cause, what’s your PowerShell-driven remediation plan?  
**Score:** 7/10  
**Why asked:** Practical remediation with safe IIS operations.  
**Good:**
- Pause rollout/remove node, validate bindings/certificates, recycle only affected app pool.
- Mentioned verification via health checks.  
**Missing:**
- Certificate thumbprint/binding mapping details and private key ACL validation.
- Safe recycle procedure and measurable success criteria.  
**Ideal answer:**
- “PowerShell steps:  
  - Validate binding: `Get-WebBinding -Name <site> -Protocol https` and map to cert thumbprint.  
  - Validate cert private key ACL for app pool identity.  
  - Restart app pool with minimal disruption: `Restart-WebAppPool` and confirm worker process PID changes.  
  - Verify: target health returns healthy and error rate drops below threshold for **10 minutes**; if worsens, revert to previous config version and reintroduce previous artifact.”

---

### Q12
**Question:** Linux idempotent automation (Python or Bash): patching + restart + health verification + JSON report.  
**Score:** 5/10  
**Why asked:** Implementation-level idempotency and automation reliability.  
**Good:**
- Correct general idempotent shape: check → update if needed → restart if changed → health check → JSON output.
- Mentioned systemctl/journalctl and structured JSON concept.  
**Missing:**
- No concrete algorithm for determining “needed updates” (dry-run, candidate version comparison).
- JSON schema fields and error taxonomy missing.
- No safe update mechanics/rollback strategy.  
**Ideal answer:**
- “Algorithm:  
  1) Acquire lock (file lock or distributed lock).  
  2) Capture current versions (`dpkg-query`/`rpm -q`).  
  3) Dry-run update (`apt-get -s upgrade` or `yum/dnf check-update`) to compute candidate changes.  
  4) If no changes: exit with JSON `{changed:false}`.  
  5) Apply updates non-interactively; handle package manager locks.  
  6) Restart service only if binary/package version changed.  
  7) Health check with timeouts/retries; emit JSON with before/after versions, commands, and structured failure reasons.”

---

### Q13
**Question:** In that patch-cycle script, how would you handle re-runs and partial success?  
**Score:** 6/10  
**Why asked:** Idempotency under partial failure and deterministic rollback ordering.  
**Good:**
- Mentioned recording state and rollback concept.  
**Missing:**
- Re-run behavior not fully specified (state machine/markers).
- Rollback ordering and dependency handling underspecified.
- Health check determinism and timeouts not explicit.  
**Ideal answer:**
- “I’d implement a state machine in JSON/marker files: `precheck_done`, `update_done`, `restart_done`, `health_passed`.  
  On re-run, it resumes safely from the last completed state.  
  Rollback ordering: stop service → revert package/config using transaction history → restart → verify health.  
  Health check uses explicit thresholds/timeouts and fails fast if readiness isn’t met.”

---

### Q14
**Question:** After patch cycle, health check fails—how do you do triage/RCA and corrective actions?  
**Score:** 6/10  
**Why asked:** Monitoring-driven RCA and containment.  
**Good:**
- Mentioned rollback validation and dependency investigation examples.
- RCA documentation elements included.  
**Missing:**
- No explicit signal-first triage flow with correlation to timeline.
- Mixed-version fleet handling and monitoring configuration verification missing.  
**Ideal answer:**
- “Triage flow:  
  1) Correlate alarm timestamps with automation run id/AMI/version tags.  
  2) Determine scope: instance-level vs target-group vs end-to-end service.  
  3) Check monitoring config: alarm evaluation periods and whether rollback changed dimensions.  
  4) If mixed versions: drain remaining nodes and converge fleet to last known-good.  
  5) Corrective actions: update runbook, add pre-deploy checks, tune dependency timeouts, and add regression tests.”

---

### Q15
**Question:** REST API starts returning 415/400 after release—how do you use HTTP semantics to pinpoint mismatch?  
**Score:** 7/10  
**Why asked:** Web fundamentals + deployment/config prevention.  
**Good:**
- Correct interpretation of 415 vs 400.
- Used logs and compared headers before/after.  
**Missing:**
- Deeper HTTP semantics checks (Accept, charset, encoding, etc.).
- Concrete config changes (IIS requestFiltering, MIME mappings, serializer settings).  
**Ideal answer:**
- “I’d check:  
  - `Content-Type` vs expected media type per endpoint  
  - `Accept` negotiation and `Vary` behavior  
  - charset/encoding and payload shape (JSON/XML)  
  - IIS requestFiltering/MIME mapping and app serializer settings  
  - correlation IDs and sample failing payloads (redacted)  
  Then I’d add contract tests for both valid and invalid combinations.”

---

### Q16
**Question:** Same client sometimes sends `Content-Type:` … (intermittent mismatch) — how do you prove it?  
**Score:** 6/10  
**Why asked:** Observability + evidence-based root cause.  
**Good:**
- Filter by endpoint/client/status/correlation ID.
- Hypothesis about payload/header mismatch.  
**Missing:**
- Concrete evidence fields and how to prove correlation across layers.
- Specific deployment/config changes and alerting mechanics.  
**Ideal answer:**
- “I’d show:  
  - request headers captured in logs (Content-Type/Accept)  
  - request body first bytes (redacted) to confirm XML vs JSON  
  - server exception types and response reason phrases  
  - correlation ID propagation from gateway → app  
  Then enforce/normalize at the edge and add negative contract tests.”

---

### Q17
**Question:** After deploying fix, how do you confirm you’re not missing regression?  
**Score:** 6/10  
**Why asked:** Post-fix validation and regression control.  
**Good:**
- Compare logs in time windows before/after.
- Focus on expected error categories decreasing.  
**Missing:**
- No exact metrics/log queries or thresholds.
- No confounder control (traffic mix, caching/CDN/WAF).  
**Ideal answer:**
- “I’d compute error rate denominators: `4xx/total requests` and `415 rate` per endpoint and client version, compare to baseline (last 14 days).  
  I’d also verify latency/p95 and 2xx success rate.  
  Use canary/traffic tagging to isolate release-related traffic.”

---

### Q18
**Question:** Pick one endpoint: exactly what would you add/change in monitoring (query + guardrails)?  
**Score:** 6/10  
**Why asked:** Implementation-level monitoring design.  
**Good:**
- Correct goal: detect endpoint-specific regressions and separate warning vs paging.  
**Missing:**
- No explicit query syntax or exact fields.
- Baseline approach and minimum volume guardrails not clear.  
**Ideal answer:**
- “CloudWatch Logs Insights example: filter `endpoint="/api/v1/customer/upload"`, group by `clientVersion`, `releaseVersion`, compute `count(status=415)/count(*)` over 5m windows; page only if volume > X and sustained for Y datapoints; compare to baseline from last N days.”

---

### Q19
**Question:** Runbook-driven incident response: first checks + decision criteria.  
**Score:** 7/10  
**Why asked:** Operational runbook quality and execution discipline.  
**Good:**
- Pause deployments, notify, inspect logs by endpoint/release/client/error type.
- Rollback vs fix vs client coordination logic included.  
**Missing:**
- First 3 checks weren’t explicitly numbered with concrete artifacts.
- Decision criteria lacked measurable thresholds and rollback success validation.  
**Ideal answer:**
- “Runbook:  
  1) Check gateway/IIS/app logs for content negotiation mismatch evidence.  
  2) Verify releaseVersion correlation and whether only specific client cohorts are affected.  
  3) Confirm whether 415/400 taxonomy changed.  
  Decision: if sustained regression >0.5% for 10m and only releaseVersion X affected → rollback config to last known-good; else apply targeted edge normalization fix.”

---

### Q20
**Question:** Confirm you’re not masking the issue after canary/ramp config fix—what do you do?  
**Score:** 7/10  
**Why asked:** Guardrails against “false green” and validation rigor.  
**Good:**
- Canary/targeted rollout and synthetic request matrix idea.
- Stop conditions present.  
**Missing:**
- Specific canary mechanics and thresholds/time windows.
- Concrete log/metric checks with denominators.  
**Ideal answer:**
- “I’d ramp 5%→25%→50%→100% while monitoring:  
  - `415 rate` and `400 rate` per client cohort  
  - p95 latency and upstream error codes  
  - ensure invalid requests still fail with correct status (taxonomy unchanged)  
  If invalid requests start succeeding unexpectedly, stop and roll back.”

---

### Q21
**Question:** After ramp, how do you confirm you’re not masking regression?  
**Score:** 8/10  
**Why asked:** Senior-level validation and “don’t broaden acceptance” thinking.  
**Good:**
- Strong focus on pre/post comparison grouped by endpoint/client/release and error categories.
- Considered synthetic negative tests and “stop if invalid succeeds.”  
**Missing:**
- More quantitative SLI/SLO checks and confounder control.
- More explicit “masking detection” beyond “invalid success.”  
**Ideal answer:**
- “I’d validate:  
  - `415/400` taxonomy counts remain consistent (only expected categories decrease)  
  - overall 2xx rate doesn’t hide validation failures  
  - p95 latency/throughput unchanged  
  - compare only release-tagged traffic (canary cohort) to avoid confounders.”

---

## 6. Skills Gap Analysis

### Skills demonstrated strongly
- **AWS breadth:** EC2, S3, IAM concepts, CloudWatch monitoring, event-driven thinking.
- **CI/CD + deployment safety mindset:** promotion gates, rollback thinking, canary/ramp concepts.
- **Security fundamentals:** S3 encryption/versioning/lifecycle and least-privilege intent.
- **Incident response reasoning:** triage flow, evidence-based hypotheses, runbook thinking.
- **HTTP semantics awareness:** correct interpretation of 415/400 and content negotiation mismatch.

### Skills that need improvement
- **Windows/IIS troubleshooting depth (critical JD):**
  - Need ordered first-checks, specific IIS/WAS logs, event IDs, binding/cert thumbprint mapping, private key ACL validation, and safe app pool recycle steps.
- **Concrete operational details:**
  - Provide exact thresholds, time windows, alarm names/metrics, and log query examples.
- **Rollback/promotion mechanics:**
  - Must describe deterministic rollback at each layer and idempotent re-run behavior.
- **Automation implementation-level idempotency:**
  - Dry-run/candidate version comparison, package manager transaction handling, state machine markers, deterministic health checks.
- **Monitoring design implementation:**
  - Include query syntax/fields, denominators, baselines, minimum volume guardrails.

### Skills not tested but required for the role
- **Bash scripting proficiency** (explicitly required in JD; you didn’t demonstrate Bash).
- **XML handling / deeper web fundamentals** (XML wasn’t evidenced beyond HTTP concepts).
- **MSBuild/NUnit/Bamboo/Octopus hands-on validation** (skills listed, but interview answers leaned heavily on Jenkins/GitLab + general Octopus/Bamboo concepts).
- **IIS management tooling commands** (appcmd/netsh/http.sys/powershell specifics were not fully shown).

---

## 7. Actionable Improvement Plan (7-day study plan)

### Day 1–2: Windows/IIS troubleshooting (highest ROI)
**Focus:** Ordered first-checks + evidence-driven remediation  
**Resources:**
- Microsoft docs: IIS logs, WAS/W3SVC event logs, app pool settings, bindings/certificates
- PowerShell cmdlets: `Get-WebBinding`, `Restart-WebAppPool`, `Get-Item Cert:\...`, `Get-WebAppPoolState`
- Practice lab: intentionally break bindings/certs and observe 502/503 patterns

**Deliverables:**
- Write a “First 5 checks” runbook template for 502/503 (IIS logs → WAS events → app pool config → bindings/certs → health/upstream).
- Create a PowerShell remediation script outline with validation + rollback criteria.

---

### Day 3–4: CI/CD + rollback/promotion mechanics (make it concrete)
**Focus:** Deterministic rollback across app + infra + traffic routing  
**Resources:**
- AWS: CloudFormation change sets, stack status states, rollback behavior
- Terraform: remote state locking, drift detection, plan/apply gates
- Octopus/Bamboo concepts: deployment records, pre-deploy checks, conditions

**Deliverables:**
- Prepare a “promotion manifest” example: release id → artifact version → expected ASG LT version → CFN change set id.
- Practice describing rollback step-by-step with idempotency and in-flight safety.

---

### Day 5–6: Linux automation idempotency + observability queries
**Focus:** Implementation-level idempotent patch script + JSON schema + health checks  
**Resources:**
- apt/yum/dnf dry-run commands
- systemd best practices
- CloudWatch Logs Insights / Splunk SPL basics (fields, filters, group-by, denominators)

**Deliverables:**
- Draft a Python script pseudocode with:
  - lock acquisition
  - dry-run candidate detection
  - conditional restart
  - deterministic health check with timeouts
  - JSON output schema (before/after versions, changed flag, errors list)

---

### Day 7: Mock practice suggestions
- Do **2 timed mock rounds (15 min each)**:
  1) IIS 502/503 ordered checks + PowerShell remediation
  2) Linux idempotent patch + rollback + JSON output
- Record yourself and ensure every answer includes:
  - ordered steps
  - measurable thresholds/time windows
  - exact evidence sources (logs/metrics fields)

---

## 8. Recommended Practice Questions (target your weak areas)

1. **Windows/IIS:** “Give the first 5 checks (ordered) for intermittent 502 after a deployment. Include exact logs/event sources and what fields indicate the root cause.”
2. **Windows/IIS:** “How do you validate that the IIS HTTPS binding is using the correct certificate thumbprint and that the app pool identity has private key access?”
3. **Rollback mechanics:** “Design a rollback that reverses: (a) ALB routing, (b) app artifact, and (c) CloudFormation stack changes. What are the exact steps and how do you ensure idempotency?”
4. **Promotion guardrails:** “What exact persisted fields would you store in Octopus/Bamboo to prevent promotion on partial infra updates? How do you check them?”
5. **Linux idempotency:** “Write the algorithm for an idempotent patch script using apt/yum dry-run to decide whether restart is needed. Include JSON schema.”
6. **Monitoring implementation:** “Provide a CloudWatch Logs Insights query (or Splunk SPL) to compute 415 rate per endpoint and release version with a minimum volume guardrail.”
7. **Masking regression:** “How do you detect that a validation layer is ‘accepting too much’ after a config fix? What metrics/log categories prove it?”

---

## 9. Interview Tips (technique improvements)
1. **Always answer with an ordered checklist when asked for “first checks”**
   - For Q10, the missing piece wasn’t correctness—it was structure. Use “1…2…3…” and tie each step to a hypothesis and evidence.
2. **Quantify decisions**
   - When you say “alarm fired” or “smoke test failed,” add: metric name, threshold, evaluation window, and what constitutes sustained failure.
3. **Use “layered rollback” language**
   - Explicitly separate: **traffic routing rollback**, **app artifact rollback**, **infra rollback**—and describe the exact trigger for each.
4. **Bring one concrete artifact per answer**
   - Examples: a sample JSON schema, a query snippet, a PowerShell cmdlet list, or a runbook template. This makes senior answers feel “real.”
5. **Close with verification + rollback criteria**
   - End answers with: “Success looks like X for Y minutes; if not, I do Z.”

---

If you want, I can also provide a **one-page “senior DevOps answer template”** you can reuse in interviews (for rollback, promotion gates, incident triage, and IIS troubleshooting) tailored to your demonstrated strengths and the gaps above.

========================================
Generated by Mock Interview Agent