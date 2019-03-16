import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HeadlineRules:
    name: str
    regex: Optional[str] = None
    order: Optional[int] = None
    required: bool = False
    dependencies: List[List[str]] = field(default_factory=list)

    def matches_any(self, candidates: List[str]) -> bool:
        for candidate in candidates:
            if self.matches(candidate):
                return True
        return False

    def matches(self, candidate: str) -> bool:
        if re.match(self.name, candidate, re.I):
            return True
        if self.regex and re.match(self.regex, candidate, re.I):
            return True
        return False
