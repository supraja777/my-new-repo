import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# ==================================================
# ENV SETUP
# ==================================================
load_dotenv()

# ==================================================
# LLM CONFIG — CONTENT GENERATION ONLY
# ==================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.15
)

# ==================================================
# RESUME INPUT
# ==================================================
from resume import resume_content

# keep prompt safe
resume_content = resume_content[:6000]

# ==================================================
# LOAD LOCKED HTML TEMPLATE
# ==================================================
with open("index.html", "r", encoding="utf-8") as f:
    HTML_TEMPLATE = f.read()

# ==================================================
# RICH, STRICT PROMPT (TEXT ONLY)
# ==================================================
prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are a professional portfolio content generator.

Your job is to extract and infer HIGH-QUALITY portfolio content
from the given resume.

ABSOLUTE RULES (VIOLATION = FAILURE):
- DO NOT generate HTML
- DO NOT generate Markdown
- DO NOT add explanations
- DO NOT change field names
- ALL sections MUST be present
- Use confident, professional language
- If information is missing, infer reasonable defaults

Return content EXACTLY in the format below.
Do NOT add extra text.

================= OUTPUT FORMAT =================

NAME:
Full professional name

SHORT_NAME:
First name or initials (for navbar/logo)

TAGLINE:
Concise role + specialization (max 12 words)

ABOUT:
4–5 sentence professional summary highlighting expertise,
impact, and interests. Written in first person.

PROJECTS:
Project Title | 1–2 sentence description with tech + outcome
|| Project Title | 1–2 sentence description
|| Project Title | 1–2 sentence description

SOCIALS:
LinkedIn | https://...
|| GitHub | https://...
|| Portfolio | https://...

CONTACT_TEXT:
1–2 sentence call to action encouraging collaboration or contact

================= RESUME =================
{resume}
"""
)

raw_output = (prompt | llm).invoke({"resume": resume_content}).content.strip()

# ==================================================
# SAFE PARSER
# ==================================================
def extract(section: str) -> str:
    try:
        return raw_output.split(f"{section}:")[1].split("\n\n")[0].strip()
    except Exception:
        return ""

# ==================================================
# BUILD PROJECTS HTML
# ==================================================
projects_html = ""
for proj in extract("PROJECTS").split("||"):
    title, desc = [p.strip() for p in proj.split("|", 1)]
    projects_html += f"""
    <div class="project-box">
      <div class="project-caption">
        <h5>{title}</h5>
        <p>{desc}</p>
      </div>
    </div>
    """

# ==================================================
# BUILD SOCIAL LINKS HTML
# ==================================================
socials_html = ""
for soc in extract("SOCIALS").split("||"):
    label, url = [s.strip() for s in soc.split("|", 1)]
    socials_html += f"""
    <a href="{url}" target="_blank" rel="noopener">
      <img src="img/social_icons/{label.lower()}.svg" alt="{label}" />
    </a>
    """

# ==================================================
# INJECT CONTENT INTO TEMPLATE
# ==================================================
final_html = (
    HTML_TEMPLATE
    .replace("{{NAME}}", extract("NAME"))
    .replace("{{SHORT_NAME}}", extract("SHORT_NAME"))
    .replace("{{TAGLINE}}", extract("TAGLINE"))
    .replace("{{ABOUT}}", extract("ABOUT"))
    .replace("{{PROJECTS}}", projects_html)
    .replace("{{SOCIAL_LINKS}}", socials_html)
    .replace("{{CONTACT_TEXT}}", extract("CONTACT_TEXT"))
)

# ==================================================
# WRITE BACK TO index.html
# ==================================================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ SUCCESS: index.html updated with generated portfolio content")
