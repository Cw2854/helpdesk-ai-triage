# AI Help-Desk Ticket Triage

A Python tool that reads incoming IT support tickets and uses AI to **categorise** them, **set a priority**, **suggest a fix** and **draft a first reply**. It then checks the AI's work and flags anything a human should review before it goes out.

Built to show how a 1st line service desk could cut the time spent sorting the queue, without handing decisions over to AI blindly.

**The results table in Excel** (most urgent first, with the issue and suggested fix side by side):

<img width="962" height="349" alt="Excel results table showing priority, category, issue, suggested fix and draft reply" src="https://github.com/user-attachments/assets/f8729873-058e-4fbd-921a-3e0f25e488e7" />

**Each answer checked against the expected answer** (green = right, red = wrong):

<img width="962" height="781" alt="Accuracy columns showing expected and actual answers" src="https://github.com/user-attachments/assets/0e4f9119-cfdd-43c7-9c36-28647dad4fc0" />

**A run in the terminal:**

<img width="837" height="452" alt="Terminal output showing accuracy results" src="https://github.com/user-attachments/assets/73b16626-ece9-4820-b46b-4a1aed959f9b" />
<img width="350" height="331" alt="Summary of tickets by priority and category" src="https://github.com/user-attachments/assets/9c49bf65-90a3-47ba-bf8a-9eac00e4b524" />

## Why I built it

I've spent six years in customer-facing roles and troubleshoot computers and devices in my own time. On a service desk, the first few minutes of every ticket go on reading it, working out what it is and how urgent it is, and acknowledging it. I wanted to see how much of that triage AI could take on, and where a person still needs to stay in control. In short the AI is not perfect but the need for human assistance is paramount in order to increase accuracy and to obtain true results going forward.

## What it does

```
tickets.csv ──► AI model ──► validation & safety checks ──► triaged_tickets.xlsx
               (issue, category,  (is the category real?      (colour-coded Excel
                priority, fix,     is the priority valid?       table, opens
                draft reply)       confident enough?            automatically)
                                   P1 or security? → human)
```

The results open in Excel as a formatted table, sorted with the most urgent tickets first:

| Column | What it means |
|---|---|
| Priority | P1 (critical) to P4 (low), colour-coded, using rules written into the prompt |
| Category | One of 11 service desk categories (Password / Account Lockout, Access Request, Hardware, Mobile Device, …) |
| Issue | A one-line summary of the problem |
| Suggested fix | 2–4 numbered steps for the 1st line analyst, including when to escalate |
| Draft reply | A friendly first response to the user, ready for an analyst to check and send |
| Human review? | **Yes** (highlighted) if a person should check it before anything is sent, plus the reason |
| AI confidence | How sure the AI is |

A **Summary** sheet shows totals by priority and category. If the input file includes the "right answers" (`expected_category`, `expected_priority`), the AI's accuracy is scored and each answer is marked right (green) or wrong (red).

## Results

On 17 test tickets, the model got the category right 88% of the time and the priority right 53% of the time. It flagged 5 tickets for human review, including the phishing incident and the vague 'not working again' ticket.

## Design decisions

- **Human in the loop.** P1s, security incidents and anything below 70% confidence are always flagged for a person to check. The AI drafts and a human decides.
- **Never trust the AI's output blindly.** Every answer is checked: the category must come from the approved list, the priority must be P1–P4, and replies that ask for a password are flagged.
- **Prompt-injection aware.** Ticket text is treated as data, not instructions. Sample ticket INC-1015 deliberately tries to trick the AI into marking a sticky mouse wheel as P1.
- **Privacy option.** It can run entirely on a local model with Ollama, so ticket data (which often contains personal information) never leaves the machine. That matters under UK GDPR.
- **Swappable AI provider.** It works with any OpenAI-compatible API, so moving to Claude, GPT or Gemini only means changing a setting.
- **Keeps going on failure.** If one ticket errors, it's logged and flagged, and the rest still get processed.
- **Spreadsheet-safe.** Ticket text that starts with `=` is stored as plain text, so a malicious ticket can't sneak a formula into the Excel file.

## How to run it (free)

You need **Python 3.9+**, plus one free package for the Excel output:

```
pip install -r requirements.txt
```

(Without it, the script still works and saves a CSV instead.)

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

Results are saved to `triaged_tickets.xlsx` and open automatically. Add `--no-open` to skip that, or `-o results.csv` to save a CSV instead.

## Using your own tickets

Create a CSV with these columns: `ticket_id, received, from_name, from_email, subject, body`. Then run:

```
python triage.py my_tickets.csv -o my_results.xlsx
```

Only use made-up or anonymised data. Never use real people's tickets.

## Ideas for version 2

- [ ] Read tickets straight from a Gmail inbox or a Google Form
- [ ] Write results to Google Sheets automatically
- [ ] Rebuild the same workflow in n8n (free, self-hosted) as a no-code version
- [ ] Implement a graphical user interface (GUI) so the system is more interactive and more visually appealing
- [ ] Suggest a knowledge-base article for common issues such as password resets and printers
- [ ] Compare accuracy across models (Groq vs Ollama vs Claude)

## Tech

Python · OpenAI-compatible chat API · Groq (`openai/gpt-oss-20b`) or Ollama (`llama3.2`) · prompt engineering · JSON output validation · Excel output with openpyxl
