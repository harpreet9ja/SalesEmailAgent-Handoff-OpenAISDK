# 🤖 AI Sales Email Agent

Multi-agent system that generates, evaluates, and sends cold emails using OpenAI Agents and SendGrid.

---

## 🚀 Features

- Generates multiple email drafts using different styles
- Selects the best email using a manager agent
- **Agent handoff workflow** for task delegation
- Formats email and generates subject line
- Sends email via SendGrid
- Fully automated end-to-end pipeline

---

## 🔄 Agent Workflow (Handoff)

- **Sales Manager Agent**
  - Orchestrates the process
  - Generates multiple drafts via agents
  - Selects the best email

- **Email Sender Agent (Handoff Target)**
  - Receives selected email via handoff
  - Formats email
  - Generates subject line
  - Sends final email

👉 Demonstrates structured **multi-agent coordination using handoffs**

---

## 🛠️ Tech Stack

- Python
- OpenAI Agents SDK
- SendGrid API
- asyncio

---

## ⚙️ Setup

```bash
git clone https://github.com/harpreet9ja/llm-profile-chatbot.git
cd llm-profile-chatbot
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```
OPENAI_API_KEY=your_key_here
SENDGRID_API_KEY=your_key_here
FROM_EMAIL=your_email
TO_EMAIL=recipient_email
```

---

## ▶️ Run

```bash
python app.py
```

---

## 📄 License

MIT
