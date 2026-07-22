import time
from typing import Dict, Any, List

class EnterpriseDataPipeline:
    """Ingests real-time and batch telemetry streams from all 14 JARVIS modules (<1s ingestion target)."""

    def __init__(self):
        self._event_buffer: List[Dict[str, Any]] = []

    async def ingest_event(
        self,
        source_module: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ingests a telemetry event into analytical data lake stream (<1s target)."""
        start_time = time.time()
        
        event_record = {
            "event_id": f"evt_{int(time.time()*1000)}",
            "source_module": source_module.lower(),
            "event_type": event_type,
            "payload": payload,
            "timestamp": time.time()
        }
        self._event_buffer.append(event_record)
        ingest_duration_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "status": "INGESTED",
            "ingest_duration_ms": ingest_duration_ms,
            "event_id": event_record["event_id"]
        }

    async def get_buffer_count(self) -> int:
        """Queries count of buffered events."""
        return len(self._event_buffer)
