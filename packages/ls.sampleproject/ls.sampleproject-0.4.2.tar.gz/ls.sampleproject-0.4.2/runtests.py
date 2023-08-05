#!/usr/bin/env python
import os
import sys
from coverage import Coverage
from unittest import defaultTestLoader
from unittest import TextTestRunner

def run():
    verbosity = 1
    if "-v" in sys.argv or "--verbose" in sys.argv:
        verbosity = 2
    tests = defaultTestLoader.discover(".")
    runner = TextTestRunner(verbosity=verbosity)
    result = runner.run(tests)
    return result.failures

def coverage():
    if "--coverage" in sys.argv:
        cover = Coverage()
        cover.start()
        failures = run()
        cover.stop()
        cover.save()
        cover.html_report()
    else:
        failures = run()
    return failures

if __name__ == "__main__":
    failures = coverage()
    sys.exit(bool(failures))
