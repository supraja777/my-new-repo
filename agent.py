import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# ==================================================
# ENV
# ==================================================
load_dotenv()

# ==================================================
# LLM CONFIG (TEXT ONLY)
# ==================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.15
)

# ==================================================
# RESUME INPUT
# ==================================================
from resume import resume_content
resume_content = resume_content[:6000]

# ==================================================
# LOAD HTML TEMPLATE (LOCKED STRUCTURE)
# ==================================================
with open("index.html", "r", encoding="utf-8") as f:
    HTML_TEMPLATE = f.read()

# ==================================================
# STRICT PROMPT — DATA ONLY
# ==================================================
prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are generating CONTENT ONLY for a personal portfolio website.

STRICT RULES:
- DO NOT output HTML
- DO NOT output Markdown
- DO NOT explain anything
- ALL fields are REQUIRED
- Professional, confident tone
- If missing info, infer reasonable defaults

Return EXACTLY this format:

NAME:
<Full professional name>

SHORT_NAME:
<Short name or initials>

TAGLINE:
<Concise role + specialization>

ABOUT:
<4–5 sentence first-person professional summary>

PROJECTS:
<Project title | short description>
|| <Project title | short description>
|| <Project title | short description>

SOCIALS:
<GitHub | https://...>
|| <LinkedIn | https://...>
|| <Twitter | https://...>

CONTACT_TEXT:
<1–2 sentence call to action>

Resume:
{resume}
"""
)

raw = (prompt | llm).invoke({"resume": resume_content}).content.strip()

# ==================================================
# SAFE PARSER
# ==================================================
def extract(label):
    try:
        return raw.split(f"{label}:")[1].split("\n\n")[0].strip()
    except Exception:
        return ""

# ==================================================
# BUILD PROJECTS HTML (MATCHES TEMPLATE)
# ==================================================
projects_html = ""
for p in extract("PROJECTS").split("||"):
    title, desc = [x.strip() for x in p.split("|", 1)]
    projects_html += f"""
    <div class="project-box" data-aos="fade-zoom-in" data-aos-duration="1000">
      <a href="#!">
        <img class="project-img" src="img/works/01.jpg" alt="{title}" />
        <div class="project-mask">
          <div class="project-caption">
            <h5 class="white">{title}</h5>
            <p class="white">{desc}</p>
          </div>
        </div>
      </a>
    </div>
    """

# ==================================================
# BUILD SOCIAL LINKS HTML
# ==================================================
socials_html = ""
for s in extract("SOCIALS").split("||"):
    label, url = [x.strip() for x in s.split("|", 1)]
    icon = label.lower()
    socials_html += f"""
    <a href="{url}" target="_blank" rel="noopener">
      <img src="img/social_icons/{icon}.svg" alt="{label}" />
    </a>
    """

# ==================================================
# FINAL HTML ASSEMBLY
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
# WRITE FILE
# ==================================================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ index.html updated successfully with generated content")
