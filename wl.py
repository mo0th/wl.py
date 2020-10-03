import csv
from typing import List, Dict, Iterator, Iterable
import typing

FIELD_NAMES = ['name', 'status']
STATUSES = ['unwatched', 'watching', 'watched', 'on hold', 'dropped']

WatchListItem = Dict[str, str]


class ItemNotFoundError(Exception):
    """Exception raised when no matching item is found"""


class InvalidStatusError(Exception):
    """Exception raised when an invalid status is used"""


class Watchlist:
    def __init__(self, items=None):
        if items == None:
            self._items = []
            self._len = 0
        else:
            self._items = items
            self._len = len(self._items)

    def add(self, name: str, status: str = None):
        if status is None:
            status = 'unwatched'
        elif status not in STATUSES:
            raise InvalidStatusError

        for item in self.search(name):
            if item['name'] == name:
                confirm = input(f"'{name}' already exists. Add anyway? [y/N]")
                if confirm.lower() not in ['y', 'ye', 'yes']:
                    return print("No items were added")

        self._items.append({'name': name, 'status': status})
        self._len += 1

    @property
    def items(self):
        return self._items

    def search(self, search_string: str, status: str = None) -> Iterable[WatchListItem]:
        if status is None:
            return filter(lambda i: search_string in i['name'], self)
        elif status not in STATUSES:
            raise InvalidStatusError
        else:
            return filter(lambda i: search_string in i['name'] and i['status'] == status, self)

    def update(self, name: str, status: str):
        if status is None:
            status = 'watched'
        elif status not in STATUSES:
            raise InvalidStatusError

        for item in self._items:
            if item['name'] == name:
                item['status'] = status
                break
        else:
            raise ItemNotFoundError

    def remove(self, name: str):
        self._items = [i for i in self._items if i['name'] != name]

        if len(self._items) == self._len:
            raise ItemNotFoundError

        self._len -= 1

    def summary(self, statuses: List[str] = None) -> Dict[str, int]:
        if statuses is None:
            statuses = STATUSES

        result = dict.fromkeys(statuses, 0)

        for item in self._items:
            if item['status'] in statuses:
                result[item['status']] += 1

        return result

    def to_file(self, filename: str):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)

            writer.writerows(self._items)

    @staticmethod
    def from_file(filename: str) -> List[WatchListItem]:
        items = None
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, fieldnames=FIELD_NAMES)
            return Watchlist([r for r in reader])

    def __iter__(self) -> Iterator[WatchListItem]:
        return iter(self._items)

    def __len__(self) -> int:
        return self._len
