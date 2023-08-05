#!/usr/bin/env python
"""
This is the main function to call for disambiguating between BAM files
from two species that have alignments from the same source of fastq files.
It is part of the explant RNA/DNA-Seq workflow where an informatics
approach is used to distinguish between e.g. human and mouse or rat RNA/DNA reads.

For reads that have aligned to both organisms, the functionality is based on
comparing quality scores from either Tophat, Hisat2, STAR or BWA. Read
name is used to collect all alignments for both mates (_1 and _2) and
compared between the alignments from the two species.

For Tophat (default, can be changed using option -a) and Hisat2, the sum of the flags XO,
NM and NH is evaluated and the lowest sum wins the paired end reads. For equal
scores, the reads are assigned as ambiguous.

The alternative algorithm (STAR, bwa) disambiguates (for aligned reads) by tags
AS (alignment score, higher better), followed by NM (edit distance, lower
better).

Code by Miika Ahdesmaki July-August 2013, based on original Perl implementation
for Tophat by Zhongwu Lai.
"""


from __future__ import print_function
import sys
import re
import pysam
from array import array
from os import path, makedirs
from argparse import ArgumentParser, RawTextHelpFormatter

DESCRIPTION = """
disambiguate.py disambiguates between two organisms that have alignments
from the same source of fastq files. An example where this might be
useful is as part of an explant RNA/DNA-Seq workflow where an informatics
approach is used to distinguish between human and mouse RNA/DNA reads.

For reads that have aligned to both organisms, the functionality is based on
comparing quality scores from either Tophat of BWA. Read
name is used to collect all alignments for both mates (_1 and _2) and
compared between human and mouse alignments.

For Tophat (default, can be changed using option -a) and Hisat2, the sum of the tags XO,
NM and NH is evaluated and the lowest sum wins the paired end reads. For equal
scores (both mates, both species), the reads are assigned as ambiguous.

The alternative algorithm (STAR, bwa) disambiguates (for aligned reads) by tags
AS (alignment score, higher better), followed by NM (edit distance, lower
better).

The output directory will contain four files:\n
...disambiguatedSpeciesA.bam: Reads that could be assigned to species A
...disambiguatedSpeciesB.bam: Reads that could be assigned to species B
...ambiguousSpeciesA.bam: Reads aligned to species A that also aligned \n\tto B but could not be uniquely assigned to either
...ambiguousSpeciesB.bam: Reads aligned to species B that also aligned \n\tto A but could not be uniquely assigned to either
..._summary.txt: A summary of unique read names assigned to species A, B \n\tand ambiguous.

Examples:
disambiguate.py test/human.bam test/mouse.bam
disambiguate.py -s mysample1 test/human.bam test/mouse.bam
"""

# "natural comparison" for strings

def nat_cmp(a, b):
    # lambda function to convert text to int if number present
    def convert(text): return int(text) if text.isdigit() else text

    # split string to piecewise strings and string numbers
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    #return cmp(alphanum_key(a), alphanum_key(b)) # use internal cmp to compare piecewise strings and numbers
    return (alphanum_key(a) > alphanum_key(b)) - (alphanum_key(a) < alphanum_key(b))

# read reads into a list object for as long as the read qname is constant (sorted file). Return the first read with new qname or None


def read_next_reads(fileobject, listobject):
    qnamediff = False
    while not qnamediff:
        try:
            myRead = next(fileobject)
        except StopIteration:
            #print("5")
            # return None as the name of the new reads (i.e. no more new reads)
            return None
        if nat_cmp(myRead.qname, listobject[0].qname) == 0:
            listobject.append(myRead)
        else:
            qnamediff = True
    return myRead  # this is the first read with a new qname

# disambiguate between two lists of reads


