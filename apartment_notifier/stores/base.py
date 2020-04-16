from apartment_notifier.models import User


class Store:
    def get(self, pk):
        raise NotImplemented

    def get_or_create(self, pk, *args, **kwargs):
        raise NotImplemented

    def save(self, instance: User):
        raise NotImplemented

    def all(self):
        raise NotImplemented

    def delete(self, pk):
        raise NotImplemented
