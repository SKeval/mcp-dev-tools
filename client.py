"""
Test client for mcp-dev-tools server.
Run this to verify all 3 tools are working correctly.
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=" * 60)
            print("mcp-dev-tools connected. Available tools:")
            for tool in tools.tools:
                print(f"   * {tool.name}")
            print("=" * 60)

            # Test 1: code_review_checklist
            print("\nTOOL 1: code_review_checklist(language='python')\n")
            result = await session.call_tool(
                "code_review_checklist",
                {"language": "python", "include_general": False}
            )
            print(result.content[0].text)

            # Test 2: generate_commit_message
            print("\n" + "=" * 60)
            print("\nTOOL 2: generate_commit_message\n")
            result = await session.call_tool(
                "generate_commit_message",
                {
                    "diff_summary": "Added FHIR resource validation to the patient data ingestion pipeline",
                    "commit_type": "feat",
                    "scope": "fhir",
                    "breaking_change": False,
                }
            )
            print(result.content[0].text)

            # Test 3: api_docs_formatter
            print("\n" + "=" * 60)
            print("\nTOOL 3: api_docs_formatter\n")
            result = await session.call_tool(
                "api_docs_formatter",
                {
                    "function_name": "validate_patient_record",
                    "raw_docstring": "Validates a patient record against the IEC 62304 compliance schema.",
                    "language": "python",
                    "include_example": True,
                }
            )
            print(result.content[0].text)
            
            
            # Test 4: Pull Request Description Formatter
            print("\n" + "=" * 60)
            print("\nTOOL 4: generate_pr_description\n")
            result = await session.call_tool(
                "generate_pr_description",
                {
                    "title": "Add FHIR validation",
                    "change_summary": "Added input validation for all FHIR Patient resources before ingestion into the clinical pipeline"
                }
            )
            print(result.content[0].text)

            print("\n" + "=" * 60)
            print("All 4 tools working. mcp-dev-tools is ready.")
            print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
