from typing import Dict, Any, List, Optional

class AgentTemplateCatalog:
    """Catalog of pre-built reusable agent templates for rapid agent instantiation."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, Any]] = {
            "research_agent": {
                "template_id": "research_agent",
                "name": "Deep Research Agent",
                "category": "Research",
                "default_tools": ["search_web", "read_url_content", "extract_structured_table"],
                "default_capabilities": ["reasoning", "knowledge_extraction"]
            },
            "coding_agent": {
                "template_id": "coding_agent",
                "name": "Full-Stack Software Engineer",
                "category": "Engineering",
                "default_tools": ["github_connector", "terminal_executor", "view_file"],
                "default_capabilities": ["code_generation", "testing", "refactoring"]
            },
            "security_agent": {
                "template_id": "security_agent",
                "name": "Zero Trust Security Guardian",
                "category": "Security",
                "default_tools": ["audit_logger", "vault_retriever", "compliance_scanner"],
                "default_capabilities": ["threat_detection", "permission_enforcement"]
            }
        }

    def list_templates(self) -> List[Dict[str, Any]]:
        """Lists available agent templates."""
        return list(self._templates.values())

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Queries template configuration by ID."""
        return self._templates.get(template_id)
