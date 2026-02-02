import argparse
import datetime as dt
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "docs" / "BLOG_POST_TEMPLATE_SEO.md"
OUT_DIR = ROOT / "siteDjangoProject" / "blog_posts"

STOPWORDS = {
    "a",
    "as",
    "o",
    "os",
    "e",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "para",
    "por",
    "que",
    "como",
    "quando",
    "onde",
    "qual",
}


def slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"[^a-z0-9_-]", "", slug)
    slug = re.sub(r"_{2,}", "_", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("_-")
    return slug


def title_from_slug(slug: str) -> str:
    words = re.split(r"[-_]+", slug)
    return " ".join(word.capitalize() for word in words if word)


def keywords_from_slug(slug: str) -> str:
    words = [w for w in re.split(r"[-_]+", slug) if w]
    filtered = [w for w in words if w not in STOPWORDS]
    seen = set()
    unique = []
    for word in filtered:
        if word not in seen:
            unique.append(word)
            seen.add(word)
    base = ", ".join(unique[:6])
    if base:
        return f"{base}, sistema eleitoral brasileiro"
    return "sistema eleitoral brasileiro"


def replace_frontmatter(template: str, fields: dict) -> str:
    lines = template.splitlines()
    for i, line in enumerate(lines):
        for key, value in fields.items():
            if line.startswith(f"{key}: "):
                safe_value = value.replace('"', '\\"')
                lines[i] = f'{key}: "{safe_value}"'
                break
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a new blog post from the SEO template.")
    parser.add_argument("slug", help="Slug do post (usado no nome do arquivo e URL).")
    parser.add_argument("--title", help="Titulo do post.")
    parser.add_argument("--description", help="Descricao curta para SEO.")
    parser.add_argument("--keywords", help="Lista de palavras-chave separadas por virgula.")
    parser.add_argument("--author", default="Filipe Dias", help="Autor do post.")
    parser.add_argument("--date", help="Data no formato YYYY-MM-DD.")
    parser.add_argument("--canonical", help="URL canonica completa.")
    args = parser.parse_args()

    slug = slugify(args.slug)
    if not slug:
        print("Slug invalido.")
        return 1

    if not TEMPLATE_PATH.exists():
        print(f"Template nao encontrado em: {TEMPLATE_PATH}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUT_DIR / f"{slug}.md"
    if output_path.exists():
        print(f"O arquivo ja existe: {output_path}")
        return 1

    title = args.title or title_from_slug(slug)
    description = args.description or f"Entenda {title} com exemplos e regras do sistema eleitoral brasileiro."
    keywords = args.keywords or keywords_from_slug(slug)
    author = args.author
    date_value = args.date or dt.date.today().isoformat()
    canonical = args.canonical or f"https://mapaeleitoral.com.br/blog/{slug}/"

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    content = replace_frontmatter(
        template,
        {
            "title": title,
            "description": description,
            "keywords": keywords,
            "author": author,
            "date": date_value,
            "canonical": canonical,
        },
    )

    output_path.write_text(content, encoding="utf-8")
    print(f"Post criado: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
