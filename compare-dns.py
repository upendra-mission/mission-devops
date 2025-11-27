#!/usr/bin/env python3

# Compare DNS records between two DNS servers.
# Usage:
#     python compare-dns.py <IP1> <IP2> <records.csv>
#
# CSV format:
#     fqdn,type
#
# Example:
#     google.com,A
#     example.org,MX

import sys
import time
import csv
import dns.resolver
from datetime import datetime


# -------------------------
# Spinner for progress
# -------------------------
def spinning_cursor():
    while True:
        for cursor in "|/-\\":
            yield cursor


def spin(spinner):
    global loopCount
    loopCount += 1
    time.sleep(0.02)
    sys.stdout.write(next(spinner))
    sys.stdout.flush()
    sys.stdout.write('\b')

    if loopCount % 100 == 0:
        sys.stdout.write("\b" * 30)
        print(f"{loopCount} records tested ", end="")


# -------------------------
# Argument Check
# -------------------------
if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} IP1 IP2 records.csv")
    sys.exit(1)

ip1 = [sys.argv[1]]
ip2 = [sys.argv[2]]
inputCsv = sys.argv[3]

# -------------------------
# Output filenames
# -------------------------
now = datetime.now()
timeString = now.strftime('%Y%m%d-%H%M%S')

logFilename = f"output/{timeString}_compare-dns.log"
identicalLogFilename = f"output/{timeString}_identical.txt"
problemsFilename = f"output/{timeString}_problems.csv"
errFilename = f"output/{timeString}_compare-dns.errors"
exceptionsFilename = f"output/{timeString}_compare-dns.exceptions"

# -------------------------
# DNS Resolvers
# -------------------------
res1 = dns.resolver.Resolver(configure=False)
res1.nameservers = ip1

res2 = dns.resolver.Resolver(configure=False)
res2.nameservers = ip2

spinner = spinning_cursor()
loopCount = 0
exceptionCount = 0
mismatchCount = 0


# -------------------------
# MAIN LOGIC
# -------------------------
with open(problemsFilename, "w") as problemsFile, \
     open(identicalLogFilename, "w") as identicalLog, \
     open(exceptionsFilename, "w") as exceptionLog, \
     open(errFilename, "w") as errlogfile, \
     open(logFilename, "w") as logfile:

    print()
    print(f"Starting DNS compare between {ip1} versus {ip2}")
    print(f"Log file: {logFilename}")
    print(f"Errors logged in: {errFilename}")
    print(f"Exceptions logged in: {exceptionsFilename}")
    print(f"Problem items logged in: {problemsFilename}")
    print(f"Identical items logged in: {identicalLogFilename}")
    print("-----------------------------\n")

    # Mirror logs inside file
    for line in [
        f"Starting DNS compare between {ip1} versus {ip2}",
        f"Log file: {logFilename}",
        f"Errors logged in: {errFilename}",
        f"Exceptions logged in: {exceptionsFilename}",
        f"Problem items logged in: {problemsFilename}",
        f"Identical items logged in: {identicalLogFilename}",
        "-----------------------------"
    ]:
        print(line, file=logfile)

    # Read CSV input file
    with open(inputCsv, "r") as csvfile:
        reader = csv.reader(csvfile)

        for i, line in enumerate(reader):
            # Skip blank or commented lines
            if not line or line[0].strip() == "" or line[0].startswith("#"):
                continue

            spin(spinner)
            print("", file=logfile)

            try:
                recName = line[0].strip()
                recType = line[1].strip()
            except Exception as exIndex:
                lineNumber = i + 1
                sys.stdout.write('\b')
                msg = f"Ignoring bad data at line {lineNumber}: \"{exIndex}\""
                print(msg)
                print(msg, file=logfile)
                print(msg, file=exceptionLog)
                continue

            # Lookup in resolver 1
            try:
                a1 = res1.resolve(recName, recType)
            except Exception as ex1:
                exceptionCount += 1
                print(f"Exception from {ip1}: {recName} {recType}: \"{ex1}\"", file=exceptionLog)
                a1 = [f"bad response \"{ex1}\""]

            answer1 = sorted([str(a).lower() for a in a1])

            # Lookup in resolver 2
            try:
                a2 = res2.resolve(recName, recType)
            except Exception as ex2:
                exceptionCount += 1
                print(f"Exception from {ip2}: {recName} {recType}: \"{ex2}\"", file=exceptionLog)
                a2 = [f"bad response \"{ex2}\""]

            answer2 = sorted([str(a).lower() for a in a2])

            # Compare answers
            if answer1 != answer2:
                mismatchCount += 1
                print(f"{recName} {recType}: mismatch", file=logfile)
                print(f"{recName} {recType}:", file=errlogfile)
                print(f"    {ip1[0]:>16}: {answer1}", file=errlogfile)
                print(f"    {ip2[0]:>16}: {answer2}", file=errlogfile)
                print(f"{recName},{recType}", file=problemsFile)
            else:
                print(f"{recName} {recType}: OK identical", file=logfile)
                print(f"{recName}", file=identicalLog)

            # Log raw responses
            print(f"    {ip1[0]:>16}: {answer1}", file=logfile)
            print(f"    {ip2[0]:>16}: {answer2}", file=logfile)

# Final output
sys.stdout.write("\b" * 30)
print(f"Finished. {loopCount} records tested, {mismatchCount} mismatched, {exceptionCount} exceptions.")
print(f"Finished. {loopCount} records tested, {mismatchCount} mismatched, {exceptionCount} exceptions.")
