"""BlockCommunity Class"""
from dataclasses import dataclass


@dataclass
class BlockCommunity:
    """Class for Community to Block information"""

    name: str
    instance: str
    block: bool = True
