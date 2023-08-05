#!/usr/bin/env python2.7
# encoding: utf-8

import argparse
import re
import os
import sys


def truncate_str(str, n=35, end=True, mark='…'):
    """
    Convenience function to truncate a string to n characters, and end or begin
    with an ellipsis (if it exceeds n characters)

    :param str: The string to truncate
    :param n: The length to truncate to
    :param end: True to truncate the end, False to truncate the start
    :param mark: The mark to use; defaults to an ellipsis

    :returns: The truncated string
    """
    assert len(mark) < n

    if len(str) <= n:
        return str

    n -= len(mark)

    return str[:n] + mark if end else mark + str[-n:]


def sort_dir(dir_listing):
    """
    Sort the given directory listing into alphabetical order, separating
    directories and files. Return a tuple (dirs, files), where both entries are
    lists of strings.
    """
    dirs = []
    files = []

    for f in dir_listing:
        if os.path.isdir(f):
            dirs.append(f)
        else:
            files.append(f)

    dirs.sort()
    files.sort()

    return dirs, files


def mass_rename(args, dir):
    """
    Compare all files in the specified directory against the given pattern,
    and rename them according to the given replacement. Read arguments
    directly from the script's args and recurse if needed.
    """
    dirs, files = sort_dir(os.listdir(dir))

    if args.recursive:
        for subdir in dirs:
            mass_rename(os.path.join(dir, subdir))

    if files and (args.verbosity > 0 or args.dry):
        print '[\x1b[0;36m%s\x1b[0m]' % truncate_str(dir, 70, False)

    for file in files:
        if not args.pattern.search(file):
            continue

        dest = re.sub(args.pattern, args.replacement, file)

        if args.verbosity > 0 or args.dry:
            sys.stdout.write(
                '%s \x1b[1;33m-->\x1b[0m %s' % (
                    truncate_str(file), truncate_str(dest)
                )
            )
            sys.stdout.flush()

        if args.dry:
            print ''
            continue

        try:
            os.rename(os.path.join(dir, file), os.path.join(dir, dest))
            if args.verbosity > 0:
                print '  [ \x1b[1;32mOK\x1b[0m ]'
        except:
            if args.verbosity > 0:
                print '  [ \x1b[1;31mFAILED\x1b[0m ]'

            if not args.force:
                if args.verbosity > 1:
                    raise
                else:
                    sys.exit(1)


def entrypoint():
    parser = argparse.ArgumentParser('Regex renamer')
    parser.add_argument('pattern')
    parser.add_argument('replacement')
    parser.add_argument(
        '-d', '--dry-run', dest='dry', action='store_true',
        help='Show changes which will be made, but do not make them'
    )
    parser.add_argument(
        '-f', '--force', dest='force', action='store_true',
        help=(
            'Do not fail fast if there\'s an error in renaming: '
            'continue processing'
        )
    )
    parser.add_argument(
        '-r', '-R', '--recursive', dest='recursive', action='store_true',
        help='Whether or not to rename recursively'
    )
    parser.add_argument(
        '-v', '--verbosity', dest='verbosity', type=int, default=1
    )
    args = parser.parse_args()

    # Compile the regex, in case we're doing a large batch of renames
    args.pattern = re.compile(args.pattern)

    # Process the current working directory
    mass_rename(args, os.getcwd())


if __name__ == '__main__':
    entrypoint()
