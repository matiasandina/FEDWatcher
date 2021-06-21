# example script for using fedwatch package

import fedwatch
import time

def readOut(line):
    print(line)

if __name__ == "__main__":
    fedwatch.setup()
    fedwatch.run(f=readOut)
    