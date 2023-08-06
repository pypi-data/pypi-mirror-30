#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ctfile command-line interface

Usage:
    ctfile -h | --help
    ctfile --version
    ctfile view <path-to-file>

Options:
    -h, --help                      Show this screen.
    -v, --verbose                   Print what files are processing.
    --version                       Show version.
"""

def cli(cmdargs):
    if cmdargs['view']:
        pass