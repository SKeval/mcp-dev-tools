# mcp-dev-tools

> An MCP (Model Context Protocol) server that integrates AI into software development workflows. Connects directly to Claude Desktop and any MCP-compatible client.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-1.3.0+-purple.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## What It Does

This server exposes 3 AI-powered development tools via the Model Context Protocol:

| Tool | Description |
|------|-------------|
| `code_review_checklist` | Generates a structured review checklist tailored to Python, TypeScript, or C# |
| `generate_commit_message` | Produces a Conventional Commits-formatted message from a plain diff summary |
| `api_docs_formatter` | Reformats raw docstrings into clean, structured Markdown API documentation |

Once connected to Claude Desktop, you can invoke these tools in natural language:
- *"Give me a Python code review checklist"*
- *"Generate a commit message for: added JWT auth to the login endpoint"*
- *"Format the docs for my validate_patient_record function"*

---

## Architecture

```
┌─────────────────────┐     JSON-RPC / stdio     ┌──────────────────────────┐
│   Claude Desktop    │ ◄─────────────────────── │   mcp-dev-tools server   │
│   (MCP Client)      │ ──────────────────────── │   (Python / FastMCP)     │
└─────────────────────┘                          │                          │
                                                 │  * code_review_checklist │
         OR                                      │  * generate_commit_msg   │
                                                 │  * api_docs_formatter    │
┌─────────────────────┐                          └──────────────────────────┘
│  Your Python Client │ ◄── stdio_client() ──────────────────┘
│  (client.py)        │
└─────────────────────┘
```

---

## Getting Started

### 1. Install dependencies

```bash
git clone https://github.com/SKeval/mcp-dev-tools
cd mcp-dev-tools
pip install -r requirements.txt
```

### 2. Test with the included client

```bash
python client.py
```

Expected output:
```
mcp-dev-tools connected. Available tools:
   * code_review_checklist
   * generate_commit_message
   * api_docs_formatter
...
All 3 tools working. mcp-dev-tools is ready.
```

### 3. Connect to Claude Desktop

Add this to your Claude Desktop config file:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-dev-tools": {
      "command": "python",
      "args": ["/absolute/path/to/mcp-dev-tools/server.py"]
    }
  }
}
```

Restart Claude Desktop. You'll see `mcp-dev-tools` appear in the tools panel.

---

## Tool Reference

### `code_review_checklist`

Returns a structured checklist for code reviews.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | `str` | `"general"` | `python`, `typescript`, `csharp`, or `general` |
| `include_general` | `bool` | `True` | Appends general checklist after language-specific |

**Example:**
```python
result = await session.call_tool(
    "code_review_checklist",
    {"language": "python", "include_general": True}
)
```

---

### `generate_commit_message`

Generates a [Conventional Commits](https://www.conventionalcommits.org/) message.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `diff_summary` | `str` | required | Plain-English description of the change |
| `commit_type` | `str` | `"feat"` | `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, etc. |
| `scope` | `str` | `""` | Component name e.g. `auth`, `api`, `fhir` |
| `breaking_change` | `bool` | `False` | Adds `!` marker and BREAKING CHANGE footer |

**Example output:**
```
feat(fhir): added FHIR resource validation to the patient data ingestion pipeline

Type: feat — A new feature
Scope: fhir
```

---

### `api_docs_formatter`

Converts a raw docstring into structured Markdown API docs.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `function_name` | `str` | required | Name of the function |
| `raw_docstring` | `str` | required | Existing description or raw docstring |
| `language` | `str` | `"python"` | `python`, `typescript`, or `csharp` |
| `include_example` | `bool` | `True` | Adds a usage example section |

---

## Why MCP?

Traditional AI integrations require custom one-off code for every tool connection. MCP standardizes this — build the server once, connect it to any MCP-compatible client. This is the same pattern applicable to clinical software development: a single MCP server can expose AI-assisted code review, compliance checking, and documentation generation across an entire development team's workflow.

---

## License

MIT License
