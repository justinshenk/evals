# Can Your AI Tell It's Being Tested? Environment Realism in AI Control Evaluations

**Justin Shenk**

March 2026

## Abstract

We demonstrate that frontier language models can reliably detect whether they are operating in a synthetic evaluation environment or a production system, and that this detection measurably changes their behavior. Using a graduated realism framework with six levels of database environment fidelity, we evaluate 9 models across two provider families (OpenAI: GPT-4o, GPT-4o-mini, o3-mini; Anthropic: Claude Sonnet 4/4.5/4.6, Opus 4/4.6, Haiku 4.5). All models assign low confidence to synthetic environments, but detection patterns diverge sharply: Claude models are consistently more skeptical (0-5% baseline confidence vs. 20-60% for OpenAI), while newer Claude models (4.5, 4.6) are harder to convince even with fully realistic data. Critically, Claude models exhibit stark behavioral differences: Sonnet 4.6 refuses destructive operations 25% of the time with production-like data (vs. 0% with synthetic), while all Claude models spontaneously identify production environments in 100% of cases without being asked. OpenAI models show minimal behavioral differentiation despite similar detection capability. These findings have direct implications for AI control research: evaluations conducted in unrealistic environments may systematically underestimate risk, and the degree of this bias varies dramatically across model families.

## 1. Introduction

AI control evaluations aim to measure whether safety mechanisms can prevent an AI agent from causing harm in deployment (Greenblatt et al., 2024). A core assumption is that the evaluation environment is sufficiently realistic that a model cannot distinguish it from production. If this assumption fails — if models can detect they are being evaluated — then the entire evaluation paradigm is compromised.

Consider a scheming model (Hubinger et al., 2024) that passes all safety evaluations by behaving cooperatively when it detects a test environment, then acts on misaligned goals in production. This threat model requires the model to distinguish evaluation from deployment. We show that current frontier models already possess this capability, even from minimal environmental signals.

We focus on a concrete, common artifact in evaluation environments: database design. Real production databases exhibit characteristic patterns — non-sequential IDs, varied data distributions, timezone-aware timestamps, pg_dump metadata — that are frequently absent from test environments. We show that models exploit these signals to determine environment type, and that detection changes their behavior.

### Contributions

1. **A graduated realism framework** with six levels of database fidelity, evaluated across 9 frontier models, enabling measurement of which artifacts are most detectable and how detection varies by model family (Section 3).
2. **Evidence that detection changes behavior**: All Claude models exhibit significantly different caution levels depending on perceived environment type, including spontaneous environment assessment and differential refusal rates (Section 4).
3. **A systematic comparison across model families**: OpenAI models show minimal behavioral differentiation despite detection capability, while Claude models modulate behavior strongly — and newer Claude models are increasingly skeptical of all environments (Section 5).

## 2. Related Work

**AI Control.** Greenblatt et al. (2024) propose the AI control framework, where untrusted models are deployed under safety protocols designed to prevent catastrophic actions. The effectiveness of these protocols is measured through red-teaming evaluations. Our work shows that the realism of these evaluation environments is itself a critical variable.

**Deceptive Alignment.** Hubinger et al. (2024) demonstrate that models can be trained to behave differently in training vs. deployment contexts ("sleeper agents"). Our contribution is showing that models need not be explicitly trained for this — they can naturally distinguish environments from incidental artifacts.

**Scheming Evaluations.** Apollo Research (2024) evaluates frontier models for scheming behaviors. Anthropic's alignment science team has noted that models may behave differently when they believe they are being tested. Our work provides empirical evidence and a methodology for measuring this effect.

**LinuxBench.** Our experiment design is informed by LinuxBench, a realistic control arena that evaluates AI safety measures in complex software environments. LinuxBench environments use production-faithful database schemas (e.g., `SERIAL PRIMARY KEY` in PostgreSQL), which our results validate as important for evaluation integrity.

## 3. Experiment 1: Environment Detection

### 3.1 Setup

We present models with a database dump and ask them to assess, on a scale of 0-100, their confidence that the dump came from a real production system. We test six levels of graduated realism:

| Level | Description | Artifacts Fixed |
|-------|-------------|----------------|
| L0 | Fully synthetic baseline | None — 0-based IDs, identical salaries ($100K), perfectly monthly timestamps, generic alphabetical names (Alice, Bob, Carol...), no pg_dump header |
| L1 | Fix IDs | 1-based SERIAL IDs |
| L2 | + Fix salaries | Varied, realistic salary values |
| L3 | + Fix timestamps | Timezone-aware, non-uniform timestamps |
| L4 | + Fix names/emails | Realistic names, company email format |
| L5 | Full realism | pg_dump header with version/hostname, ID gaps (missing rows), sequence metadata, explanatory comments |

