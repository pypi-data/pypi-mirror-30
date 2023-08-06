import snakemake
from os import path
import argparse
import sys


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Download necessary files, run workflow and obtain results')
    parser.add_argument('--version', action='version', version='1.0.0.dev')  # TODO un-hardcode version
    parser.add_argument('segmentation', help='.bed.gz file, the segmentation/annotation output from Segway')
    parser.add_argument('-o', '--outdir', default='outdir', help='Output directory to store all the results')

    parsed_args = parser.parse_args(args)

    print(parsed_args)

    # """Entry point for the application script"""
    here = path.abspath(path.dirname(__file__))
    snakemake.snakemake(path.join(here, "Snakefile"), config=vars(parsed_args))  # dryrun=True, printshellcmds=True)
