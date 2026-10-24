# AI Help-Desk Ticket Triage

A Python tool that reads incoming IT support tickets and uses AI to **categorise** them, **set a priority**, **suggest a fix** and **draft a first reply**. It then checks the AI's work and flags anything a human should review before it goes out.

Built to show how a 1st line service desk could cut the time spent sorting the queue, without handing decisions over to AI blindly.

https://github.com/user-attachments/assets/32670a83-f153-48ae-92c4-78bdf7866704

<img width="2020" height="1388" alt="overview_1" src="https://github.com/user-attachments/assets/cc853af8-1d49-4f63-b820-eb236fdd2710" />

**Live demo:** [Requests (employee form)](https://YOURUSERNAME.pythonanywhere.com/requests) · [Admin login](https://YOURUSERNAME.pythonanywhere.com/admin)

**The results table in Excel** (most urgent first, with the issue and suggested fix side by side):

<img width="962" height="349" alt="Excel results table showing priority, category, issue, suggested fix and draft reply" src="https://github.com/user-attachments/assets/f8729873-058e-4fbd-921a-3e0f25e488e7" />

**Each answer checked against the expected answer** (green = right, red = wrong):

<img width="962" height="781" alt="Accuracy columns showing expected and actual answers" src="https://github.com/user-attachments/assets/0e4f9119-cfdd-43c7-9c36-28647dad4fc0" />

**A run in the terminal:**

<img width="837" height="452" alt="Terminal output showing accuracy results" src="https://github.com/user-attachments/assets/73b16626-ece9-4820-b46b-4a1aed959f9b" />
<img width="350" height="331" alt="Summary of tickets by priority and category" src="https://github.com/user-attachments/assets/9c49bf65-90a3-47ba-bf8a-9eac00e4b524" />

## Why I built it

I've spent six years in customer-facing roles and troubleshooting computers and devices in my own time. On a service desk, the first few minutes of every ticket go on reading it, working out what it is and how urgent it is, and acknowledging it. I wanted to see how much of that triage AI could take on, and where a person still needs to stay in control. So far, the AI is a useful first pass, but a person still needs to check its work, especially on priority.

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

## Admin web app (in progress)

A small web app where the service desk admin signs in to see the ticket queue, built with Flask (Python), HTML, CSS and a little JavaScript. It's branded as **Brightmoor IT Desk Portal**, a made-up company, so it looks like a real internal tool. The name is one setting at the top of `app.py`.

**Step 1, done: a secure sign-in page.** Security built in:

- **Passwords are never stored.** `set_password.py` saves only a salted hash, so even someone reading the settings file can't see the password.
- **Account lockout.** 5 wrong attempts locks sign-in for 5 minutes, like a real lockout policy.
- **CSRF protection.** Every form carries a secret token, so another website can't submit it on the admin's behalf.
- **Session safety.** The sign-in cookie can't be read by page scripts, the admin is signed out after 30 minutes without activity, and signed-in pages are never cached, so "Back" after signing out shows nothing.
- **Locked-down pages.** Security headers block the page being framed by other sites or loading scripts from elsewhere, and the app only listens on this computer.

Friendly touches: show/hide password, a Caps Lock warning, a "Signing in…" state and a live lockout countdown.

To run it:

```
pip install -r requirements.txt
python set_password.py     # once: choose the admin username and password
python app.py              # then open http://127.0.0.1:5000/admin
```

The employee form is at http://127.0.0.1:5000/requests.

**Step 2, done: the ticket queue.** Once signed in, the admin sees every ticket from the latest `triaged_tickets.xlsx`, most urgent first. It's read-only for now:

- Filter by priority (P1–P4) or show only tickets that need human review
- Search across ticket number, issue, category, name and message
- Sort by urgency, newest or oldest
- Click a ticket to see the suggested fix, draft reply, original message, the AI's confidence and reasoning, and whether it matched the expected answer

Ticket text is untrusted input, so it's always displayed as plain text and can never run as code in the page.

**Step 3, done: employees can report problems.** A **Requests** page (`/requests`) lets any employee send a ticket without signing in. As soon as it's sent:

1. The AI triages it (category, priority, issue summary, suggested fix and draft reply)
2. It's saved to a small SQLite database (`tickets.db`) with the next ticket number
3. The employee gets their ticket number straight away
4. Within 30 seconds, the admin's queue shows a "new ticket has arrived" message

Design choices:

- **No ticket is ever lost.** If the AI is unavailable, the ticket is still saved and flagged for a person to triage by hand.
- **A database instead of the Excel file.** Saving to Excel fails while the file is open, and two tickets arriving together could overwrite each other. SQLite comes with Python and handles both. The admin can still **Download as Excel** at any time.
- **Rate limited.** Each computer can send 5 tickets per 10 minutes, so nobody can flood the queue or use up the free AI quota.
- **Safe with untrusted text.** Tickets are stored using parameterised SQL (no SQL injection) and always displayed as plain text (no cross-site scripting).
- **The employee never sees the AI's draft reply.** It's for the analyst to check and send, so a person stays in control.
- **The 30-minute sign-out still works.** The queue's background check for new tickets doesn't count as admin activity.

When the app starts, it copies in any tickets from your latest `triaged_tickets.xlsx`, skipping ones it already has. `tickets.db` contains people's names and messages, so it's in `.gitignore` and never goes to GitHub.

**Step 4, done: completing, deleting and restoring tickets.** The queue has three lists: **Open**, **Completed** and **Deleted**.

- Open a ticket to **Mark as completed** or **Delete** it. Both show an **Undo** straight away.
- Completed tickets can be **reopened**; deleted tickets can be **restored** at any time from the Deleted list.
- Each list shows who completed or deleted a ticket and when, and **Download as Excel** exports the list you're looking at.

To clear tickets out for good, use **Delete permanently** on a ticket in the Deleted list, or **Empty the Deleted list**. Both show a confirmation page first, only work on tickets already in the Deleted list, and shrink `tickets.db` afterwards. A permanently deleted ticket's name, email and message are gone for good (useful for UK GDPR erasure requests). Only its ticket number is kept, so it isn't copied back in from Excel and the number is never reused.

Until then, nothing is wiped from the database ("soft delete"). That means every action can be undone, there's a record of who did what, ticket numbers are never reused, and a deleted ticket isn't copied back in from the Excel results when the app restarts. All actions are POST requests protected by the CSRF token, so a link or another website can't trigger them.

**Next step:** let employees email tickets in, using the same database and AI triage.

Flask's built-in server is only for running on your own computer. Online, PythonAnywhere runs the app behind its own web server with HTTPS (see below).

## Putting it online (free, on PythonAnywhere)

The portal runs online on a free PythonAnywhere account, at `https://YOURUSERNAME.pythonanywhere.com`:

| Address | Page |
|---|---|
| `/requests` | **Brightmoor IT Desk Portal - Requests**: the employee form (the home page goes here too) |
| `/admin` | **Brightmoor IT - Admin Login** |
| `/admin/tickets` | **Brightmoor IT Desk Portal - Admin Manager**: the ticket queue |

PythonAnywhere was chosen because its free plan keeps files between restarts (so `tickets.db` survives) and allows connections to the Groq API.

Extra protections switch on when `.env` contains `PUBLIC_SITE=1`:

- **HTTPS only:** the sign-in cookie is never sent over plain HTTP, and browsers are told to always use HTTPS (HSTS).
- **Real visitor addresses:** online, every request arrives through PythonAnywhere's load balancer. The app reads each visitor's real IP from the `X-Real-IP` header, so one person's failed logins can't lock everyone out.
- **Spam protection on the form:** a hidden spam-trap field, 5 tickets per visitor per 10 minutes, and a cap of 30 tickets an hour for the whole site, to protect the free AI quota.
- **A clear demo notice** on every page, so nobody mistakes Brightmoor IT for a real company or enters real personal data.

`pythonanywhere_wsgi.py` shows what goes in PythonAnywhere's WSGI configuration file. Free web apps must be renewed once a month from the Web tab.

## Ideas for version 2

- [ ] Read tickets straight from a Gmail inbox or a Google Form
- [ ] Write results to Google Sheets automatically
- [ ] Rebuild the same workflow in n8n (free, self-hosted) as a no-code version
- [ ] Implement a graphical user interface (GUI) so the system is more interactive and more visually appealing
- [ ] Suggest a knowledge-base article for common issues such as password resets and printers
- [ ] Compare accuracy across models (Groq vs Ollama vs Claude)

## Tech

Python · Flask · SQLite · HTML, CSS & JavaScript · OpenAI-compatible chat API · Groq (`openai/gpt-oss-20b`) or Ollama (`llama3.2`) · prompt engineering · JSON output validation · Excel output with openpyxl
