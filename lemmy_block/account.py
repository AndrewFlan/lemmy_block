"""Account Class"""
from dataclasses import dataclass, field


@dataclass
class Account:
    """Class for Lemmy Account information"""

    account: str
    site: str
    user: str
    password: str = field(repr=False)
