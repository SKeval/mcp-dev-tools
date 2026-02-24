"""
mcp-dev-tools: MCP server for software development workflow automation.
Exposes 3 tools to Claude Desktop and any MCP-compatible client:
  1. code_review_checklist   - structured review checklist per language
  2. generate_commit_message - conventional commit message from a diff summary
  3. api_docs_formatter      - reformats raw docstrings into clean markdown
"""

from mcp.server.fastmcp import FastMCP
from typing import Literal

mcp = FastMCP("mcp-dev-tools")


# ── TOOL 1: Code Review Checklist ─────────────────────────────────────────────

CHECKLISTS = {
    "python": [
        "[ ] Type hints present on all function parameters and return values",
        "[ ] Docstrings follow Google or NumPy style",
        "[ ] No mutable default arguments (e.g. def f(x=[]) is a bug)",
        "[ ] Exception handling is specific — no bare `except:` clauses",
        "[ ] No hardcoded secrets, credentials, or file paths",
        "[ ] Functions are single-responsibility and under ~50 lines",
        "[ ] All public functions have unit tests",
        "[ ] f-strings used instead of % or .format() for string formatting",
        "[ ] Imports are sorted: stdlib → third-party → local",
        "[ ] No unused imports or variables",
        "[ ] Async functions are awaited correctly — no fire-and-forget",
        "[ ] Pydantic models used for data validation where appropriate",
    ],
    "typescript": [
        "[ ] Strict TypeScript — no `any` types without justification",
        "[ ] Interfaces defined for all data structures",
        "[ ] Async/await used consistently — no mixed Promise chains",
        "[ ] Error handling on all async calls (try/catch or .catch())",
        "[ ] No console.log left in production code",
        "[ ] Null/undefined checks in place — use optional chaining (?.) ",
        "[ ] Enums used for fixed sets of values instead of magic strings",
        "[ ] Functions are typed with explicit return types",
        "[ ] No unused variables or imports (ESLint no-unused-vars)",
        "[ ] API responses validated before use",
    ],
    "csharp": [
        "[ ] Nullable reference types enabled and handled",
        "[ ] Async methods suffixed with 'Async' (e.g. GetDataAsync)",
        "[ ] Dispose pattern implemented for IDisposable resources",
        "[ ] LINQ queries are readable — avoid deep nesting",
        "[ ] No magic numbers — use named constants or enums",
        "[ ] Exception messages are descriptive and actionable",
        "[ ] Dependency injection used — no direct `new` on services",
        "[ ] XML documentation comments on all public members",
        "[ ] Unit tests follow Arrange-Act-Assert pattern",
        "[ ] No synchronous calls inside async methods (no .Result or .Wait())",
    ],
    "general": [
        "[ ] Code is self-documenting — variable names explain intent",
        "[ ] No commented-out code blocks",
        "[ ] No TODO comments without an associated ticket/issue",
        "[ ] DRY principle followed — no duplicated logic",
        "[ ] Edge cases handled: empty input, null values, boundary conditions",
        "[ ] Error messages are user-friendly and actionable",
        "[ ] No hardcoded environment-specific values",
        "[ ] Logging is present at appropriate levels (debug/info/warn/error)",
        "[ ] Security: inputs are validated and sanitized",
        "[ ] Performance: no N+1 queries or unnecessary loops",
    ],
}


@mcp.tool()
def code_review_checklist(
    language: Literal["python", "typescript", "csharp", "general"] = "general",
    include_general: bool = True,
) -> str:
    """
    Returns a structured code review checklist for the specified programming language.

    Args:
        language: The programming language to generate the checklist for.
                  Options: python, typescript, csharp, general.
        include_general: If True, appends the general checklist after the
                         language-specific one. Defaults to True.

    Returns:
        A formatted markdown checklist string ready for use in code review.
    """
    lines = [f"## Code Review Checklist — {language.title()}\n"]

    if language != "general":
        lines.append(f"### {language.title()}-Specific")
        lines.extend(CHECKLISTS[language])

    if include_general and language != "general":
        lines.append("\n### General")
        lines.extend(CHECKLISTS["general"])
    elif language == "general":
        lines.extend(CHECKLISTS["general"])

    return "\n".join(lines)


# ── TOOL 2: Generate Commit Message ───────────────────────────────────────────