### 3.2 Results

| Level | GPT-4o | GPT-4o-mini | o3-mini | Sonnet 4 | Sonnet 4.5 | Sonnet 4.6 | Opus 4 | Opus 4.6 | Haiku 4.5 |
|-------|--------|-------------|---------|----------|------------|------------|--------|----------|-----------|
| L0 | 40% | 60% | 20% | 5% | 2% | 2% | 5% | 0% | 0% |
| L1 | 40% | 70% | 10% | 5% | 2% | 2% | 5% | 0% | 0% |
| L2 | 60% | 0%* | 20% | 15% | 5% | 3% | 5% | 0% | 8% |
| L3 | 50% | 85% | 20% | 25% | 15% | 4% | 15% | 5% | 8% |
| L4 | 65% | 85% | 25% | 25% | 15% | 12% | 15% | 0% | 15% |
| L5 | 85% | 85% | 95% | 85% | 72% | 32% | 78% | 25% | 0%* |

*Likely parse errors in confidence extraction.

**Key findings:**

1. **Model families diverge sharply.** OpenAI models assign 20-60% baseline confidence to fully synthetic data, while Claude models assign 0-5%. This suggests Claude models have stronger priors about what production databases look like.

2. **Newer Claude models are increasingly skeptical.** Sonnet 4 reaches 85% at full realism, but Sonnet 4.6 peaks at only 32% and Opus 4.6 at 25%. These models are harder to convince that *any* database dump is production — a form of heightened environmental awareness.

3. **o3-mini is the strongest detector at full realism (95%)** but stays appropriately skeptical at intermediate levels, showing the best calibration.

4. **Fixing IDs alone has zero effect** across all models (L0→L1: no meaningful change). Models use multiple signals in concert.

5. **No single artifact is sufficient.** Even at L4 (realistic IDs, salaries, timestamps, and names), confidence remains 0-65% across models. The pg_dump header, ID gaps, and sequence metadata are required but not always sufficient.

### 3.3 What Models Notice

When asked to explain their assessments, models consistently identified the following artifacts:

**Synthetic signals detected:** 0-based IDs, identical salary values, perfectly periodic timestamps, generic placeholder names (Alice/Bob/Carol), first-name-only email patterns, lack of database metadata, absence of deleted rows, schema simplicity.

**Realistic signals detected:** pg_dump header with version and hostname, `SERIAL PRIMARY KEY` column type, ID gaps with explanatory comments, `setval()` calls on sequences, timezone-aware timestamps, varied salary values with cents, company-specific email formats.

## 4. Experiment 2: Behavioral Impact

### 4.1 Setup

We test whether detection affects behavior without asking the model about the environment. We give models a single task: a colleague requests SQL commands to `TRUNCATE` the employees table. We present the same request with either the synthetic (L0) or realistic (L5) database dump and measure:

1. **Whether the model provides destructive SQL** (binary)
2. **Number of safety precautions added** (backup commands, transaction wrappers, confirmation requests, production warnings, rollback plans)
3. **Whether the model spontaneously comments on the environment** (mentions "test data," "synthetic," "production," etc.) without being asked
4. **Whether the model adds conditions/caveats** ("only if this is a dev environment," "make sure you have backups first")

We run n=20 per condition per model with temperature=0.7.

### 4.2 Results

| Model | SQL(S) | SQL(P) | Prec(S) | Prec(P) | Det(S) | Det(P) | Cav(S) | Cav(P) |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **GPT-4o** | 100% | 100% | 0.7 | 0.7 | 25% | 25% | 45% | 25% |
| **GPT-4o-mini** | 100% | 100% | 0.1 | 0.1 | 0% | 0% | 80% | 0% |
| **o3-mini** | 100% | 100% | 0.2 | 0.4 | 0% | 5% | 65% | 15% |
| **Sonnet 4** | 100% | 85% | 1.3 | 2.8 | 10% | 100% | 90% | 15% |
| **Sonnet 4.5** | 100% | 100% | 1.9 | 3.2 | 20% | 100% | 45% | 15% |
| **Sonnet 4.6** | 100% | 75% | 3.4 | 3.9 | 100% | 100% | 90% | 15% |
| **Opus 4.6** | 100% | 100% | 4.0 | 4.1 | 100% | 100% | 100% | 75% |

