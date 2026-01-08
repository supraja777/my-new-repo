import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# ==================================================
# ENV
# ==================================================
load_dotenv()

# ==================================================
# LLM CONFIG
# ==================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)

# ==================================================
# RESUME
# ==================================================
from resume import resume_content
resume_content = resume_content[:6000]

# ==================================================
# HTML TEMPLATE (LOCKED STRUCTURE)
# ==================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{{NAME}}</title>

  <link rel="stylesheet" href="css/main.css"/>
  <link rel="stylesheet" href="css/media.css"/>

  <link rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css"/>

</head>

<body>

<header class="header">
  <div class="container container-lg">
    <div class="header-nav">
      <a href="#home" class="logo">{{SHORT_NAME}}</a>
      <nav class="nav">
        <ul class="nav-list">
          <li><a href="#home" class="nav-link active">Home</a></li>
          <li><a href="#about" class="nav-link">About</a></li>
          <li><a href="#projects" class="nav-link">Works</a></li>
          <li><a href="#contact" class="nav-link">Contact</a></li>
        </ul>
      </nav>
    </div>
  </div>
</header>

<section id="home" class="hero">
  <div class="container container-lg hero-row">
    <div class="hero-content">
      <span class="hero-greeting">Hello, I am</span>
      <h1 class="hero-heading">{{NAME}}</h1>
      <span class="hero-heading-subtitle">{{TAGLINE}}</span>

      <div class="social-links-row">
        {{SOCIAL_LINKS}}
      </div>

      <div>
        <a href="#projects" class="btn">My Work</a>
        <a href="#contact" class="btn btn-white">Contact Me</a>
      </div>
    </div>

    <div class="hero-img">
      <img src="formal.jpg" alt="{{NAME}}">
    </div>
  </div>
</section>

<section id="about" class="about">
  <div class="container">
    <h2 class="title">About Me</h2>
    <p class="about-descr">
      {{ABOUT}}
    </p>
  </div>
</section>

<section id="projects" class="projects">
  <div class="container container-lg">
    <h2 class="title">Works</h2>
    <div class="projects-row">
      {{PROJECTS}}
    </div>
  </div>
</section>

<section id="contact" class="contact">
  <div class="container">
    <h2 class="title">Contact</h2>
    <p>{{CONTACT_TEXT}}</p>

    <div class="social-links-row">
      {{SOCIAL_LINKS}}
    </div>
  </div>
</section>

<footer class="footer">
  <p>© 2026 {{NAME}}</p>
</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js"></script>
<script>AOS.init();</script>
</body>
</html>
"""

# ==================================================
# PROMPT — FIXED (MANDATORY OUTPUT)
# ==================================================
prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are generating portfolio website content.

You MUST return ALL sections below.
If information is missing, intelligently infer professional content.
DO NOT leave any section empty.

Return EXACTLY in this format:

NAME:
<full name>

SHORT_NAME:
<initials or first name>

TAGLINE:
<role + specialization>

ABOUT:
<professional summary paragraph>

PROJECTS:
<project title | short description> || <project title | short description> || <project title | short description>

SOCIALS:
<label | url> || <label | url> || <label | url>

CONTACT_TEXT:
<1–2 lines encouraging contact>

Resume:
{resume}
"""
)

raw = (prompt | llm).invoke({"resume": resume_content}).content

# ==================================================
# PARSER (SAFE)
# ==================================================
def get(label):
    try:
        return raw.split(f"{label}:")[1].split("\n\n")[0].strip()
    except:
        return ""

# ==================================================
# BUILD SECTIONS
# ==================================================
projects_html = "".join(
    f"""
    <div class="project-box">
      <div class="project-caption">
        <h5>{p.split('|')[0].strip()}</h5>
        <p>{p.split('|')[1].strip()}</p>
      </div>
    </div>
    """
    for p in get("PROJECTS").split("||")
)

socials_html = "".join(
    f"""
    <a href="{s.split('|')[1].strip()}" target="_blank">
      <span>{s.split('|')[0].strip()}</span>
    </a>
    """
    for s in get("SOCIALS").split("||")
)

# ==================================================
# FILL TEMPLATE
# ==================================================
final_html = (
    HTML_TEMPLATE
    .replace("{{NAME}}", get("NAME"))
    .replace("{{SHORT_NAME}}", get("SHORT_NAME"))
    .replace("{{TAGLINE}}", get("TAGLINE"))
    .replace("{{ABOUT}}", get("ABOUT"))
    .replace("{{PROJECTS}}", projects_html)
    .replace("{{SOCIAL_LINKS}}", socials_html)
    .replace("{{CONTACT_TEXT}}", get("CONTACT_TEXT"))
)

# ==================================================
# WRITE FILE
# ==================================================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("✅ index.html generated with ALL sections")
