from typing import Any, Dict, Optional


class OutputFormatter:
    """Output formatter supporting multiple formats

    Maintenance note (for yourself in 6 months):
    - Add JSON output to format_content()
    - Consider YAML output support
    - Support for custom templates
    """

    def __init__(self, format_type: str = "markdown"):
        self.format_type = format_type

    def format_content(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format content based on specified type"""
        if self.format_type == "markdown":
            return self._format_markdown(content, metadata)
        else:
            return content

    def _format_markdown(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format as Markdown (metadata is optional)"""
        result = []

        if metadata:
            result.append("---")
            for key, value in metadata.items():
                result.append(f"{key}: {value}")
            result.append("---")
            result.append("")

        result.append(content)
        return "\n".join(result)
