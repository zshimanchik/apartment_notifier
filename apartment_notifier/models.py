from dataclasses import dataclass

import arrow
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


@dataclass
class User:
    pk: int
    chat_id: int
    last_check_datetime: Arrow = None
    onlinerby_url: str = None
    store: object = None

    def to_dict(self):
        return {
            'pk': self.pk,
            'chat_id': self.chat_id,
            'last_check_datetime': self.last_check_datetime.isoformat() if self.last_check_datetime else None,
            'onlinerby_url': self.onlinerby_url,
        }

    @classmethod
    def from_dict(cls, d):
        if d.get('last_check_datetime'):
            d['last_check_datetime'] = arrow.get(d['last_check_datetime'])
        return User(**d)

    def save(self, store=None):
        store = store if store is not None else self.store
        if store is None:
            raise RuntimeError("Can't save model without store")
        store.save(self)
