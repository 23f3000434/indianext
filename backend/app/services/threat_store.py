"""
safewaves Threat Store
=======================
Simple in-memory store for recent threat analysis results.
Used by the threat feed endpoint and populated by all analysis endpoints.
"""

from collections import deque


class ThreatStore:
    def __init__(self, maxlen=100):
        self._threats = deque(maxlen=maxlen)

    def add(self, threat: dict):
        self._threats.appendleft(threat)

    def get_all(self) -> list:
        return list(self._threats)

    def get_recent(self, n: int = 10) -> list:
        return list(self._threats)[:n]


threat_store = ThreatStore()
