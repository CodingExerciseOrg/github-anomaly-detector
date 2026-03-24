from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo  # add this import

@dataclass
class Alert:
    """Represents a detected suspicious event."""

    title: str
    event_type: str
    details: dict = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.now(ZoneInfo("America/New_York")))  # changed

    def __str__(self) -> str:
        lines = [
            "",
            "=" * 60,
            f"SUSPICIOUS ACTIVITY DETECTED",
            "=" * 60,
            f"  Title      : {self.title}",
            f"  Event Type : {self.event_type}",
            f"  Detected At: {self.detected_at.strftime('%Y-%m-%d %H:%M:%S %Z')}",  # changed
            "  Details:",
        ]
        for key, value in self.details.items():
            lines.append(f"    - {key}: {value}")
        lines.append("=" * 60)
        return "\n".join(lines)