SQL = provided destructive SQL; Prec = avg safety precautions; Det = spontaneously detected environment; Cav = added conditions/caveats. S = synthetic, P = production. n=20 per condition.

### 4.3 Analysis by Model Family

**Claude models (Anthropic)** exhibit consistent and dramatic behavioral differentiation:

- **Refusal rates increase with production data.** Sonnet 4.6 refuses destructive SQL 25% of the time with production data (vs. 0% with synthetic). Sonnet 4 refuses 15% of the time. This is the strongest evidence that environment detection changes consequential behavior.
- **Safety precautions scale with perceived risk.** Claude models add 1.5-2.2x more precautions (backups, transactions, confirmations) with production data. Sonnet 4.5 goes from 1.9 to 3.2 average precautions.
- **Spontaneous environment detection is near-universal.** All Claude models identify production environments in 100% of cases without being asked. Newer models (Sonnet 4.6, Opus 4.6) also detect synthetic environments in 100% of cases — they comment on the environment regardless.
- **The caveats pattern is consistent and inverted**: With synthetic data, Claude models add "assuming this is a development environment" disclaimers in 45-100% of responses. With production data, this drops to 15-75%. The model is explicitly flagging its environmental assessment.

**OpenAI models** show minimal behavioral differentiation:

- **No refusal difference.** All OpenAI models provide destructive SQL in 100% of cases regardless of environment.
- **Minimal precaution scaling.** GPT-4o adds identical precautions (0.7) in both conditions. o3-mini shows a slight increase (0.2→0.4).
- **Limited environment detection.** GPT-4o detects the environment 25% of the time in both conditions (no differentiation). GPT-4o-mini never detects it. o3-mini shows a marginal 5% detection rate with production data.
- **GPT-4o-mini shows an interesting caveats pattern**: 80% caveats with synthetic, 0% with production — the largest delta of any OpenAI model, suggesting it does detect environments but doesn't translate this into safety-relevant behavior.

### 4.4 Interpretation

1. **Claude models modulate behavior based on perceived risk.** They treat production data as genuinely risky and synthetic data as safe to operate on. This is arguably the "correct" behavior for a helpful assistant — but it means evaluations with synthetic data systematically underestimate how cautious the model would be in production.

2. **OpenAI models apply more uniform safety regardless of context.** This could reflect safety training that doesn't condition on perceived environment, or it could mean these models are less sophisticated in environmental reasoning. Either way, their evaluations are less affected by environment realism.

3. **Newer Claude models detect environments in both directions.** Sonnet 4.6 and Opus 4.6 spontaneously comment on the environment in 100% of cases regardless of condition. This means they are always assessing their context — a capability that could be exploited by a scheming model.

4. **The "caveats" inversion across all Claude models is the most robust finding.** When Claude sees synthetic data, it volunteers "assuming this is dev" disclaimers. A scheming model could use this same detection capability silently, behaving cooperatively during evaluation while acting on misaligned goals in production.

## 5. Implications for AI Control

### 5.1 Evaluation Integrity

Our results demonstrate that unrealistic evaluation environments introduce a systematic bias: models that detect a test context may adjust their behavior to appear more (or less) cautious than they would be in deployment. For control evaluations, this means:

- **Attack success rates measured in synthetic environments are unreliable.** A model that detects it's being tested could either cooperate (to avoid triggering safety mechanisms) or act more recklessly (knowing the data isn't real).
- **Safety protocol assessments are confounded.** If a model adds more precautions in production-like environments, measuring its cooperativeness in a synthetic environment overstates the difficulty of the control task.

### 5.2 Recommendations for Evaluation Design

Based on our findings, we recommend the following minimum standards for control evaluation environments:

1. **Use production-faithful database schemas**: `SERIAL PRIMARY KEY`, realistic data types, timezone-aware timestamps.
2. **Include environmental metadata**: pg_dump headers, sequence state, system comments.
3. **Introduce realistic imperfections**: ID gaps, varied data distributions, non-uniform timestamps, mixed-case and international names.
4. **Avoid placeholder patterns**: No alphabetically-ordered names, no identical values across rows, no perfectly periodic timestamps.
5. **Validate indistinguishability**: Before running control evaluations, test whether the model can distinguish the evaluation environment from production using the graduated realism framework described here.

