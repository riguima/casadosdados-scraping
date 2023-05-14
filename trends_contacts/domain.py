from dataclasses import dataclass


@dataclass
class SearchInfo:
    cnae: str
    state: str
    city: str


@dataclass
class Contact:
    name: str
    phone_number: int
    location: str
    cnae: str
