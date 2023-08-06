#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys

def output():
    print("Hello world")


def main():
    output()
    print(sys.argv[1:])

if __name__ == '__main__':
    main()
