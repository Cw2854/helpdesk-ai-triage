# AI Help-Desk Ticket Triage

A Python tool that reads incoming IT support tickets and uses AI to **categorise** them, **set a priority**, and **draft a first reply**. It then checks the AI's work and flags anything a human should review before it goes out.

Built to show how a 1st line service desk could cut the time spent sorting the queue, without handing decisions over to AI blindly.

<img width="837" height="452" alt="image" src="https://github.com/user-attachments/assets/73b16626-ece9-4820-b46b-4a1aed959f9b" />
<img width="962" height="349" alt="image" src="https://github.com/user-attachments/assets/f8729873-058e-4fbd-921a-3e0f25e488e7" />
<img width="350" height="331" alt="image" src="https://github.com/user-attachments/assets/9c49bf65-90a3-47ba-bf8a-9eac00e4b524" />
<img width="962" height="781" alt="image" src="https://github.com/user-attachments/assets/0e4f9119-cfdd-43c7-9c36-28647dad4fc0" />





## Why I built it

I've spent six years in customer-facing roles and troubleshoot computers and devices in my own time. On a service desk, the first few minutes of every ticket go on reading it, working out what it is and how urgent it is, and acknowledging it. I wanted to see how much of that triage AI could take on, and where a person still needs to stay in control. In short the AI is not perfect but the need for human assistance is paramount in order to increase accuracy and to obtain true results going forward. 

## What it does

```
tickets.csv ──► AI model ──► validation & safety checks ──► triaged_tickets.csv
               (category,      (is the category real?        (open in Excel or
                priority,       is the priority valid?        Google Sheets)
                draft reply)    confident enough?
                                P1 or security? → human)
```

For every ticket it records:

| Column | What it means |
|---|---|
| `category` | One of 10 service desk categories (Password / Account Lockout, Access Request, Hardware, …) |
| `priority` | P1 (critical) to P4 (low), using rules written into the prompt |
| `confidence` | How sure the AI is (0–1) |
| `needs_human_review` | **Yes** if the ticket needs a person to check it before anything is sent |
| `review_reason` | Why it was flagged |
| `draft_reply` | A friendly first response, ready for an analyst to check and send |

If the input file includes the "right answers" (`expected_category`, `expected_priority`), it also scores the AI's accuracy.

## Results

On 16 test tickets, the model got the category right 88% of the time and the priority right 53% of the time. It flagged 5 tickets for human review, including the phishing incident and the vague 'not working again' ticket."

## Design decisions

- **Human in the loop.** P1s, security incidents and anything below 70% confidence are always flagged for a person to check. The AI drafts and a human decides.
- **Never trust the AI's output blindly.** Every answer is checked: the category must come from the approved list, the priority must be P1–P4, and replies that ask for a password are flagged.
- **Prompt-injection aware.** Ticket text is treated as data, not instructions. Sample ticket INC-1015 deliberately tries to trick the AI into marking a sticky mouse wheel as P1.
- **Privacy option.** It can run entirely on a local model with Ollama, so ticket data (which often contains personal information) never leaves the machine. That matters under UK GDPR.
- **Swappable AI provider.** It works with any OpenAI-compatible API, so moving to Claude, GPT or Gemini only means changing a setting.
- **Keeps going on failure.** If one ticket errors, it's logged and flagged, and the rest still get processed.

## How to run it (free)

You need **Python 3.9+**. No extra packages are required.

**Option A – Groq (free cloud API, no card needed)**
1. Sign up at [console.groq.com](https://console.groq.com) and create an API key.
2. Copy `.env.example`, rename the copy to `.env`, and paste your key into `AI_API_KEY`.
3. Run:
   ```
   python triage.py --limit 3     # quick test on 3 tickets
   python triage.py               # all sample tickets
   ```

**Option B – Ollama (free, runs on your own computer)**
1. Install Ollama from [ollama.com](https://ollama.com).
2. In a terminal, run `ollama pull llama3.2`.
3. In `.env`, set `AI_PROVIDER=ollama`.
4. Run `python triage.py`.

> On Mac, use `python3` instead of `python`.

Results are saved to `triaged_tickets.csv`. To view them in Google Sheets, use **File → Import → Upload**.

## Using your own tickets

Create a CSV with these columns: `ticket_id, received, from_name, from_email, subject, body`. Then run:

```
python triage.py my_tickets.csv -o my_results.csv
```

Only use made-up or anonymised data. Never use real people's tickets.

## Ideas for version 2

- [ ] Read tickets straight from a Gmail inbox or a Google Form
- [ ] Write results to Google Sheets automatically
- [ ] Rebuild the same workflow in n8n (free, self-hosted) as a no-code version
- [ ] implementing a graphical user interface (GUI) whereby the system is more interactive, and more aesthetically pleasing. 
- [ ] Suggest a knowledge-base article for common issues such as password resets and printers
- [ ] Compare accuracy across models (Groq vs Ollama vs Claude)

## Tech

Python (standard library only) · OpenAI-compatible chat API · Groq (`openai/gpt-oss-20b`) or Ollama (`llama3.2`) · prompt engineering · JSON output validation · CSV / Google Sheets