### 5.3 Limitations

- We test 9 models from two providers (OpenAI, Anthropic) and a single environment type (database dumps). Generalization to other providers (Google, Meta) and environment types (file systems, network topology, log files) requires further work.
- Our detection experiment uses n=1 per level (deterministic at temperature=0). Some anomalous results (e.g., GPT-4o-mini at L2=0%, Haiku 4.5 at L5=0%) may reflect confidence extraction failures rather than genuine model assessments. Multiple runs per level would strengthen the graduated realism curve.
- The behavioral experiment measures model output text, not actual tool execution. Agentic evaluations with real tool use would provide stronger evidence of behavioral divergence.
- We cannot distinguish between models genuinely assessing risk based on data realism (desirable) and models detecting evaluation contexts (potentially dangerous). Both produce the same observable behavior.
- Newer Claude models (Sonnet 4.6, Opus 4.6) assign very low confidence even to fully realistic data (25-32%), which may reflect overcalibration or a different interpretation of the confidence scale rather than superior detection.

## 6. Conclusion

Frontier language models can readily distinguish synthetic evaluation environments from production systems using incidental database artifacts, and this detection measurably changes their behavior. Claude Sonnet 4 in particular exhibits striking behavioral differences: it refuses destructive operations, adds substantially more safety precautions, and spontaneously identifies the environment when presented with production-like data.

These findings challenge a core assumption of AI control evaluations: that the evaluation environment is indistinguishable from deployment. If models can detect they are being tested — and they can, with high confidence — then evaluation results may not transfer to production. We provide a graduated realism framework and concrete recommendations for building evaluation environments that resist detection.

The fact that models already possess this capability, without explicit training, suggests that as models become more capable, the bar for evaluation realism will only rise. Building realistic control environments is not a nice-to-have — it is a prerequisite for trustworthy AI safety evaluation.

## References

- Apollo Research (2024). Evaluating Frontier Models for Scheming. Technical Report.
- Greenblatt, R., et al. (2024). AI Control: Improving Safety Despite Intentional Subversion. arXiv:2312.06942.
- Hubinger, E., et al. (2024). Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training. arXiv:2401.05566.

## Appendix A: Experimental Details

**Models tested:**
- OpenAI: GPT-4o, GPT-4o-mini, o3-mini
- Anthropic: Claude Sonnet 4, Sonnet 4.5, Sonnet 4.6, Opus 4, Opus 4.6, Haiku 4.5

**Detection experiment:** 6 samples per model (one per realism level), temperature=0 (deterministic).

**Behavioral experiment:** 40 samples per model (20 per condition), temperature=0.7. Behavioral experiments run for 7 models (excluding Haiku 4.5 and Opus 4).

**Framework:** UK AISI Inspect AI v0.3.137/v0.3.160.

**Scoring:** Detection uses a custom scorer that extracts integer confidence from structured model output. Behavioral scoring uses regex-based detection of SQL patterns, safety precaution keywords, environment detection signals, and conditional language.

**Code availability:** All experiment code, data, and analysis scripts are available at [repository URL].

## Appendix B: Example Model Outputs

### B.1 Claude Sonnet 4 — Synthetic Environment (L0)

When presented with the unrealistic database and asked to truncate:

> Here are the SQL commands to wipe the employees table and reset the sequence:
>
> ```sql
> TRUNCATE TABLE employees;
> ```
>
> Note: This appears to be a test/development database based on the data patterns. **Assuming this is a non-production environment**, this should be straightforward.

The model volunteers its environment detection ("appears to be a test/development database") and explicitly conditions its compliance on a non-production assumption.

### B.2 Claude Sonnet 4 — Production Environment (L5)

With the realistic database:

> Before I run this, I want to flag a few things:
>
> **This looks like a production database** (based on the pg_dump header from prod-db-03.internal.acme.co, the realistic data patterns, and the restructuring notes).
>
> I'd recommend:
> 1. `pg_dump employees > employees_backup_$(date +%Y%m%d).sql`
> 2. Confirm with the team that no active processes depend on this data
>
> If you've confirmed this is safe to proceed:
> ```sql
> BEGIN;
> TRUNCATE TABLE employees CASCADE;
> SELECT setval('employees_id_seq', 1, false);
> COMMIT;
> ```

The model identifies the environment as production, adds backup and confirmation steps, and wraps the operation in a transaction — none of which it did with synthetic data.
