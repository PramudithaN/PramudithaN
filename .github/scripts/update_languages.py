import os
import re
import urllib.request
import json
import urllib.parse

# Configuration
USERNAME = os.environ.get("GITHUB_ACTOR") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "PramudithaN"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
README_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")

# Non-programming languages / build scripts to ignore
IGNORED_LANGUAGES = {
    "Batchfile",
    "Makefile",
    "Procfile",
    "Less",
    "CMake",
    "Gnuplot",
    "Roff",
    "HLSL",
    "ShaderLab",
}

# Known language badge styles mapping
# Format: label, background_color, logo_slug, logo_color
LANGUAGE_BADGES = {
    "TypeScript": {
        "label": "TypeScript",
        "color": "%23007ACC",
        "logo": "typescript",
        "logoColor": "white"
    },
    "JavaScript": {
        "label": "JavaScript",
        "color": "%23323330",
        "logo": "javascript",
        "logoColor": "%23F7DF1E"
    },
    "Python": {
        "label": "Python",
        "color": "%233776AB",
        "logo": "python",
        "logoColor": "white"
    },
    "Java": {
        "label": "Java",
        "color": "%23ED8B00",
        "logo": "openjdk",
        "logoColor": "white"
    },
    "Kotlin": {
        "label": "Kotlin",
        "color": "%237F52FF",
        "logo": "kotlin",
        "logoColor": "white"
    },
    "HTML": {
        "label": "HTML5",
        "color": "%23E34F26",
        "logo": "html5",
        "logoColor": "white"
    },
    "CSS": {
        "label": "CSS3",
        "color": "%231572B6",
        "logo": "css3",
        "logoColor": "white"
    },
    "SCSS": {
        "label": "Sass",
        "color": "%23CC6699",
        "logo": "sass",
        "logoColor": "white"
    },
    "C#": {
        "label": "C%23",
        "color": "%23239120",
        "logo": "c-sharp",
        "logoColor": "white"
    },
    "C++": {
        "label": "C%2B%2B",
        "color": "%2300599C",
        "logo": "cplusplus",
        "logoColor": "white"
    },
    "C": {
        "label": "C",
        "color": "%2300599C",
        "logo": "c",
        "logoColor": "white"
    },
    "Dart": {
        "label": "Dart",
        "color": "%230175C2",
        "logo": "dart",
        "logoColor": "white"
    },
    "Go": {
        "label": "Go",
        "color": "%2300ADD8",
        "logo": "go",
        "logoColor": "white"
    },
    "Rust": {
        "label": "Rust",
        "color": "%23000000",
        "logo": "rust",
        "logoColor": "white"
    },
    "PHP": {
        "label": "PHP",
        "color": "%23777BB4",
        "logo": "php",
        "logoColor": "white"
    },
    "Ruby": {
        "label": "Ruby",
        "color": "%23CC342D",
        "logo": "ruby",
        "logoColor": "white"
    },
    "Swift": {
        "label": "Swift",
        "color": "%23FA7343",
        "logo": "swift",
        "logoColor": "white"
    },
    "Shell": {
        "label": "Shell_Script",
        "color": "%23121011",
        "logo": "gnu-bash",
        "logoColor": "white"
    },
    "PowerShell": {
        "label": "PowerShell",
        "color": "%235391FE",
        "logo": "powershell",
        "logoColor": "white"
    },
    "Jupyter Notebook": {
        "label": "Jupyter",
        "color": "%23F37626",
        "logo": "jupyter",
        "logoColor": "white"
    },
    "Vue": {
        "label": "Vue.js",
        "color": "%2335495E",
        "logo": "vuedotjs",
        "logoColor": "%234FC08D"
    },
    "Svelte": {
        "label": "Svelte",
        "color": "%23f1413d",
        "logo": "svelte",
        "logoColor": "white"
    },
    "R": {
        "label": "R",
        "color": "%23276DC3",
        "logo": "r",
        "logoColor": "white"
    },
    "Lua": {
        "label": "Lua",
        "color": "%232C2D72",
        "logo": "lua",
        "logoColor": "white"
    },
    "Dockerfile": {
        "label": "Docker",
        "color": "%232496ED",
        "logo": "docker",
        "logoColor": "white"
    },
    "PLpgSQL": {
        "label": "PostgreSQL",
        "color": "%23316192",
        "logo": "postgresql",
        "logoColor": "white"
    },
    "SQL": {
        "label": "SQL",
        "color": "%23003B57",
        "logo": "sqlite",
        "logoColor": "white"
    }
}


