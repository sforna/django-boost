"""
RuleRepository — manages project rules in .ai/rules/.

Equivalent to Laravel Boost's RuleRepository.
"""

import os

import yaml


class RuleRepository:
    """Manages project rules stored as markdown files in .ai/rules/.

    Each rule file has YAML frontmatter with paths (globs) and
    markdown body with titled sections.
    """

    INDEX_FILENAME = "index.md"
    MANAGED_DIRNAME = "boost"

    def __init__(self, directory: str | None = None):
        self._directory = directory or os.path.join(os.getcwd(), ".ai", "rules")

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def write(self, glob: str, title: str, note: str) -> str:
        """Record a rule and return the file path."""
        glob = glob.strip()
        title = " ".join(title.strip().split())
        note = note.strip()

        target = self._resolve_target_file(glob)

        if not os.path.isfile(target["path"]):
            self._create_file(target["path"], target["heading"], [glob])
        else:
            self._ensure_glob(target["path"], glob, target.get("parsed"))

        self._append_entry(target["path"], title, note)
        self.write_index()

        return target["path"]

    def write_index(self) -> str:
        """Regenerate the index.md file."""
        rows = []
        for f in self._markdown_files():
            parsed = self._parse_file(f)
            if parsed and parsed.get("paths"):
                rel = os.path.relpath(f, os.getcwd())
                globs = ", ".join(parsed["paths"])
                rows.append(f"| {globs} | {rel} |")

        table = "\n".join(rows) if rows else "No rules recorded yet."
        body = (
            "# Project Rules Index\n\n"
            "Before planning or editing, find the row whose globs match "
            "the file's path and read that rule file.\n\n"
            "| Applies to | Rule file |\n| --- | --- |\n"
            f"{table}\n"
        )

        os.makedirs(self._directory, exist_ok=True)
        index_path = os.path.join(self._directory, self.INDEX_FILENAME)
        with open(index_path, "w") as f:
            f.write(body)

        return index_path

    def normalize_glob(self, glob: str) -> str:
        """Normalize a glob path (remove leading cwd)."""
        glob = glob.replace("\\", "/").strip()
        cwd = os.getcwd().rstrip("/") + "/"
        if glob.startswith(cwd):
            glob = glob[len(cwd) :]
        return glob.lstrip("/")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _resolve_target_file(self, glob: str) -> dict:
        """Find or create the appropriate rule file for a glob."""
        all_parsed = []
        for f in self._markdown_files():
            parsed = self._parse_file(f)
            if parsed:
                all_parsed.append({"file": f, **parsed})

        area = self._area_key(glob)

        for existing in all_parsed:
            if glob in existing.get("paths", []):
                return {"path": existing["file"], "heading": "", "parsed": existing}
            for p in existing.get("paths", []):
                if self._area_key(p) == area:
                    return {"path": existing["file"], "heading": "", "parsed": existing}

        # Create new file
        segments = [s for s in glob.split("/") if s and not any(c in s for c in "*.[]")]
        slug = "-".join(s.lower().replace("_", "-") for s in segments) if segments else "general"

        path = os.path.join(self._directory, f"{slug}.md")
        heading = os.path.splitext(os.path.basename(path))[0].replace("-", " ").title()

        return {"path": path, "heading": heading, "parsed": None}

    def _area_key(self, glob: str) -> str:
        segments = [s for s in glob.split("/") if s and not any(c in s for c in "*.[]")]
        return "/".join(segments)

    def _create_file(self, path: str, heading: str, paths: list[str]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(self._render_frontmatter(paths))
            f.write(f"# {heading}\n")

    def _ensure_glob(self, path: str, glob: str, parsed: dict | None) -> None:
        if parsed is None:
            parsed = self._parse_file(path) or {"paths": [], "body": ""}

        if glob in parsed.get("paths", []):
            return

        paths = list(parsed.get("paths", [])) + [glob]
        frontmatter = self._render_frontmatter(paths)
        body = parsed.get("body", "")
        # Strip existing frontmatter
        if body.startswith("---"):
            body = body.split("---\n", 2)[-1] if "---\n" in body[4:] else body

        with open(path, "w") as f:
            f.write(frontmatter + body.lstrip("\n"))

    def _append_entry(self, path: str, title: str, note: str) -> None:
        with open(path, "a") as f:
            f.write(f"\n## {title}\n{note}\n")

    def _render_frontmatter(self, paths: list[str]) -> str:
        return f"---\n{yaml.dump({'paths': list(paths)}, default_flow_style=False)}---\n\n"

    def _parse_file(self, path: str) -> dict | None:
        """Parse a rule file into {paths, body}."""
        try:
            with open(path, "r") as f:
                content = f.read()
        except Exception:
            return None

        if content.startswith("---"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    return {
                        "paths": frontmatter.get("paths", []) if frontmatter else [],
                        "body": parts[2],
                    }
                except yaml.YAMLError:
                    pass

        return {"paths": [], "body": content}

    def _markdown_files(self) -> list[str]:
        """List all .md files in the rules directory (excluding index)."""
        if not os.path.isdir(self._directory):
            return []

        files = []
        for fname in os.listdir(self._directory):
            if fname.endswith(".md") and fname != self.INDEX_FILENAME:
                full_path = os.path.join(self._directory, fname)
                if os.path.isfile(full_path):
                    files.append(full_path)
        return sorted(files)
