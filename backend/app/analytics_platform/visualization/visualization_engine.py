from typing import Dict, Any, List

class DataVisualizationEngine:
    """Formats chart data structures for Line Charts, Bar Charts, Heatmaps, Sankey Diagrams, and Knowledge Maps."""

    def format_chart_payload(
        self,
        chart_type: str,
        raw_series: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Formats raw telemetry into chart render structures."""
        chart_clean = chart_type.lower()
        
        return {
            "chart_type": chart_clean,
            "render_config": {
                "theme": "dark_glassmorphism",
                "animation": True,
                "responsive": True
            },
            "data": raw_series
        }
