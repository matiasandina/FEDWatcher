from src import fedwatcher as fwr
import time

multiOn = False

def printTime(line):
    print(time.ctime())

if __name__ == "__main__":
    fw = fwr.Fedwatcher()
    try:
        print("Starting fedwatch")
        fw.run(f=printTime, multi=multiOn, verbose=True)
        print("started")
        while True:
            pass
    except KeyboardInterrupt:
        print("stopping and closing fedwatch")
        fw.stop()
        fw.close()
        print("finished")
