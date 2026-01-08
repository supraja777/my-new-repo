import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# ==================================================
# ENV
# ==================================================
load_dotenv()

# ==================================================
# LLM CONFIG (CONTENT ONLY)
# ==================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)

# ==================================================
# RESUME INPUT
# ==================================================
from resume import resume_content
resume_content = resume_content[:6000]

# ==================================================
# LOCKED HTML — DO NOT MODIFY
# ==================================================
HTML_SKELETON = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{NAME}}</title>

  <link rel="stylesheet" href="css/main.css" />
  <link rel="stylesheet" href="css/media.css" />
  <link rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css"/>

</head>
<body>

<header id="header" class="header">
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
        <a href="#projects" class="btn">My Portfolio</a>
        <a href="#contact" class="btn btn-white">Contact Me</a>
      </div>
    </div>

    <div class="hero-img">
      <img src="formal.jpg" alt="{{NAME}}" />
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
# STRICT PROMPT — TEXT ONLY (NO HTML)
# ==================================================
prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are extracting portfolio CONTENT ONLY.

CRITICAL RULES:
- DO NOT output HTML
- DO NOT output Markdown
- DO NOT change field names
- ALL fields are REQUIRED
- If info is missing, infer professional defaults

Return EXACTLY in this format:

NAME:
<full name>

SHORT_NAME:
<first name or initials>

TAGLINE:
<role + specialization>

ABOUT:
<4–5 sentence professional summary>

PROJECTS:
<Title | Description> || <Title | Description> || <Title | Description>

SOCIALS:
<Label | URL> || <Label | URL> || <Label | URL>

CONTACT_TEXT:
<1–2 sentence call to action>

Resume:
{resume}
"""
)

raw = (prompt | llm).invoke({"resume": resume_content}).content

# ==================================================
# SAFE PARSER
# ==================================================
def extract(label: str) -> str:
    try:
        return raw.split(f"{label}:")[1].split("\n\n")[0].strip()
    except Exception:
        return ""

# ==================================================
# BUILD HTML BLOCKS (PROGRAMMATIC)
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
    for p in extract("PROJECTS").split("||")
)

socials_html = "".join(
    f"""
    <a href="{s.split('|')[1].strip()}" target="_blank">
      <img src="img/social_icons/{s.split('|')[0].lower()}.svg" />
    </a>
    """
    for s in extract("SOCIALS").split("||")
)

# ==================================================
# FINAL HTML ASSEMBLY
# ==================================================
final_html = (
    HTML_SKELETON
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

print("✅ SUCCESS: index.html generated with ALL sections and EXACT structure")