def disambiguate(humanlist, mouselist, disambalgo):
    if disambalgo in ['tophat', 'hisat2']:
        # a high quality score to replace missing quality scores (no real quality score should be this high)
        dv = 2**13
        # score array, with [human_1_QS, human_2_QS, mouse_1_QS, mouse_2_QS]
        sa = array('i', (dv for i in range(0, 4)))
        for read in humanlist:
            if 0x4 & read.flag:  # flag 0x4 means unaligned
                continue
            QScore = read.opt('XO') + read.opt('NM') + read.opt('NH')
           # directionality (_1 or _2)
            d12 = 0 if 0x40 & read.flag else 1
            if sa[d12] > QScore:
                # update to lowest (i.e. 'best') quality score
                sa[d12] = QScore
        for read in mouselist:
            if 0x4 & read.flag:  # flag 0x4 means unaligned
                continue
            QScore = read.opt('XO') + read.opt('NM') + read.opt('NH')
           # directionality (_1 or _2)
            d12 = 2 if 0x40 & read.flag else 3
            if sa[d12] > QScore:
                # update to lowest (i.e. 'best') quality score
                sa[d12] = QScore
        if min(sa[0:2]) == min(sa[2:4]) and max(sa[0:2]) == max(sa[2:4]):  # ambiguous
            return 0
        elif min(sa[0:2]) < min(sa[2:4]) or min(sa[0:2]) == min(sa[2:4]) and max(sa[0:2]) < max(sa[2:4]):
            # assign to human
            return 1
        else:
            # assign to mouse
            return -1
    elif disambalgo.lower() in ('bwa', 'star'):
        dv = -2 ^ 13  # default value, low
        # ,'XS'] # in order of importance (compared sequentially, not as a sum as for tophat)
        bwatags = ['AS', 'NM']
        # ,1] # for AS and XS higher is better. for NM lower is better, thus multiply by -1
        bwatagsigns = [1, -1]
        AS = list()
        for x in range(0, len(bwatagsigns)):
            # alignment score array, with [human_1_Score, human_2_Score, mouse_1_Score, mouse_2_Score]
            AS.append(array('i', (dv for i in range(0, 4))))
        #
        for read in humanlist:
            if 0x4 & read.flag:  # flag 0x4 means unaligned
                continue
            # directionality (_1 or _2)
            d12 = 0 if 0x40 & read.flag else 1
            for x in range(0, len(bwatagsigns)):
                try:
                    QScore = bwatagsigns[x] * read.opt(bwatags[x])
                except KeyError:
                    if bwatags[x] == 'NM':
                        bwatags[x] = 'nM'  # oddity of STAR
                    elif bwatags[x] == 'AS':
                        # this can happen for e.g. hg38 ALT-alignments (missing AS)
                        continue
                    QScore = bwatagsigns[x] * read.opt(bwatags[x])

                if AS[x][d12] < QScore:
                    # update to highest (i.e. 'best') quality score
                    AS[x][d12] = QScore
        #
        for read in mouselist:
            if 0x4 & read.flag:  # flag 0x4 means unaligned
                continue
           # directionality (_1 or _2)
            d12 = 2 if 0x40 & read.flag else 3
            for x in range(0, len(bwatagsigns)):
                try:
                    QScore = bwatagsigns[x] * read.opt(bwatags[x])
                except KeyError:
                    if bwatags[x] == 'NM':
                        bwatags[x] = 'nM'  # oddity of STAR
                    elif bwatags[x] == 'AS':
                        # this can happen for e.g. hg38 ALT-alignments (missing AS)
                        continue
                    QScore = bwatagsigns[x] * read.opt(bwatags[x])

                if AS[x][d12] < QScore:
                    # update to highest (i.e. 'best') quality score
                    AS[x][d12] = QScore
        #
        for x in range(0, len(bwatagsigns)):
            if max(AS[x][0:2]) > max(AS[x][2:4]) or max(AS[x][0:2]) == max(AS[x][2:4]) and min(AS[x][0:2]) > min(AS[x][2:4]):
                # assign to human
                return 1
            elif max(AS[x][0:2]) < max(AS[x][2:4]) or max(AS[x][0:2]) == max(AS[x][2:4]) and min(AS[x][0:2]) < min(AS[x][2:4]):
                # assign to mouse
                return -1
        return 0  # ambiguous
    else:
        print("Not implemented yet")
        sys.exit(2)


def main():
    parser = get_parser()
    args = parser.parse_args()
    run_disambiguate(args)


