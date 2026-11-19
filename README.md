# Email Triage Agent

Classifies each email in my Gmail into one category, with a written spec and a measured evaluation.

Categories: `MUST_SEE`, `IMPORTANT`, `LOW_PRIORITY`, `TRASH`, `UNSURE`.
Read-only: it never deletes, moves, or sends mail (v1 only reads via `gmail.readonly`).

## How it works
- `docs/categories.md` is the source of truth: category definitions, numbered rules, and a rulings table. It is loaded into the system prompt.
- `classifier.py` sends one email at a time to the Anthropic Messages API and expects a JSON object (`category`, `reason`). Output is validated with Pydantic. Truncation (`max_tokens`) or invalid output falls back to `UNSURE` and is counted separately.
- Email content is untrusted. It is wrapped in `<email>` tags, tag-closing text is neutralized, and the spec tells the model to ignore instructions found inside emails.
- Optional: `retrieval.py` adds the 5 most similar labeled emails (TF-IDF cosine similarity) as examples. It was evaluated and is not enabled by default.

## Dashboard (in progress)
A local web dashboard groups emails by category: Must see, Important, Unsure, Low priority, Trash. It has a sidebar with counts, search, and expandable rows showing the model's reason and a link to open the message in Gmail.

- Backend: FastAPI (`api.py`, `dashboard_data.py`), bound to `127.0.0.1`.
- Front end: React + TypeScript + Vite (`frontend/`). Email content is rendered as plain text only, because subjects, bodies and the model's reason are untrusted.
- **Current limitation:** it displays saved emails and saved model results from `data/`. It does not fetch or classify new mail yet.

## Evaluation
- 30 synthetic emails (`evals/fake_emails.json`) cover hard cases: phishing, injected instructions, garbled mail.
- 340 real emails from my inbox, labeled by me: a dev set (130) used while building, a first held-out set (70), a second held-out sample (100), and 40 emails from Gmail's Primary tab. Real mail is not in the repo.
- Method: dev/held-out split fixed at fetch time, held-out run once per design, noise floor measured by repeating runs (about 2 emails of 130).

### Results (model: claude-opus-5-5)
| Set | Baseline | With retrieval | Always-TRASH |
|---|---|---|---|
| Dev (130), leave-one-out | 118-120 | 126 | n/a |
| Held-out v1 (70), before policy changes | 58 | 61 | 59 |
| Held-out v2 (100), after policy clarification* | 94 | 96 | 94 |

\*Not a clean held-out result: I changed the policy after seeing earlier errors on this set.

What I can say:
- Across about 134 fresh emails, nothing worth keeping was sent to TRASH.
- About 1-6% of junk was surfaced as important (false alarms).
- Retrieval gave no difference beyond the noise floor. The simpler baseline is the default.

What I cannot say:
- Accuracy is misleading: about 92% of my mail is junk, so always answering `TRASH` ties the model.
- Recall on important mail is unmeasured. My samples contained almost no real `IMPORTANT` or `MUST_SEE` mail.

### What I learned
- Most gains came from aligning the spec with my real policy, not from changing the model or prompt.
- My own labels drifted over time. The same sender groups were labeled differently across sessions, which means label noise limits any score.
- Dev scores overstated held-out performance.

## Run
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_eval.py                          # synthetic set
python run_real_eval.py --split heldout2    # needs your own data/
```
Needs `ANTHROPIC_API_KEY` in `.env` and Gmail OAuth credentials in `secrets/` (not included).

Dashboard (needs Node 20 or newer and your own `data/` folder):
```
uvicorn api:app --host 127.0.0.1 --port 8000     # terminal 1, project root
cd frontend && npm install && npm run dev          # terminal 2, open http://localhost:5173
```

## Limitations
- Single labeler (me), single inbox, junk-heavy sample.
- Gmail OAuth is in testing mode; tokens expire about weekly.
- `reason` text can quote attacker-controlled content, so render it as plain text.

## Next
Fetch and classify new mail with a per-message cache and a cost cap, a cheaper-model comparison, a mocked-model test suite, an injection test set, and a "mark as wrong" button that feeds corrections back into the eval labels.
