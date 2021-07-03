from src import fedwatcher as fwr
import time

def printTime(line):
    print(time.ctime())

if __name__ == "__main__":
    try:
        print("Starting fedwatch")
        fw = fwr.Fedwatcher()
        fw.run(f=printTime, verbose=True)
        print("started")
        print(f"Running: {fw.is_running()}, Ready: {fw.is_ready()}")
        while True:
            pass
    except KeyboardInterrupt:
        print("stopping and closing fedwatch")
        fw.stop()
        fw.close()
        print("finished")
        print(f"Running: {fw.is_running()}, Ready: {fw.is_ready()}")