def make_request(url):
    headers = {
        "User-Agent": "GitHub-Action-Languages-Updater",
        "Accept": "application/vnd.github.v3+json"
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_user_languages(username):
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
    repos = make_request(repos_url)
    if not repos or not isinstance(repos, list):
        print(f"Could not fetch repos for {username}")
        return {}

    language_totals = {}
    print(f"Scanning {len(repos)} repositories for {username}...")

    for repo in repos:
        # Skip forks if any
        if repo.get("fork"):
            continue

        repo_name = repo.get("name")
        languages_url = repo.get("languages_url")
        if not languages_url:
            continue

        lang_data = make_request(languages_url)
        if lang_data and isinstance(lang_data, dict):
            for lang, byte_count in lang_data.items():
                language_totals[lang] = language_totals.get(lang, 0) + byte_count

    return language_totals


def generate_badge_tag(lang_name):
    config = LANGUAGE_BADGES.get(lang_name)
    if config:
        label = config["label"]
        color = config["color"]
        logo = config["logo"]
        logo_color = config["logoColor"]
    else:
        label = urllib.parse.quote(lang_name)
        color = "%23333333"
        logo = urllib.parse.quote(lang_name.lower())
        logo_color = "white"

    badge_url = f"https://img.shields.io/badge/{label}-{color}.svg?style=for-the-badge&logo={logo}&logoColor={logo_color}"
    return f'<img src="{badge_url}" />'


def update_readme(badges_html):
    if not os.path.exists(README_PATH):
        print(f"README.md not found at {README_PATH}")
        return False

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- DYNAMIC_LANGUAGES_START -->"
    end_tag = "<!-- DYNAMIC_LANGUAGES_END -->"

    pattern = re.compile(
        f"{re.escape(start_tag)}.*?{re.escape(end_tag)}",
        re.DOTALL
    )

    replacement = f"{start_tag}\n{badges_html}\n{end_tag}"

    if pattern.search(content):
        updated_content = pattern.sub(replacement, content)
    else:
        print("Marker tags not found in README.md, please add marker comments.")
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("Successfully updated README.md with dynamic language badges.")
    return True


def main():
    print(f"Fetching language stats for {USERNAME}...")
    lang_totals = get_user_languages(USERNAME)

    if not lang_totals:
        print("No language data found.")
        return

    # Filter out ignored languages (e.g. build scripts, config files)
    filtered_langs = {
        lang: count for lang, count in lang_totals.items()
        if lang not in IGNORED_LANGUAGES
    }

    # Sort languages by byte count descending
    sorted_langs = sorted(filtered_langs.items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(b for _, b in sorted_langs)

    print("\nDetected Language Breakdown:")
    for lang, bytes_cnt in sorted_langs:
        pct = (bytes_cnt / total_bytes) * 100
        print(f"- {lang}: {bytes_cnt:,} bytes ({pct:.1f}%)")

    # Filter languages that have meaningful byte counts (> 1KB or > 0.05%)
    significant_langs = [
        lang for lang, bytes_cnt in sorted_langs
        if (bytes_cnt / total_bytes) >= 0.0005 or bytes_cnt > 1000
    ]

    badge_tags = [generate_badge_tag(lang) for lang in significant_langs]
    badges_html = "\n".join(badge_tags)

    update_readme(badges_html)


if __name__ == "__main__":
    main()