def get_parser():
    parser = ArgumentParser(description=DESCRIPTION,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('A', help='Input BAM file for species A.')
    parser.add_argument('B', help='Input BAM file for species B.')
    parser.add_argument('-o', '--output-dir', default="disambres",
                        help='Output directory.')
    parser.add_argument('-i', '--intermediate-dir', default="intermfiles",
                        help='Location to store intermediate files')
    parser.add_argument('-d', '--no-sort', action='store_true', default=False,
                        help='Disable BAM file sorting. Use this option if the '
                        'files have already been name sorted.')
    parser.add_argument('-s', '--prefix', default='',
                        help='A prefix (e.g. sample name) to use for the output '
                        'BAM files. If not provided, the input BAM file prefix '
                        'will be used. Do not include .bam in the prefix.')
    parser.add_argument('-a', '--aligner', default='tophat',
                        choices=('tophat', 'hisat2', 'bwa', 'star'),
                        help='The aligner used to generate these reads. Some '
                        'aligners set different tags.')
    return parser


def run_disambiguate(args):
    numhum = nummou = numamb = 0
    #starttime = time.clock()
    # parse inputs
    humanfilename = args.A
    mousefilename = args.B
    samplenameprefix = args.prefix
    outputdir = args.output_dir
    intermdir = args.intermediate_dir
    disablesort = args.no_sort
    disambalgo = args.aligner
    supportedalgorithms = set(['tophat', 'hisat2', 'bwa', 'star'])

    # check existence of input BAM files
    if not (file_exists(humanfilename) and file_exists(mousefilename)):
        sys.stderr.write("\nERROR in disambiguate.py: Two existing input BAM files "
                         "must be specified as positional arguments\n")
        sys.exit(2)
    if len(samplenameprefix) < 1:
        humanprefix = path.basename(humanfilename.replace(".bam", ""))
        mouseprefix = path.basename(mousefilename.replace(".bam", ""))
    else:
        if samplenameprefix.endswith(".bam"):
            # the above if is not stricly necessary for this to work
            samplenameprefix = samplenameprefix[0:samplenameprefix.rfind(
                ".bam")]
        humanprefix = samplenameprefix
        mouseprefix = samplenameprefix
    samplenameprefix = None  # clear variable
    if disambalgo.lower() not in supportedalgorithms:
        print(disambalgo + " is not a supported disambiguation scheme at the moment.")
        sys.exit(2)

    if disablesort:
        # assumed to be sorted externally...
        humanfilenamesorted = humanfilename
        # assumed to be sorted externally...
        mousefilenamesorted = mousefilename
    else:
        if not path.isdir(intermdir):
            makedirs(intermdir)
        humanfilenamesorted = path.join(
            intermdir, humanprefix + ".speciesA.namesorted.bam")
        mousefilenamesorted = path.join(
            intermdir, mouseprefix + ".speciesB.namesorted.bam")
        if not path.isfile(humanfilenamesorted):
            pysam.sort("-n", "-m", "2000000000", "-o",
                       humanfilenamesorted, humanfilename)
        if not path.isfile(mousefilenamesorted):
            pysam.sort("-n", "-m", "2000000000", "-o",
                       mousefilenamesorted, mousefilename)

    # read in human reads and form a dictionary
    myHumanFile = pysam.Samfile(humanfilenamesorted, "rb")
    myMouseFile = pysam.Samfile(mousefilenamesorted, "rb")
    if not path.isdir(outputdir):
        makedirs(outputdir)
    myHumanUniqueFile = pysam.Samfile(path.join(
        outputdir, humanprefix + ".disambiguatedSpeciesA.bam"), "wb", template=myHumanFile)
    myHumanAmbiguousFile = pysam.Samfile(path.join(
        outputdir, humanprefix + ".ambiguousSpeciesA.bam"), "wb", template=myHumanFile)
    myMouseUniqueFile = pysam.Samfile(path.join(
        outputdir, mouseprefix + ".disambiguatedSpeciesB.bam"), "wb", template=myMouseFile)
    myMouseAmbiguousFile = pysam.Samfile(path.join(
        outputdir, mouseprefix + ".ambiguousSpeciesB.bam"), "wb", template=myMouseFile)
    summaryFile = open(path.join(outputdir, humanprefix + '_summary.txt'), 'w')

    #initialise
    try:
        nexthumread = next(myHumanFile)
        nextmouread = next(myMouseFile)
    except StopIteration:
        print("No reads in one or either of the input files")
        sys.exit(2)

    EOFmouse = EOFhuman = False
    prevHumID = '-+=RANDOMSTRING=+-'
    prevMouID = '-+=RANDOMSTRING=+-'
    while not EOFmouse & EOFhuman:
        while not (nat_cmp(nexthumread.qname, nextmouread.qname) == 0):
            # check order between current human and mouse qname (find a point where they're identical, i.e. in sync)
            # mouse is "behind" human, output to mouse disambiguous
            while nat_cmp(nexthumread.qname, nextmouread.qname) > 0 and not EOFmouse:
                myMouseUniqueFile.write(nextmouread)
                if not nextmouread.qname == prevMouID:
                    nummou += 1  # increment mouse counter for unique only
                prevMouID = nextmouread.qname
                try:
                    nextmouread = next(myMouseFile)
                except StopIteration:
                    EOFmouse = True
            # human is "behind" mouse, output to human disambiguous
            while nat_cmp(nexthumread.qname, nextmouread.qname) < 0 and not EOFhuman:
                myHumanUniqueFile.write(nexthumread)
                if not nexthumread.qname == prevHumID:
                    numhum += 1  # increment human counter for unique only
                prevHumID = nexthumread.qname
                try:
                    nexthumread = next(myHumanFile)
                except StopIteration:
                    EOFhuman = True
            if EOFhuman or EOFmouse:
                break
        # at this point the read qnames are identical and/or we've reached EOF
        humlist = list()
        moulist = list()
        if nat_cmp(nexthumread.qname, nextmouread.qname) == 0:
            humlist.append(nexthumread)
            # read more reads with same qname (the function modifies humlist directly)
            nexthumread = read_next_reads(myHumanFile, humlist)
            if not nexthumread:
                EOFhuman = True
            moulist.append(nextmouread)
            # read more reads with same qname (the function modifies moulist directly)
            nextmouread = read_next_reads(myMouseFile, moulist)
            if not nextmouread:
                EOFmouse = True

        # perform comparison to check mouse, human or ambiguous
        if len(moulist) > 0 and len(humlist) > 0:
            myAmbiguousness = disambiguate(humlist, moulist, disambalgo)
            if myAmbiguousness < 0:  # mouse
                nummou += 1  # increment mouse counter
                for myRead in moulist:
                    myMouseUniqueFile.write(myRead)
            elif myAmbiguousness > 0:  # human
                numhum += 1  # increment human counter
                for myRead in humlist:
                    myHumanUniqueFile.write(myRead)
            else:  # ambiguous
                numamb += 1  # increment ambiguous counter
                for myRead in moulist:
                    myMouseAmbiguousFile.write(myRead)
                for myRead in humlist:
                    myHumanAmbiguousFile.write(myRead)
        if EOFhuman:
            #flush the rest of the mouse reads
            while not EOFmouse:
                myMouseUniqueFile.write(nextmouread)
                if not nextmouread.qname == prevMouID:
                    nummou += 1  # increment mouse counter for unique only
                prevMouID = nextmouread.qname
                try:
                    nextmouread = next(myMouseFile)
                except StopIteration:
                    #print("3")
                    EOFmouse = True
        if EOFmouse:
            #flush the rest of the human reads
            while not EOFhuman:
                myHumanUniqueFile.write(nexthumread)
                if not nexthumread.qname == prevHumID:
                    numhum += 1  # increment human counter for unique only
                prevHumID = nexthumread.qname
                try:
                    nexthumread = next(myHumanFile)
                except StopIteration:
                    EOFhuman = True

    summaryFile.write(
        "sample\tunique species A pairs\tunique species B pairs\tambiguous pairs\n")
    summaryFile.write(humanprefix + "\t" + str(numhum) +
                      "\t" + str(nummou) + "\t" + str(numamb) + "\n")
    summaryFile.close()
    myHumanFile.close()
    myMouseFile.close()
    myHumanUniqueFile.close()
    myHumanAmbiguousFile.close()
    myMouseUniqueFile.close()
    myMouseAmbiguousFile.close()


def file_exists(fname):
    """Check if a file exists and is non-empty.
    """
    return path.exists(fname) and path.getsize(fname) > 0


if __name__ == "__main__":
   main()
