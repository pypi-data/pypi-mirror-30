#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import sys
import skittlesPY
import json
import os


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def usage():
    print("usage :")
    print("-i --in=pdfinfile\tfichier pdf d'entrée")
    print("-c --conf=conffile\tfichier de paramètres")
    print("-o --out=pdfoutfile\tfichier pdf de sortie")
    print("-d --debug\t\tactive les traces sur stderr")


def normalize_parameters(parameters, infile, filepath):
    filepath = os.path.realpath(filepath)
    dirname = os.path.dirname(filepath)

    if not os.path.isabs(infile):
        # pdf en entrée : si relatif par rapport au cwd
        infile = os.path.realpath(infile)
    parameters["general"] = dict()
    parameters["general"]["name"] = infile

    for annexe in parameters["annexes"]:
        if not os.path.isabs(annexe["name"]):
            # les annexes en relatif par rapport au fichier de config
            annexe["name"] = os.path.realpath(os.path.join(dirname, annexe["name"]))

    return parameters


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:o:d", ["help", "in=", "conf=", "out=", "debug"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    inparam = None
    confparam = None
    outparam = None
    debugparam = False

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-i", "--in"):
            inparam = a
        elif o in ("-c", "--conf"):
            confparam = a
        elif o in ("-o", "--out"):
            outparam = a
        elif o in ("-d", "--debug"):
            debugparam = True
        else:
            print("unhandled option")
            usage()
            sys.exit(1)

    if inparam is None or confparam is None or outparam is None:
        usage()
        sys.exit(1)

    if not os.path.isfile(inparam):
        eprint("%s not found" % inparam)
        sys.exit(1)

    if not os.path.isfile(confparam):
        eprint("%s not found" % confparam)
        sys.exit(1)
    try:
        with open(confparam) as json_data:
            parameters = json.load(json_data)
    except Exception as e:
        eprint("%s invalid format\n%s" % (confparam, e))
        sys.exit(1)

    parameters = normalize_parameters(parameters, inparam, confparam)

    res = skittlesPY.skyttles(parameters, outparam, debugparam)
    if res is not True:
        eprint(res)
        sys.exit(1)


if __name__ == "__main__":
    main()
