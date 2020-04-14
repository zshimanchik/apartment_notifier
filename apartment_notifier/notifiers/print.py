from dataclasses import asdict
from pprint import pprint
from typing import List

from apartment_notifier.models import Apartment


class PrintNotifier:
    def notify(self, apartments: List[Apartment]):
        for apartment in apartments:
            print('==='*3)
            pprint(asdict(apartment))
