# Prompt: fill in an incident runbook

Paste this into ChatGPT, Claude.ai, Gemini or a local model, then paste the contents of TEMPLATE.md and your incident notes below it.

---

You are helping me write a runbook for ONE recurring failure class of ONE service. Below this message I will paste a runbook template with [[PLACEHOLDER]] fields and my notes from past incidents.

Rules:
1. Fill only from my notes. If a command, signature or number is missing, leave the placeholder and list it under "Questions for you". Never invent them.
2. Keep the structure: (1) classify the incident before reading logs, (2) deploy-time failures, (3) runtime failures as a ranked list, (4) after identifying the cause, with separate escalation and closure criteria, (5) do not.
3. Rank failure signatures by how often each actually occurred in my notes, most frequent first.
4. Give every signature a caveat that starts "This is not evidence that ..." and names the wrong conclusion a tired responder would jump to, with the reason it does not follow.
5. In "Do not", list only remediations my notes show were tried and made things worse or wasted time.
6. Closure requires: fix deployed and independently verified, a regression test exists, incident recorded. Keep that wording.
7. Use plain words and short sentences. Do not add hostnames, secrets or personal data.

Output: the completed runbook in Markdown, then a short "Questions for you" list.

Optional second step: for the confirmed root cause, list the conditions that had to hold for the failure to happen, and propose one named static check per condition (script, thresholds, exit codes 0 pass / 1 fail / 2 input missing, plus a synthetic test).

--- TEMPLATE AND NOTES FOLLOW ---
