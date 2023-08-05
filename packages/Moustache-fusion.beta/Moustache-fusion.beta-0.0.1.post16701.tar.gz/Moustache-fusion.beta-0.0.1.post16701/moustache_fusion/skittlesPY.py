#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from itertools import count, product
from string import ascii_uppercase
import sys
import os
import traceback

PDFTK_PATH = '/usr/bin/pdftk'
PDFINFO_PATH = '/usr/bin/pdfinfo'
PDFGREP_PATH = '/usr/bin/pdfgrep'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def dprint(*args, **kwargs):
    if getdebugflag():
        print(*args, file=sys.stderr, **kwargs)


debugflag = False


def setdebugflag(f):
    global debugflag
    debugflag = f


def getdebugflag():
    global debugflag
    return debugflag


# alphabet de lettre (A,B, ..., AB, AC)
def multiletters(seq):
    for n in count(1):
        for s in product(seq, repeat=n):
            yield ''.join(s)


letter = multiletters(ascii_uppercase)


def set_annexes_length(annexes):
    for annexe in annexes:
        dprint("exec %s %s" % (PDFINFO_PATH, annexe['name']))
        output = subprocess.run([PDFINFO_PATH, annexe['name']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode:
            raise Exception(output.stderr.decode('utf-8'))
        output_array = output.stdout.decode('utf-8').split()
        pageinfo = output_array.index("Pages:")
        annexe["length"] = output_array[pageinfo + 1]
        if not annexe["length"].isdigit():
            raise Exception("Impossible de lire le nombre de pages dans %s" % annexe['name'])
        dprint("%s pages:%d" % (annexe['name'], int(annexe["length"])))


# find only one + cache file speed +++
# pdfgrep -n --max-count 1 --cache "challenge" principal.pdf
# find pattern page
# TODO test if not null
def set_annexe_pattern_pages(annexes, document_path):
    for annex in annexes:
        annex["alias"] = next(letter)
        # ubuntu 16.04 ships with pdfgrep 1.4 which does not support '--cache' parameter
        # cmd = '{0} -n --max-count 1 --cache "{1}" {2}'.format(PDFGREP_PATH, annex["pattern"], documentPath)
        cmd = '{0} -n --max-count 1 --cache "{1}" {2}'.format(PDFGREP_PATH, annex["pattern"], document_path)
        dprint("exec %s" % cmd)
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        outds, errs = res.communicate()
        if res.returncode:
            if not errs:
                errs = "erreur %s" % PDFGREP_PATH
            raise Exception(errs)
        v = outds.split(':')[0]
        if not v.isdigit():
            raise Exception("Impossible de lire la page de départ pour %s" % annex['name'])
        annex["startPage"] = int(v)
        dprint("%s page de départ:%d" % (annex['name'], int(v)))


# create and execute script to replace annexes
#  cmd = "/usr/bin/pdftk A=main.pdf B=annexe.pdf cat A1-10 B A12-end output generated.pdf"
# TODO test if not null
def replace_annexes(docs, outputfile):
    # generate aliases (/usr/bin/pdftk A=main.pdf B=annexe.pdf)
    docs["general"]["alias"] = next(letter)

    cmd = "{0} {1}={2} ".format(PDFTK_PATH, docs["general"]["alias"], docs["general"]["name"])

    for annex in docs["annexes"]:
        annex["alias"] = next(letter)
        # cmd += annex["alias"] + "=" + annex["name"] + " "
        cmd += "{0}={1} ".format(annex["alias"], annex["name"])

    # (cat A1-10 B A12-end output generated.pdf)
    cmd += "cat "
    general_doc_position = 1

    for annex in docs["annexes"]:
        cmd += "{0}{1}-{2} {3} ".format(docs["general"]["alias"], general_doc_position, annex["startPage"] - 1,
                                        annex["alias"])
        general_doc_position = annex["startPage"] + int(annex["length"])

    cmd += "{0}{1}-end output {2}".format(docs["general"]["alias"], general_doc_position, outputfile)

    dprint(cmd)
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    outds, errs = res.communicate()
    if res.returncode:
        raise Exception(errs)


def add_page_numbering_to_annexes(docs):
    for annexe in docs["annexes"]:
        start = int(annexe["startPage"])
        end = start + int(annexe["length"])
        existing_pdf = PdfFileReader(open(annexe["name"], "rb"))
        output = PdfFileWriter()
        increment = 0
        while start < end:
            packet = io.BytesIO()
            le_can = canvas.Canvas(packet, pagesize=A4)
            le_can.setFont('Helvetica', 10)
            le_can.drawString(200, 20, "{0}".format(start))
            le_can.save()

            # move to the beginning of the buffer
            packet.seek(0)
            new_pdf = PdfFileReader(packet)

            dprint("{0} {1} {2}".format(increment, start, end))
            page = existing_pdf.getPage(increment)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)
            increment += 1
            start += 1

        # finally, write "output" to a real file
        new_annexe_name = "{0}_{1}.pdf".format(annexe["name"], annexe["alias"])
        output_stream = open(new_annexe_name, "wb")
        output.write(output_stream)
        output_stream.close()
        annexe["name"] = new_annexe_name


def skyttles(parameters, outputfile, debug):
    try:
        setdebugflag(debug)
        set_annexes_length(parameters["annexes"])
        set_annexe_pattern_pages(parameters["annexes"], parameters["general"]["name"])
        no_page_numbering = parameters["options"]["nopagenumbering"]
        if not no_page_numbering:
            add_page_numbering_to_annexes(parameters)
        else:
            dprint("skip add_page_numbering_to_annexes")
        replace_annexes(parameters, outputfile)

        # cleanup
        if not no_page_numbering:
            for annexe in parameters["annexes"]:
                os.remove(annexe["name"])

        dprint("file created: %s" % outputfile)
        return True
    except Exception as e:
        eprint(traceback.format_exc())
        return str(e)
