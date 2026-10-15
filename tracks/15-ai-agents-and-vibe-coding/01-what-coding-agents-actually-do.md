# What Coding Agents Actually Do

> Understand exactly how AI coding agents work — and why you don't need a CS degree to use them profitably.

**Track:** AI Agents & Vibe-Coding for Creators
**Time:** ~35 minutes
**Prerequisites:** None

## The Problem

Most creators hear "build your own tools" and immediately disengage — convinced that building software requires years of computer science education, knowledge of data structures, and the ability to read thousands of lines of foreign-looking code.

This belief was accurate before 2023. It is no longer accurate.

The barrier used to be: *you can't build what you can't write*. Coding agents like Claude Code, Cursor, and GitHub Copilot have inverted this: **you can now build anything you can clearly describe**. The agent writes, edits, debugs, and explains the code — you direct it.

If you don't understand the distinction between an AI image tool (where you type prompts into a UI) and an AI coding agent (where you describe a program and the agent builds it), you'll miss the most profitable skill shift of the current decade.

---

## The Concept

A **Coding Agent** is an AI that can read, write, run, and debug code files autonomously inside your project directory:

```
Your Plain-English Instruction ──► Agent Reads Existing Files ──► Agent Writes/Edits Code ──► Agent Runs & Tests ──► Working Program
```

### The 3 Key Distinctions (Agents vs. Chatbots vs. Scripts):

1. **AI Chatbots (ChatGPT, Claude.ai web):** You paste code in, it replies with suggestions in the chat window. You manually copy-paste changes back. No file access, no execution. Great for questions, slow for building.
2. **Coding Agents (Claude Code, Cursor, GitHub Copilot):** The agent operates *inside your file system*. It can open files, write new ones, run terminal commands, read error messages, and self-correct — completing multi-step programming tasks from a single instruction.
3. **Traditional Scripts (Python, Bash):** Pre-written code you run manually. Fast and cheap, but requires you to write and debug the code yourself, or hire a developer.

### What Agents Can Build for Creators:
* **Batch API runners** — Scripts that call muapi 50 times automatically, saving hours of manual clicking.
* **Metadata generators** — Tools that read a folder of images and auto-write CSV titles and keywords for stock platforms.
* **Prompt matrix expanders** — Generate 100 prompt variations from a 3-variable template in seconds.
* **Client intake automations** — Forms that receive selfies and auto-trigger a headshot generation pipeline.
* **Pricing calculators** — Interactive web tools your clients use to estimate their project cost.

---

## Do It

### Step 1: Install a Coding Agent
Choose one of the two most creator-accessible agents:
* **Claude Code** (Anthropic): Terminal-based agent. Install via `npm install -g @anthropic-ai/claude-code`. Runs inside any project folder.
* **Cursor** (cursor.sh): VS Code-based agent with a familiar visual code editor. Download the app, open a folder, and start chatting in the sidebar.

Open [`templates/vibe-coding-session-brief.md`](templates/vibe-coding-session-brief.md) to set up your first session.

### Step 2: Give the Agent a Single Clear Instruction
Open your project folder in the agent. Type one instruction:
> *"Create a Python script called `batch_prompt_runner.py` that reads a list of prompts from a file called `prompts.txt` (one prompt per line) and prints each one numbered."*

The agent will create the file, write the code, and confirm it works.

### Step 3: Run the Output
Execute the file the agent created:
```bash
python batch_prompt_runner.py
```
You will see your prompts printed, numbered. This is your first agent-built tool.

### Step 4: Iterate with Corrections
Tell the agent what to change in plain English:
> *"Now instead of printing, save the output to a file called `results.txt`."*

The agent edits the script automatically. You don't read the code — you just describe the change.

---

## Worked Example

**First Agent Session for "Niche Creator Alex"**

* **Background:** Alex runs an Etsy print-on-demand store. Every week she manually types 30 product titles into a spreadsheet.
* **Agent Instruction Given:** *"Write a Python script that reads a list of design names from `designs.txt` and generates 3 SEO-friendly Etsy product title variations for each design, saving all results to `etsy_titles.csv`."*
* **Time to Working Tool:** 8 minutes (including installing Claude Code).
* **Weekly Time Saved:** 2.5 hours of manual copywriting per week.
* **Value of Tool:** If sold on Gumroad at $19, this tool would pay back its creation time after the first 3 sales.

---

## Compare Tools

| Agent Platform | Interface Style | Best For | Monthly Cost |
|---|---|---|---|
| **Claude Code** | Terminal (command line) | Creators comfortable with a basic terminal | ~$20/mo (Anthropic API credits) |
| **Cursor** | Visual editor (like VS Code) | Creators who prefer a graphical interface | Free tier + $20/mo Pro |
| **GitHub Copilot** | In-editor autocomplete | Creators already using VS Code for other work | $10/mo |
| **Replit Agent** | Browser-based, zero install | Creators who want zero local setup | Free tier available |

---

## Launch It

**What you can sell after this lesson:**
* **Agent Setup Service:** Charge **$99–$199** to set up and configure Claude Code or Cursor for other creators who find the installation confusing. Many non-technical creators will pay to skip the terminal setup entirely.

---

## Exercises

1. **Easy:** Install Cursor or Claude Code and open a blank project folder. Ask the agent: *"Create a file called `hello.txt` containing the words 'My first agent output'."* Confirm the file was created.
2. **Medium:** Ask the agent to write a Python script that reads a text file of product names and outputs an all-caps version of each name into a new file.
3. **Hard:** Ask the agent to build a script that generates 5 Midjourney prompt variations from a single subject, aesthetic style, and camera angle — reading inputs from a CSV and writing outputs to a new CSV.

---

## Templates

* [`templates/vibe-coding-session-brief.md`](templates/vibe-coding-session-brief.md) — Agent instruction frameworks, session planning sheets, and first-tool prompt libraries.

---

[Track Overview](README.md) · Next: [Building Your First Sellable Micro-Tool →](02-building-your-first-sellable-micro-tool.md)
