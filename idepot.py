#=======================================================================
"""
Manage software installations using symlinks
"""
#-----------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020 Infinnovation Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#=======================================================================
from __future__ import print_function
import sys
import os
import logging

default_dirs = ('bin',
                'lib',
                'lib/python',
                'etc',
                'man/man1',
                'man/man3')

class AppError(Exception): pass

_log = logging.getLogger('idepot')

class Depot(object):
    def __init__(self, base, static_dirs, log=_log):
        self.base = base        # E.g. /usr/local
        self.static_dirs = static_dirs
        self.log = log
        self.depot = os.path.join(base, 'DEPOT')
        if not os.path.exists(self.depot):
            raise AppError('No depot in %s' % base)

    def commit(self, product, version, dryrun=False):
        proddir = os.path.join(self.depot, product)
        if not os.path.isdir(proddir):
            raise AppError('No such product %s' % product)
        vsndir = os.path.join(proddir, version)
        if not os.path.isdir(vsndir):
            raise AppError('Version %s of %s not installed' %
                           (version, product))
        # See which links to add or remove
        active = os.path.join(proddir, 'ACTIVE')
        if os.path.exists(active):
            oldvsn = os.readlink(active)
            if oldvsn == version:
                self.log.warn('Already at version %s' % version)
                return          # Nothing to do
            self.log.info('Replacing version %s' % oldvsn)
            oldlinks = self._vsn_links(active)
        else:
            self.log.info('No previous version')
            oldlinks = []
        newlinks = self._vsn_links(vsndir)
        addlinks = set(newlinks) - set(oldlinks)
        remlinks = set(oldlinks) - set(newlinks)
        # Create any new links needed
        for path, item in addlinks:
            # ln -s ../../depot/$prod/ACTIVE/man/man3/$func.3
            src= os.path.join(self.base, path, item)
            dots = os.path.join(*(['..'] * len(path.split('/'))))
            dest = os.path.join(dots, depot, product, 'ACTIVE', path, item)
            self.log.debug('%s -> %s', src, dest)
            if dryrun:
                print('ln -s %s %s' % (dest, src))
            else:
                os.symlink(dest, src)
        # Switch ACTIVE to point to new version
        if dryrun:
            print('ln -sf %s %s' % (version, active))
        else:
            try:
                os.unlink(active)
            except OSError: pass
            os.symlink(version, active)
        # Remove any redundant links
        for path, item in remlinks:
            src = os.path.join(self.base, path, item)
            if dryrun:
                print('rm %s' % src)
            else:
                os.unlink(src)

    def _vsn_links(self, instdir):
        links = []
        for path in self.static_dirs:
            sub = os.path.join(instdir, path)
            if os.path.exists(sub):
                for item in os.listdir(sub):
                    links.append((path, item))
        return links

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('-v','--verbose',
                    action='store_const', dest='level', const=logging.INFO,
                    default=logging.WARNING,
                    help='Show progress')
    ap.add_argument('-d','--debug',
                    action='store_const', dest='level', const=logging.DEBUG,
                    help='Show detailed information')
    ap.add_argument('-b','--basedir', default='/usr/local',
                    help='Base directory with bin, lib subdirectories etc.')
    sub = ap.add_subparsers(dest='method', metavar='method')
    #
    m_commit = sub.add_parser('commit',
                              help='Commit a version')
    m_commit.add_argument('-n','--dryrun', action='store_true',
                          help='Show commands without executing them')
    m_commit.add_argument('product',
                          help='Product name')
    m_commit.add_argument('version',
                          help='Version')
    #
    args = ap.parse_args()
    logging.basicConfig(level=args.level)
    try:
        depot = Depot(args.basedir, default_dirs)
        if args.method == 'commit':
            depot.commit(args.product, args.version,
                         dryrun=args.dryrun)
        else:
            raise NotImplementedError
    except AppError as e:
        print('%s: %s' % (ap.prog, e),
              file=sys.stderr)
        sys.exit(1)

if __name__=='__main__':
    main()
