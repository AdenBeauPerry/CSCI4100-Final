from typing import List, Optional

class Event:
    def __init__(
        self,
        name: str,
        duration: int,  # in days
        dependencies: Optional[List[str]] = None,  # list of event names/IDs
        resources_required: int = 1,
        priority: int = 1,  # 1 = highest priority
        deadline: int = -1  # in days from start, -1 means no deadline
    ):
        self.name = name
        self.duration = duration
        self.dependencies = dependencies if dependencies else []
        self.resources_required = resources_required
        self.priority = priority
        self.deadline = deadline

    def __repr__(self):
        return (
            f"Event(name={self.name!r}, duration={self.duration}, "
            f"dependencies={self.dependencies}, resources_required={self.resources_required}, "
            f"priority={self.priority}, deadline={self.deadline})"
        )