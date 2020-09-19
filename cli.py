import argparse
import os
from os import path

from wl import Watchlist, InvalidStatusError, ItemNotFoundError, STATUSES


def print_item(name, status):
    print(f'{name} => {status}')


def wl_status(status: str) -> str:
    status = status.lower()
    if status not in STATUSES:
        raise argparse.ArgumentTypeError(
            "must be one of " + ', '.join(STATUSES))

    return status


wl = None
fieldnames = ['name', 'status']

filename = os.path.expanduser('~/wl')
if 'WL_PATH' in os.environ:
    filename = os.path.expanduser(os.environ['WL_PATH'])

read_required = False
write_required = False

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    dest='command', help='thingo', required=True)

add_parser = subparsers.add_parser('add', help='add an item')
add_parser.add_argument('name', help="name of the new item")
add_parser.add_argument(
    '-s', '--status',
    help='status to filter by',
    default='unwatched',
    type=wl_status
)

remove_parser = subparsers.add_parser(
    'remove', aliases=['rm'], help='remove an item')
remove_parser.add_argument('name', help='name of the item to remove')

update_parser = subparsers.add_parser(
    'update',
    help='update the status of an item'
)
update_parser.add_argument('name', help="name of the item to update")
update_parser.add_argument(
    'status',
    help="updated status of the item",
    default="watched",
    nargs="?",
    type=wl_status
)

search_parser = subparsers.add_parser('search', help="search for an item")
search_parser.add_argument('search', help='search string')
search_parser.add_argument(
    '-s', '--status',
    help='status to filter by',
    default='unwatched',
    type=wl_status
)

list_parser = subparsers.add_parser('list', help='list all items')

summary_parser = subparsers.add_parser(
    'summary',
    help="show a summary of your watch list"
)

args = parser.parse_args()

# print(args)

try:
    wl = Watchlist.from_file(filename)
except FileNotFoundError:
    wl = Watchlist()

if args.command == 'add':
    wl.add(args.name, args.status)
    write_required = True

elif args.command == 'update':
    wl.update(args.name, args.status)
    write_required = True

elif args.command == 'remove':
    wl.remove(args.name)
    write_required = True

elif args.command == 'list':
    for item in wl:
        print_item(**item)

elif args.command == 'search':
    results = wl.search(args.search, args.status)
    for item in results:
        print_item(**item)

elif args.command == 'summary':
    total = 0
    summary = wl.summary()
    status_col_width = len(max(STATUSES, key=len)) + 1
    count_col_width = len(str(max(summary.values())))

    for status, count in summary.items():
        total += count
        print(
            f' {status.ljust(status_col_width)} | {str(count).rjust(count_col_width)}'
        )

    print('-'*(status_col_width + count_col_width + 3 + 2))

    print(f' {"total".ljust(status_col_width)} | {str(total).rjust(count_col_width)}')


if wl and write_required:
    wl.to_file(filename)
