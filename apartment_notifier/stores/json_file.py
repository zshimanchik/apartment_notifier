import json

from apartment_notifier.models import User
from apartment_notifier.stores import ObjectDoesNotExist
from apartment_notifier.stores.base import Store


class JsonFileStore(Store):
    def __init__(self, filename):
        self.filename = filename

    def get(self, pk):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ObjectDoesNotExist()
        data['store'] = self
        return User.from_dict(data)

    def get_or_create(self, pk, *args, **kwargs):
        try:
            return self.get(pk), False
        except ObjectDoesNotExist:
            user = User(pk=pk, store=self, *args, **kwargs)
            self.save(user)
            return user, True

    def save(self, instance: User):
        with open(self.filename, 'w') as f:
            json.dump(instance.to_dict(), f, indent=2)

    def all(self):
        try:
            yield self.get(0)
        except ObjectDoesNotExist:
            pass
