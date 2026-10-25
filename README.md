# AI Help-Desk Ticket Triage

A Python tool that reads incoming IT support tickets and uses AI to **categorise** them, **set a priority**, **suggest a fix** and **draft a first reply**. It then checks the AI's work and flags anything a human should review before it goes out.

Built to show how a 1st line service desk could cut the time spent sorting the queue, without handing decisions over to AI blindly.

**Live demo:** [Requests (employee form)](https://brightmooritdigitaldesk.pythonanywhere.com/requests) · [Admin login](https://brightmooritdigitaldesk.pythonanywhere.com/admin)

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
| Priority | P1 (critical) to P4 (low), colour-coded. The AI records the facts and fixed rules decide the priority (see below) |
| Category | One of 11 service desk categories (Password / Account Lockout, Access Request, Hardware, Mobile Device, …) |
| Issue | A one-line summary of the problem |
| Suggested fix | 2–4 numbered steps for the 1st line analyst, including when to escalate |
| Draft reply | A friendly first response to the user, ready for an analyst to check and send |
| Human review? | **Yes** (highlighted) if a person should check it before anything is sent, plus the reason |
| AI confidence | How sure the AI is |

A **Summary** sheet shows totals by priority and category. If the input file includes the "right answers" (`expected_category`, `expected_priority`), the AI's accuracy is scored and each answer is marked right (green) or wrong (red).

## Results

Tested on 50 hand-labelled tickets (`test_tickets_50.csv`), the same set before and after each change:

| | Before | After the facts + rules change |
|---|---|---|
| Category accuracy | 90% | 92% |
| Priority accuracy | 76% | **86%** |
| Priority too low (not urgent enough) | 10 | **2** |
| Priority too high (more urgent than needed) | 2 | 5 |

The AI was good at working out what a ticket was about but too relaxed about urgency, which is the dangerous direction on a service desk. For example, someone who had typed their password into a fake login page was marked P2 instead of P1. Letting the AI record the facts and fixed rules decide the priority cut "too low" mistakes by 80%. The trade-off is a few more tickets marked more urgent than needed, which is the safer way to be wrong.

(An earlier version scored 88% on category and 53% on priority across the original 17 sample tickets.)

## Design decisions

- **The AI gathers the facts; rules decide the priority.** The AI was good at understanding tickets but too relaxed about urgency. Now it records the facts (how many people are affected, whether they can work, any deadline, any security risk) and `decide_priority()` turns them into P1–P4 using the ITIL impact × urgency approach. Every priority can be explained, and if the AI itself thought a ticket was more urgent than the rules did, it's flagged for a person.
- **Corrections are visible and measured.** The admin queue marks every ticket where the rules changed the AI's own priority (↑ raised or ↓ lowered), with a "Corrected by rules" filter. `triage.py` reports how many corrections fixed a mistake or caused one, and how the AI would have scored on its own.
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
   python triage.py               # the 50-ticket test set (test_tickets_50.csv)
   ```

**Option B – Ollama (free, runs on your own computer)**
1. Install Ollama from [ollama.com](https://ollama.com).
2. In a terminal, run `ollama pull llama3.2`.
3. In `.env`, set `AI_PROVIDER=ollama`.
4. Run `python triage.py`.

> On Mac, use `python3` instead of `python`.

Results are saved to a dated file such as `test_results_2026-10-25_0916.xlsx` and open automatically, so every run is kept and you can compare accuracy before and after a change. Add `--no-open` to skip opening it, or `-o results.csv` to save a CSV instead. The summary shows category and priority accuracy, and whether wrong priorities were too low (not urgent enough) or too high.

To load the original sample tickets into the web app's queue, run `python triage.py sample_tickets.csv -o triaged_tickets.xlsx`.

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
- **Usernames ignore capitals, passwords don't.** "Admin" and "admin" are the same user, like Windows and Active Directory logins, but the password must match exactly.
- **CSRF protection.** Every form carries a secret token, so another website can't submit it on the admin's behalf.
- **Session safety.** The sign-in cookie can't be read by page scripts, the admin is signed out after 30 minutes without activity, when the browser closes or if an admin page is reloaded, and signed-in pages are never cached, so "Back" after signing out shows nothing.
- **The admin page always asks for the password.** Opening `/admin` (for example from the link on the request form) signs out any existing session first, so nobody can get into the queue from a computer the admin left signed in.
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

**Step 5, done: SLA timers.** Every ticket gets a "resolve by" time from its priority, like the service level agreements real service desks work to:

| Priority | Resolve within |
|---|---|
| P1 Critical | 4 hours |
| P2 High | 8 hours |
| P3 Medium | 3 days |
| P4 Low | 5 days |

- Each open ticket shows how long is left ("Due in 2h 15m"). It turns **amber** when under a quarter of the time is left and **red** once it's overdue ("Overdue by 40m").
- The timers count down live while the page is open, without reloading.
- An **At risk or overdue** filter and a **Due soonest first** sort show what needs doing next. A P3 due in an hour can matter more than a P2 due tomorrow.
- Completed tickets record whether they **met** or **missed** their target, and how long they took. The Completed list has a **Missed target** filter.

The targets live in one place (`SLA_HOURS` in `sla.py`). They count clock time, 24 hours a day; a real desk would usually pause the clock for P3 and P4 outside working hours.

**Next step:** let employees email tickets in, using the same database and AI triage.

Flask's built-in server is only for running on your own computer. Online, PythonAnywhere runs the app behind its own web server with HTTPS (see below).

## Putting it online (free, on PythonAnywhere)

The portal runs online on a free PythonAnywhere account, at `https://brightmooritdigitaldesk.pythonanywhere.com`:

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

## Tests

Automated tests run on GitHub every time the code changes (GitHub Actions):

- `test_priority.py` checks each priority rule, e.g. a whole team that can't work is P1, and a problem with a workaround is P3.
- `test_corrections.py` gives the checking code made-up AI answers that are wrong, and confirms the rules correct them: a phishing ticket the AI marked P2 is raised to P1, and an "URGENT!!!" sticky key it marked P2 is lowered to P4 and flagged for a person.
- `test_sla.py` checks the SLA timers with a fixed "now": a P1 with 30 minutes left is at risk, one 45 minutes past its target is overdue, and a completed ticket met or missed its target.

No real AI is called, so the tests are free and take seconds. To run them yourself: `pip install pytest`, then `python -m pytest -v`.

## Ideas for version 2

- [ ] Read tickets straight from a Gmail inbox or a Google Form
- [ ] Write results to Google Sheets automatically
- [ ] Rebuild the same workflow in n8n (free, self-hosted) as a no-code version
- [ ] Implement a graphical user interface (GUI) so the system is more interactive and more visually appealing
- [ ] Suggest a knowledge-base article for common issues such as password resets and printers
- [ ] Compare accuracy across models (Groq vs Ollama vs Claude)

## Tech

Python · Flask · SQLite · HTML, CSS & JavaScript · OpenAI-compatible chat API · Groq (`openai/gpt-oss-20b`) or Ollama (`llama3.2`) · prompt engineering · JSON output validation · Excel output with openpyxl
