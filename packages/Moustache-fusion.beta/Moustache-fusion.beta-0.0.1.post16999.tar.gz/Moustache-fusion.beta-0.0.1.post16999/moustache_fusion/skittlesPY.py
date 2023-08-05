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
import tempfile

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
        v = output_array[pageinfo + 1]
        if not v.isdigit():
            raise Exception("Impossible de lire le nombre de pages dans %s:%s" % (annexe['name'], v))
        annexe["length"] = int(v)
        dprint("%s pages:%d" % (annexe['name'], annexe["length"]))


# find only one + cache file speed +++
# pdfgrep -n --cache "challenge" principal.pdf
# find pattern page
# TODO test if not null
def set_annexe_pattern_pages(annexes, document_path):
    new_annexes = []
    for annex in annexes:
        # ubuntu 16.04 ships with pdfgrep 1.4 which does not support '--cache' parameter
        # cmd = '{0} -n --cache "{1}" {2}'.format(PDFGREP_PATH, annex["pattern"], documentPath)
        cmd = '{0} -n --cache "{1}" {2}'.format(PDFGREP_PATH, annex["pattern"], document_path)
        dprint("exec %s" % cmd)
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        outds, errs = res.communicate()
        if res.returncode:
            if not errs:
                errs = "%s retourne %d" % (PDFGREP_PATH, res.returncode)
            raise Exception(errs)

        outds = outds.split()
        for line in outds:
            v = line.split(":")[0]
            if not v.isdigit():
                raise Exception("Impossible de lire la page de départ pour %s" % annex['name'])
            annex["alias"] = next(letter)
            annex["startPage"] = int(v)
            new_annexes.append(dict(annex))
            dprint("%s alias=%s start page=%d" % (annex['name'], annex["alias"], annex["startPage"]))
    return new_annexes


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
        if general_doc_position <= annex["startPage"] - 1:
            cmd += "{0}{1}-{2} {3} ".format(docs["general"]["alias"], general_doc_position, annex["startPage"] - 1,
                                        annex["alias"])
        else:
            cmd += "{0} ".format(annex["alias"])

        general_doc_position = annex["startPage"] + annex["length"]

    cmd += "{0}{1}-end output {2}".format(docs["general"]["alias"], general_doc_position, outputfile)

    dprint(cmd)
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    outds, errs = res.communicate()
    if res.returncode:
        raise Exception(errs)


def add_page_numbering_to_annexes(docs):
    for annexe in docs["annexes"]:
        start = annexe["startPage"]
        existing_pdf = PdfFileReader(open(annexe["name"], "rb"))
        output = PdfFileWriter()
        end = start + annexe["length"]
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

            dprint("%s cur=%d [%d-%d]" % (annexe["name"], increment, start, end))
            page = existing_pdf.getPage(increment)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)
            increment += 1
            start += 1

        # finally, write "output" to a real file
        new_annexe_name = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
        output_stream = open(new_annexe_name, "wb")
        output.write(output_stream)
        output_stream.close()
        dprint("%s to %s" % (annexe["name"], new_annexe_name))
        annexe["name"] = new_annexe_name


def skyttles(parameters, outputfile, debug):
    try:
        setdebugflag(debug)
        set_annexes_length(parameters["annexes"])
        parameters["annexes"] = set_annexe_pattern_pages(parameters["annexes"], parameters["general"]["name"])
        try:
            no_page_numbering = parameters["options"]["nopagenumbering"]
        except KeyError:
            no_page_numbering = False
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
