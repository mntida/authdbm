#!/usr/bin/env python
import sys
import os
import argparse

from authdbm import AuthDbm, AuthGroup


def read_dbm(filename):
    sys.stdin.close()
    groups = AuthGroup(AuthDbm.read_file(filename))

    print >>sys.stderr, 'Contents of "{}" are:'.format(filename)
    print >>sys.stderr, '-' * 32
    for groupname in sorted(groups.get_groups()):
        print groupname + ':',
        print ' '.join(sorted(groups.users_in_group(groupname)))

def write_dbm(filename):
    groups = AuthGroup()

    for line in sys.stdin:
        tokens = line.split()
        groupname = tokens[0].rstrip(':')
        usernames = tokens[1:]
        for username in usernames:
            groups.add_group(username, groupname)

    if groups.db:
        AuthDbm.write_file(filename, groups.db)

    print >>sys.stderr, 'Generated file "{}"'.format(filename)
    read_dbm(filename)

def main():

    parser = argparse.ArgumentParser(
        description="""Manage DBM-formatted authorization groups for apache.

  You can display or generate a DBM-formatted file, based on specified
options.  To generate a file, use the "-g (--generate)" option, and
supply text-formatted data on standard input.  To only display the
contents of a DBM-formatted file, do not specify the "-g (--generate)"
option.

  In both cases, you must supply the name of the DBM-formatted file
with "-f (--filename)".  The format expected on standard input is the
same format which is outputted.  It is the text-based format which
Apache uses for AuthGroupFile.""")

    parser.add_argument('-g', '--generate', action='store_true',
                        help='Generate DBM file.')
    parser.add_argument('-f', '--filename', required=True,
                        help='Name of DBM-formatted file to display or edit.') 
    args = parser.parse_args()

    if args.generate:
        write_dbm(args.filename)
    else:
        read_dbm(args.filename)

    sys.exit(0)

if __name__ == '__main__':
    main()
