from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TimeWindow:
    start: datetime
    end: datetime

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600
