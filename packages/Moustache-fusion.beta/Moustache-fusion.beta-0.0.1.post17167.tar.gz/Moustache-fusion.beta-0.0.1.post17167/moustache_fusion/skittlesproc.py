#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import sys
import skittlesPY
import json
import os
import logging
from logging.config import fileConfig

logger = logging.getLogger()


def usage():
    print("usage :")
    print("-i --in=pdfinfile\tfichier pdf d'entrée")
    print("-c --conf=conffile\tfichier de paramètres")
    print("-o --out=pdfoutfile\tfichier pdf de sortie")
    print("-d --debug\t\tactive les traces sur stderr")
    print("-l --logger=loggerfile\t\tfichier de configuration du logger")


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


def setlogger(conffile):
    if not os.path.isfile(conffile):
        logger.error("Can't access %s" % conffile)
        sys.exit(1)

    fileConfig(conffile)
    logger.debug("Using %s for logging config file" % conffile)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:c:o:dl=", ["help", "in=", "conf=", "out=", "debug", "logger="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(1)

    inparam = None
    confparam = None
    outparam = None
    debugparam = False
    loggerparam = None

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
        elif o in ("-l", "--logger"):
            loggerparam = a
        else:
            print("unhandled option")
            usage()
            sys.exit(1)

    if loggerparam:
        setlogger(loggerparam)

    if inparam is None or confparam is None or outparam is None:
        usage()
        sys.exit(1)

    if not os.path.isfile(inparam):
        logger.error("%s not found" % inparam)
        sys.exit(1)

    if not os.path.isfile(confparam):
        logger.error("%s not found" % confparam)
        sys.exit(1)
    try:
        with open(confparam) as json_data:
            parameters = json.load(json_data)
    except Exception as e:
        logger.error("%s invalid format\n%s" % (confparam, e))
        sys.exit(1)

    parameters = normalize_parameters(parameters, inparam, confparam)

    res = skittlesPY.skittles(parameters, outparam, debugparam)
    if res is not True:
        logger.error(res)
        sys.exit(1)


if __name__ == "__main__":
    main()
