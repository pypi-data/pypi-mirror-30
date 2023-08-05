# -*- coding:utf-8 -*-
# Author：hankcs
# Date: 2018-03-19 01:05
import sys

import argparse

from pyhanlp import HanLP
from pyhanlp.static import eprint, PATH_CONFIG


def main():
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    arg_parser = argparse.ArgumentParser(description='HanLP: Han Language Processing')
    task_parser = arg_parser.add_subparsers(dest="task", help='which task to perform?')
    segment_parser = task_parser.add_parser(name='segment', help='word segmentation')
    parse_parser = task_parser.add_parser(name='parse', help='dependency parsing')

    def add_args(p):
        p.add_argument("--config", default=PATH_CONFIG,
                       help='path to hanlp.properties')
        # p.add_argument("--action", dest="action", default='predict',
        #                help='Which action (train, test, predict)?')

    add_args(segment_parser)
    add_args(parse_parser)
    args = arg_parser.parse_args()

    def die(msg):
        eprint(msg)
        exit(1)

    if args.task == 'segment':
        for line in sys.stdin:
            line = line.strip()
            print(' '.join(term.toString() for term in HanLP.segment(line)))
    elif args.task == 'parse':
        for line in sys.stdin:
            line = line.strip()
            print(HanLP.parseDependency(line))


if __name__ == '__main__':
    main()
