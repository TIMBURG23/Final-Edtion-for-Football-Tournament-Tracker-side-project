# storage/base_store.py
"""
Abstract storage interface used by UI and core logic.
Concrete implementations must implement these methods.
"""
from abc import ABC, abstractmethod

class BaseStore(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_all_teams(self):
        pass

    @abstractmethod
    def add_team(self, name):
        pass

    @abstractmethod
    def get_pending_reports(self):
        pass

    @abstractmethod
    def find_captain_by_token_or_pin(self, token_or_pin):
        pass
