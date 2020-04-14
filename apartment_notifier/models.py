from dataclasses import dataclass


@dataclass
class Apartment:
    source: str
    source_id: str
    location: str
    photo: str
    price: str
    price_currency: str
    link: str
    created_at: str
    last_time_up: str
