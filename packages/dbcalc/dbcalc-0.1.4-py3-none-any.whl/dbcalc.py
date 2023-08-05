#!/usr/bin/env python
import math
import sys

USAGE = """dbcalc [i|o|d] [PARAMS]

Conversion tool to do power <-> dB calculations. PARAMS is a list of space-separated values depending
on the mode (i, o or d) selected:

i   calculate input power from the PARAMS output power and dB
o   calculate output power from the PARAMS input power and dB
d   calculate dB from the PARAMS output power and input power

E.g.: to calculate the output power, given 1W of input power and 3dB loss

    $ dbcalc o 1 -3
    0.5011872336272722

"""

def main():
    if len(sys.argv) < 4:
        sys.stderr.write(USAGE)
        sys.stderr.write("Error: Not enough arguments.\n")
        sys.exit(1)
    if sys.argv[1] == 'd':
        sys.stdout.write(str(10 * math.log10(float(sys.argv[2])/float(sys.argv[3]))))
    elif sys.argv[1] == 'i':
        sys.stdout.write(str(float(sys.argv[2])*math.pow(10., -float(sys.argv[3])/10.)))
    elif sys.argv[1] == 'o':
        sys.stdout.write(str(float(sys.argv[2])*math.pow(10., float(sys.argv[3])/10.)))
    else:
        sys.stderr.write(USAGE)
        sys.stderr.write("Error: unrecognized mode '%s'\n" % sys.argv[1])

    sys.stdout.write('\n')

if __name__ == '__main__':
    main()
