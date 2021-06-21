import serial
import time
import multiprocessing as mp

# bitrate of serial from fed to pi
# do not set above 57600, will lose data
baud = 57600

# number of seconds you want each port to wait for a response
timeout = 1

# Set ports up, empty
ready = False
port1 = None
port2 = None
port3 = None
port4 = None
ports = ()

def setup(port1src="/dev/ttyAMA1", port2src="/dev/ttyAMA2", port3src="/dev/ttyAMA3", port4src="/dev/ttyAMA4"):
    """
    Script to call first, setting up the serial ports to listen for incoming traffic
    
    Arguments:
        port#src: The location of the activated serial port for port #, found in /dev/
            set to anything not starting with "/dev/" to deactivate
    """
    global ports
    # initialize serial port objects
    if port1src is not None and port1src[0:4] == "/dev/":
        global port1
        port1 = serial.Serial(
            port = port1src,
            baudrate = baud,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = timeout,
        )
        ports += port1

    if port2src is not None and port2src[0:4] == "/dev/":
        global port2
        port2 = serial.Serial(
            port = port2src,
            baudrate = baud,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = timeout,
        )
        ports += port2

    if port3src is not None and port3src[0:4] == "/dev/":
        global port3
        port3 = serial.Serial(
            port = port3src,
            baudrate = baud,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = timeout,
        )
        ports += port3

    if port4src is not None and port4src[0:4] == "/dev/":
        global port4
        port4 = serial.Serial(
            port = port4src,
            baudrate = baud,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = timeout,
        )
        ports += port4

    if ports:
        ready = True

def close():
    """
    Call to disable all active serial ports and free pins
    """
    global ready
    ready = False
    for port in ports:
        if port is not None:
            port.close()

def readPort(port, f=None, verbose=False):
    """
    Reads from a serial port until a UTF-8 newline character \n
    arguments:
        port: pointer to the serial port object to read
        f: function to call on read with argument line
        verbose: prints all input if true
    """
    line = port.readline()
    if verbose: print(line)
    if f is not None:
        f(line)

def run(f=None, multi=False, verbose=False):
    """
    Main function
    Loops indefinitely, reading all serial ports with ~1 ms delay between each loop
    Arguments:
        f: the function to call upon receiving and reading a line from a port with argument of the line
        mp: if true, uses multiprocessing to poll ports faster
    """
    if not ready:
        raise RuntimeError("setup was not called before run")
    while True:
        for port in ports:
            if port.isWaiting():
                if multi: 
                    mp.Process(target=readPort, args=(port, f, verbose)).start()
                else: 
                    readPort(port, f, verbose)

        time.sleep(0.0009)  # loop without reading a port takes about 0.0001, total time ~1ms per loop

if __name__ == "__main__":
    run(multi=True, verbose=True)