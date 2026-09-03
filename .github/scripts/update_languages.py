import os
import sys
import re
import urllib.request
import json
import urllib.parse

# Configuration
owner = os.environ.get("GITHUB_REPOSITORY_OWNER")
actor = os.environ.get("GITHUB_ACTOR")
if owner and not owner.endswith("[bot]"):
    USERNAME = owner
elif actor and not actor.endswith("[bot]"):
    USERNAME = actor
else:
    USERNAME = "PramudithaN"

TOKEN = (
    os.environ.get("GH_PAT")
    or os.environ.get("PAT_TOKEN")
    or os.environ.get("GITHUB_TOKEN")
    or os.environ.get("GH_TOKEN")
)
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
    },
    "Solidity": {
        "label": "Solidity",
        "color": "%23363636",
        "logo": "solidity",
        "logoColor": "white"
    },
    "Scala": {
        "label": "Scala",
        "color": "%23DC322F",
        "logo": "scala",
        "logoColor": "white"
    },
    "Elixir": {
        "label": "Elixir",
        "color": "%234B275F",
        "logo": "elixir",
        "logoColor": "white"
    },
    "Haskell": {
        "label": "Haskell",
        "color": "%235D4F85",
        "logo": "haskell",
        "logoColor": "white"
    },
    "Zig": {
        "label": "Zig",
        "color": "%23F7A41D",
        "logo": "zig",
        "logoColor": "white"
    },
    "Julia": {
        "label": "Julia",
        "color": "%239558B2",
        "logo": "julia",
        "logoColor": "white"
    },
    "GraphQL": {
        "label": "GraphQL",
        "color": "%23E10098",
        "logo": "graphql",
        "logoColor": "white"
    }
}


def make_request(url):
    headers = {
        "User-Agent": "GitHub-Action-Languages-Updater",
        "Accept": "application/vnd.github.v3+json"
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_user_languages(username):
    repos = []
    page = 1
    # If a custom PAT is supplied, /user/repos returns both public and private repos owned by the user
    # Otherwise, /users/{username}/repos fetches all public repos
    has_pat = bool(os.environ.get("GH_PAT") or os.environ.get("PAT_TOKEN"))

    while True:
        if has_pat:
            repos_url = f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner"
        else:
            repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&type=owner"

        page_repos = make_request(repos_url)
        if page_repos is None:
            # If error and page 1, we can't continue; if subsequent page, break
            if page == 1 and not has_pat:
                print(f"Could not fetch repos for {username}")
                return None
            break

        if not isinstance(page_repos, list) or len(page_repos) == 0:
            break

        repos.extend(page_repos)
        if len(page_repos) < 100:
            break
        page += 1

    if not repos:
        print(f"No repositories found for {username}")
        return {}

    language_totals = {}
    print(f"Scanning {len(repos)} repositories for {username}...")

    for repo in repos:
        # Skip forks if any
        if repo.get("fork"):
            continue

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

    if lang_totals is None:
        print("Failed to fetch repository or language data from GitHub API.")
        # Exit with non-zero code so GitHub Actions workflow alerts on failure
        sys.exit(1)

    if not lang_totals:
        print("No language data found across repositories.")
        return

    # Filter out ignored languages (e.g. build scripts, config files)
    filtered_langs = {
        lang: count for lang, count in lang_totals.items()
        if lang not in IGNORED_LANGUAGES
    }

    if not filtered_langs:
        print("No eligible programming languages found after filtering.")
        return

    # Sort languages by byte count descending
    sorted_langs = sorted(filtered_langs.items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(b for _, b in sorted_langs)

    print(f"\nDetected Language Breakdown (Total: {total_bytes:,} bytes):")
    for lang, bytes_cnt in sorted_langs:
        pct = (bytes_cnt / total_bytes) * 100 if total_bytes > 0 else 0
        print(f"- {lang}: {bytes_cnt:,} bytes ({pct:.1f}%)")

    # Include all detected languages that make up at least 0.01% or at least 100 bytes
    significant_langs = [
        lang for lang, bytes_cnt in sorted_langs
        if (total_bytes > 0 and (bytes_cnt / total_bytes) >= 0.0001) or bytes_cnt >= 100
    ]

    # Fallback to top languages if none met the threshold
    if not significant_langs:
        significant_langs = [lang for lang, _ in sorted_langs[:15]]

    badge_tags = [generate_badge_tag(lang) for lang in significant_langs]
    badges_html = " ".join(badge_tags)

    success = update_readme(badges_html)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
