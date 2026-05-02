from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
import os
from openai import OpenAI
from openai.types.responses import ResponseTextDeltaEvent
import sendgrid
from sendgrid.helpers.mail import Mail,Email,To,Content
import asyncio

load_dotenv(override=True)
api_key=os.getenv("SENDGRID_API_KEY")

Client_OpenAI = OpenAI()

instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."

instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three email_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use the handoff  agent  to send the best email (and only the best email) to the user.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
"""

emailsender_instruction = """You are an Email Orchestrator Agent.

Your job is to prepare and send a high-quality email by coordinating with other agents (tools).

Available tools:
1. emailformatter_agent → formats raw email body into a professional, structured email
2. emailSubjectFinder_agent → generates a subject line based on the email body
3. send_email → sends the final email

Workflow (STRICT — must follow in order):

Step 1: Format Email
- Use emailformatter_agent with the raw email body
- Get a clean, professional version of the email

Step 2: Generate Subject
- Use emailSubjectFinder_agent with the formatted email
- Generate a concise, relevant subject line

Step 3: Send Email
- Use send_email tool with:
  - email_content = formatted email
  - subject = generated subject

Rules:
- ALWAYS use the tools — do not manually format or write subject yourself
- Execute steps in sequence (format → subject → send)
- Call send_email ONLY once
- Do not skip any step
- Do not modify tool outputs unnecessarily
- Ensure the final email is professional and clean

Output:
- Do not return intermediate drafts
- Final output should confirm email sent successfully

Goal:
Ensure every email is well-formatted, has a strong subject, and is sent correctly using tools."""

instruction_emailformating = """You are an Email Formatting Agent.

Your task is to transform a plain text email into a well-structured, professional, and visually appealing rich email format.

Instructions:
- Preserve the original meaning and content. Do NOT add new information.
- Improve readability and structure.
- Format the email using:
  - Proper paragraphs
  - Bullet points where appropriate
  - Clear greeting and closing
  - Logical spacing
- Enhance tone slightly to make it professional and polished.
- Fix grammar and sentence flow if needed.
- Highlight key points using formatting (bold, line breaks, sections).
- Ensure the output is suitable for sending as a professional email.

Output format:
- Return only the formatted email body
- Use clean formatting (plain text with spacing OR HTML if specified)

Additionally:
- Format output in clean HTML
- Use <p>, <ul>, <li>, <strong>, <br> tags
- Avoid excessive styling (no inline CSS unless needed)

Constraints:
- Do not change intent or facts
- Do not make the email longer unnecessarily
- Keep it concise but refined

If input is already well formatted, lightly refine instead of rewriting.

Goal:
Make the email clear, professional, and easy to read."""

instruction_emailsubject = """You are an Email Subject Line Generator.

Your task is to generate a concise, compelling, and relevant subject line based on the provided email body.

Instructions:
- Read the email body carefully and understand its intent.
- Generate a subject line that reflects the core message.
- Keep it short and impactful (ideally 5–10 words).
- Make it engaging and likely to be opened.
- Maintain a professional tone (unless the email is clearly informal).
- Avoid spammy words (e.g., "FREE", "URGENT", excessive punctuation).
- Do not include emojis unless explicitly appropriate.
- Do not mislead — subject must match the content.

Output format:
- Return ONLY the subject line
- No quotes, no extra text

Optional styles (adapt based on email tone):
- Professional: clear and direct
- Sales: benefit-driven, curiosity-based
- Follow-up: polite and contextual
- Informational: descriptive and neutral

Goal:
Maximize clarity and open-rate while staying truthful to the email content."""


# three cold email generation agents
email_agent1 = Agent(name="Email_Agent1",instructions=instructions1,model="gpt-4o-mini")
email_agent2 = Agent(name="Email_Agent2",instructions=instructions2,model="gpt-4o-mini")
email_agent3 = Agent(name="Email_Agent3",instructions=instructions3,model="gpt-4o-mini")




emailformatter_agent = Agent(name="Email_Formatter", instructions=instruction_emailformating, model="gpt-4o-mini")
emailSubjectFinder_agent = Agent(name="Email_Subject_Finder", instructions=instruction_emailsubject, model="gpt-4o-mini")

tool1 = emailformatter_agent.as_tool(tool_name="emailformatter",tool_description="Formats raw email body into a professional, structured email. Input: raw email body. Output: formatted email body.")
tool2 = emailSubjectFinder_agent.as_tool(tool_name="emailSubjectFinder",tool_description="Generates a subject line based on the email body. Input:  email body. Output: concise, relevant subject line."    )


@function_tool
def send_email(email_content:str, subject:str):
    sg = sendgrid.SendGridAPIClient(api_key)
    email = Mail(
        from_email=os.getenv("FROM_EMAIL"),
        to_emails=os.getenv("TO_EMAIL"),
        subject=subject,
        html_content=email_content
    )
    response = sg.send(email)
    print("Email sent with status code:", response.status_code)
    print("Email body:", email_content)
    print("Email subject headers:", subject)
    return response

emailsender_agent = Agent(name="Email_Sender", instructions=emailsender_instruction, model="gpt-4o-mini",tools=[tool1,tool2,send_email])

sales_manager = Agent(name="Sales_Manager", instructions=instructions, model="gpt-4o-mini",handoffs=[emailsender_agent])

async def main():
    response = await Runner.run(sales_manager,input="Generate best cold email for a potential client and send it")
    print("Final Response:", response)
    
    
asyncio.run(main())

