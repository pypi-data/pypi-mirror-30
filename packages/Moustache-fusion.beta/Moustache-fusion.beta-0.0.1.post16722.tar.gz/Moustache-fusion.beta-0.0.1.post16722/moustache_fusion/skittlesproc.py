#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import sys
from moustache_fusion import skittlesPY
import json
import os


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def usage():
    print("usage :")
    print("-i --in=conffile\tfichier de paramètres")
    print("-o --out=pdfoutfile\tfichier pdf de sortie")
    print("-d --debug\tactive les traces sur stderr")


def normalize_parameters(parameters, filepath):
    filepath = os.path.realpath(filepath)
    dirname = os.path.dirname(filepath)

    name = parameters["general"]["name"]
    if not os.path.isabs(name):
        parameters["general"]["name"] = os.path.join(dirname, name)

    for annexe in parameters["annexes"]:
        if not os.path.isabs(annexe["name"]):
            annexe["name"] = os.path.join(dirname, annexe["name"])

    return parameters


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:d", ["help", "in=", "out=", "debug"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    inparam = None
    outparam = None
    debugparam = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-i", "--in"):
            inparam = a
        elif o in ("-o", "--out"):
            outparam = a
        elif o in ("-d", "--debug"):
            debugparam = True
        else:
            print("unhandled option")
            usage()
            sys.exit(1)

    if inparam is None or outparam is None:
        usage()
        sys.exit(1)

    if not os.path.isfile(inparam):
        eprint("%s not found" % inparam)
        sys.exit(1)

    try:
        with open(inparam) as json_data:
            parameters = json.load(json_data)
    except Exception as e:
        eprint("%s invalid format\n%s" % (inparam, e))
        sys.exit(1)

    parameters = normalize_parameters(parameters, inparam)

    res = skittlesPY.skyttles(parameters, outparam, debugparam)
    if res is not True:
        eprint(res)
        sys.exit(1)


if __name__ == "__main__":
    main()