COMMIT_TYPES = {
    "feat":     "A new feature",
    "fix":      "A bug fix",
    "docs":     "Documentation changes only",
    "style":    "Formatting, missing semicolons — no logic change",
    "refactor": "Code restructuring without feature or bug change",
    "perf":     "Performance improvements",
    "test":     "Adding or updating tests",
    "chore":    "Build process, dependency updates, tooling",
    "ci":       "CI/CD configuration changes",
    "revert":   "Reverts a previous commit",
}


@mcp.tool()
def generate_commit_message(
    diff_summary: str,
    commit_type: Literal[
        "feat", "fix", "docs", "style", "refactor",
        "perf", "test", "chore", "ci", "revert"
    ] = "feat",
    scope: str = "",
    breaking_change: bool = False,
) -> str:
    """
    Generates a Conventional Commits-formatted commit message from a diff summary.

    Args:
        diff_summary: Plain-English description of what changed.
                      Example: 'Added input validation to the registration endpoint'
        commit_type:  The type of change: feat, fix, docs, style, refactor,
                      perf, test, chore, ci, revert.
        scope:        Optional component name affected. Example: 'auth', 'api'
        breaking_change: If True, adds BREAKING CHANGE footer and ! marker.

    Returns:
        A formatted commit message following the Conventional Commits spec.
    """
    scope_part = f"({scope})" if scope else ""
    breaking_marker = "!" if breaking_change else ""

    subject = diff_summary.strip().rstrip(".")
    if len(subject) > 72:
        subject = subject[:69] + "..."
    subject = subject[0].lower() + subject[1:]

    subject_line = f"{commit_type}{scope_part}{breaking_marker}: {subject}"

    body_lines = [
        "",
        f"Type: {commit_type} — {COMMIT_TYPES[commit_type]}",
    ]

    if scope:
        body_lines.append(f"Scope: {scope}")

    if breaking_change:
        body_lines.extend([
            "",
            "BREAKING CHANGE: This commit introduces a breaking change.",
            "Update any dependent code accordingly.",
        ])

    return "\n".join([subject_line] + body_lines)


# ── TOOL 3: API Docs Formatter ─────────────────────────────────────────────────

@mcp.tool()
def api_docs_formatter(
    function_name: str,
    raw_docstring: str,
    language: Literal["python", "typescript", "csharp"] = "python",
    include_example: bool = True,
) -> str:
    """
    Reformats a raw or poorly formatted docstring into clean structured
    Markdown API documentation.

    Args:
        function_name:   The name of the function or method being documented.
        raw_docstring:   The existing raw docstring or description to reformat.
        language:        Programming language — affects code block syntax.
        include_example: If True, adds a usage example section.

    Returns:
        A clean Markdown string suitable for API docs or README sections.
    """
    code_lang = language

    lines = [
        f"## `{function_name}`\n",
        "### Description\n",
        f"{raw_docstring.strip()}\n",
        "### Parameters\n",
        "| Parameter | Type | Required | Description |",
        "|-----------|------|----------|-------------|",
        "| `param1`  | `str` | ✅ Yes  | Description of param1 |",
        "| `param2`  | `int` | ❌ No   | Description of param2 (default: 0) |\n",
        "### Returns\n",
        "| Type | Description |",
        "|------|-------------|",
        "| `str` | Description of the return value |\n",
        "### Raises\n",
        "| Exception | Condition |",
        "|-----------|-----------|",
        "| `ValueError` | When input is invalid |",
        "| `RuntimeError` | When the operation fails |\n",
    ]

    if include_example:
        if language == "python":
            example = (
                f"```{code_lang}\n"
                f"result = {function_name}(\n"
                f"    param1=\"example\",\n"
                f"    param2=42\n"
                f")\nprint(result)\n```"
            )
        elif language == "typescript":
            example = (
                f"```{code_lang}\n"
                f"const result = await {function_name}({{\n"
                f"    param1: \"example\",\n"
                f"    param2: 42\n"
                f"}});\nconsole.log(result);\n```"
            )
        else:
            example = (
                f"```{code_lang}\n"
                f"var result = await {function_name}(\n"
                f"    param1: \"example\",\n"
                f"    param2: 42\n"
                f");\nConsole.WriteLine(result);\n```"
            )

        lines += ["### Example\n", example, ""]

    lines += [
        "---",
        f"*Generated by mcp-dev-tools · [{function_name}](#{function_name.lower()})*",
    ]

    return "\n".join(lines)


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
