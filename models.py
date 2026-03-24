from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Alert:
    """Represents a detected suspicious event."""

    title: str                      # Alert description
    event_type: str                 # GitHub webhook event type (e.g. "push")
    details: dict = field(default_factory=dict)  # Relevant payload fields
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        lines = [
            "",
            "=" * 60,
            f"SUSPICIOUS ACTIVITY DETECTED",
            "=" * 60,
            f"  Title      : {self.title}",
            f"  Event Type : {self.event_type}",
            f"  Detected At: {self.detected_at.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "  Details:",
        ]
        for key, value in self.details.items():
            lines.append(f"    - {key}: {value}")
        lines.append("=" * 60)
        return "\n".join(lines)
