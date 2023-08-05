#!/usr/bin/env python3

import logging
import xml.etree.ElementTree as ET

import click

from junit_xml import TestCase, TestSuite

logging.basicConfig()
logger = logging.getLogger("findbugs2junit")


@click.command()
@click.argument('infile', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
@click.option('--debug/--no-debug', default=False)
def cli(infile, outfile, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    logger.info("infile: {inf} outfile: {outf}".format(
        inf=infile.name, outf=outfile.name))
    tree = ET.parse(infile)
    root = tree.getroot()

    test_cases = []
    files = root.findall("file")
    for f in files:
        for b in f.findall("BugInstance"):
            classname = b.get("classname")
            tc = TestCase(
                b.get("type"),  # name
                classname,  # classname
            )
            # mark test case as a failure
            tc.add_failure_info("{0} line:{1}".format(b.get("message"),
                                                      b.get("lineNumber")))
            test_cases.append(tc)
    ts = TestSuite("Findbugs", test_cases)
    ts.to_file(outfile, [ts])


if __name__ == "__main__":
    cli()
