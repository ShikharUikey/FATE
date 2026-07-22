import time
from typing import Dict, Any, List, Callable

class EventBusPlatform:
    """Publish-Subscribe Event Bus platform (Kafka, RabbitMQ, Redis Streams adapters) with Dead Letter Queue."""

    def __init__(self):
        self._topics: Dict[str, List[Dict[str, Any]]] = {}
        self._dlq: List[Dict[str, Any]] = []

    async def publish_event(
        self,
        topic: str,
        event_name: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publishes an event message to target topic."""
        event_id = f"evt_bus_{int(time.time()*1000)}"
        record = {
            "event_id": event_id,
            "topic": topic,
            "event_name": event_name,
            "payload": payload,
            "timestamp": time.time()
        }
        
        if topic not in self._topics:
            self._topics[topic] = []
        self._topics[topic].append(record)

        return {
            "status": "PUBLISHED",
            "topic": topic,
            "event_id": event_id
        }

    async def fetch_topic_events(self, topic: str) -> List[Dict[str, Any]]:
        """Retrieves messages published on topic."""
        return self._topics.get(topic, [])

    async def push_to_dead_letter_queue(self, event_id: str, reason: str) -> bool:
        """Routes failed message into Dead-Letter Queue (DLQ)."""
        self._dlq.append({"event_id": event_id, "reason": reason, "timestamp": time.time()})
        return True
