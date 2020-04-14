from dataclasses import dataclass

from arrow import Arrow


@dataclass
class Apartment:
    source: str
    source_id: str
    location: str
    photo: str
    price: str
    price_currency: str
    link: str
    created_at: Arrow
    last_time_up: Arrow

    @property
    def created_at_humanized(self) -> str:
        return self.created_at.to("Europe/Minsk").format("YYYY-MM-DD HH:mm:ss")

    @property
    def last_time_up_humanized(self) -> str:
        return self.last_time_up.to("Europe/Minsk").format("YYYY-MM-DD HH:mm:ss")
