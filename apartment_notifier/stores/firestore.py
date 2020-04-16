from apartment_notifier.models import User
from apartment_notifier.stores.base import Store
from apartment_notifier.stores.exceptions import ObjectDoesNotExist


class FireStore(Store):
    def __init__(self):
        from google.cloud import firestore
        self.db = firestore.Client()

    def get(self, pk):
        ds = self.db.collection('users').document(str(pk)).get()
        if not ds.exists:
            raise ObjectDoesNotExist("Object does not exist")
        data = ds.to_dict()
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
        data = instance.to_dict()
        self.db.collection('users').document(str(instance.pk)).set(data)

    def all(self):
        for document_snapshot in self.db.collection('users').stream():
            data = document_snapshot.to_dict()
            data['store'] = self
            yield User.from_dict(data)

    def delete(self, pk):
        self.db.collection('users').document(str(pk)).delete()
