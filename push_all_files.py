import os
import base64
import requests
from dotenv import load_dotenv

# ===================== CONFIG =====================
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = "supraja777"
REPO = "my-new-repo"
BRANCH = "main"
ROOT_DIR = "."   # directory to push

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# ===================== HELPERS =====================
def github_get(url):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def github_post(url, payload):
    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def github_patch(url, payload):
    r = requests.patch(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

# ===================== STEP 1: GET LATEST COMMIT =====================
def get_latest_commit_sha():
    ref = github_get(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}"
    )
    return ref["object"]["sha"]

def get_base_tree_sha(commit_sha):
    commit = github_get(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/commits/{commit_sha}"
    )
    return commit["tree"]["sha"]

# ===================== STEP 2: CREATE BLOBS =====================
def create_blob(file_path):
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    blob = github_post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/blobs",
        {
            "content": content,
            "encoding": "base64"
        }
    )
    return blob["sha"]

# ===================== STEP 3: BUILD TREE =====================
def build_tree():
    tree = []

    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            full_path = os.path.join(root, file)

            # skip git + env files
            if ".git" in full_path or file == ".env":
                continue

            blob_sha = create_blob(full_path)

            tree.append({
                "path": os.path.relpath(full_path, ROOT_DIR),
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha
            })

    return tree

# ===================== STEP 4: CREATE TREE =====================
def create_tree(base_tree_sha, tree):
    new_tree = github_post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees",
        {
            "base_tree": base_tree_sha,
            "tree": tree
        }
    )
    return new_tree["sha"]

# ===================== STEP 5: CREATE COMMIT =====================
def create_commit(message, tree_sha, parent_sha):
    commit = github_post(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/commits",
        {
            "message": message,
            "tree": tree_sha,
            "parents": [parent_sha]
        }
    )
    return commit["sha"]

# ===================== STEP 6: UPDATE BRANCH =====================
def update_branch(commit_sha):
    github_patch(
        f"https://api.github.com/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
        {"sha": commit_sha}
    )

# ===================== RUN =====================
def push_all():
    print("🚀 Pushing entire directory to GitHub...")

    latest_commit = get_latest_commit_sha()
    base_tree = get_base_tree_sha(latest_commit)

    tree = build_tree()
    new_tree_sha = create_tree(base_tree, tree)

    commit_sha = create_commit(
        "Auto commit: push full repo",
        new_tree_sha,
        latest_commit
    )

    update_branch(commit_sha)

    print("✅ SUCCESS: All files pushed in ONE commit")

if __name__ == "__main__":
    push_all()
