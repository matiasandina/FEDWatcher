import serial
import time
import multiprocessing as mp

class Fedwatcher:
    # bitrate of serial from fed to pi 
    ### do not set above 57600, will lose data ###
    baud = 57600

    # number of seconds you want each port to wait for a response
    timeout = 1

    # Port variables
    portpaths = tuple()
    ports = tuple()

    # Process variables
    runProcess = None
    ready = False
    running = False

    def __init__(self, baud=57600, timeout=1, portpaths=("/dev/ttyAMA1", "/dev/ttyAMA2", "/dev/ttyAMA3", "/dev/ttyAMA4")):
        """
        Constructor
        Creates a new Fedwatch object with baud, timeout, and portpaths
        Arguments:
            baud: bitrate of serial connection from FED3. Will have errors if above 57600. Must match FED3 baud
            timeout: number of seconds to wait upon a readline call before stopping
            portpaths: the path to each open serial port on the Raspberry Pi. Defaulted to opening UART2 through UART5 in order
        """
        self.baud = baud
        self.timeout = timeout
        self.portpaths = portpaths

        for portpath in self.portpaths:
            port = serial.Serial(
                port = portpath,
                baudrate = self.baud,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout = self.timeout,
            )
            if not port.is_open:
                raise IOError("Serial port at % not opening" % portpath)
            self.ports += port
        if self.ports:
            self.ready = True
        else:
            raise RuntimeError("No ports given")
    
    def setupNewPorts(self, portpaths):
        """
        Used to change the active ports to the ones given in portpaths.
        Will close ports currently open
        Arguments:
            portpaths: new list of ports to use
        """
        
        if self.running():
            raise RuntimeError("Process is running, cannot call")

        if portpaths is not None:
            if not portpaths:
                raise RuntimeError("Given empty portpaths")
            self.close()
            self.ports = tuple()
            self.portpaths = portpaths

            for portpath in self.portpaths:
                port = serial.Serial(
                    port = portpath,
                    baudrate = self.baud,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout = self.timeout,
                )
                if not port.is_open:
                    raise IOError("Serial port at % not opening" % portpath)
                self.ports += port
            if self.ports:
                self.ready = True
        
    def readPort(self, port, f=None, verbose=False):
        """
        Reads from a serial port until a UTF-8 newline character \n
        arguments:
            port: pointer to the serial port object to read
            f: function to call on read with argument line
            verbose: prints all input if true
        """
        line = port.readline()
        if verbose: 
            print(line)
        if f is not None:
            f(line)

    def runHelper(self, f=None, multi=False, verbose=False):
        """
        Main function helper, should not be called directly
        Loops indefinitely in this thread, reading all serial ports with ~1 ms delay between each loop
        Arguments:
            f: the function to call upon receiving and reading a line from a port with argument of the line
            multi: if true, uses multiprocessing to poll ports faster
            verbose: if true, prints out all lines received
        """
        for port in self.ports():
            port.reset_input_buffer()

        while True:
            for port in self.ports():
                if port.isWaiting():
                    if multi: 
                        mp.Process(target=self.readPort, args=(port, f, verbose)).start()
                    else: 
                        self.readPort(port, f, verbose)

            time.sleep(0.0009)  # loop without reading a port takes about 0.0001, total time ~1ms per loop

    def run(self, f=None, multi=False, verbose=False):
        """
        Main function
        Loops indefinitely in the background, reading all serial ports with ~1 ms delay between each loop
        Arguments:
            f: the function to call upon receiving and reading a line from a port with argument of the line
            multi: if true, uses multiprocessing to poll ports faster
            verbose: if true, prints out all lines received
        """
        if not self.ready:
            raise RuntimeError("Ports are not setup")
        if self.running():
            raise RuntimeError("Process is already running")
        self.running = True
        self.runProcess = mp.Process(target=self.runHelper, args=(f, multi, verbose))
        self.runProcess.start()

    def stop(self):
        """
        Stops all watcher processes
        """
        if not self.running:
            raise RuntimeError("Process is not running")
        self.runProcess.terminate()
        self.running = False

    def close(self):
        """
        Closes all serial ports
        If process is running, will stop process first, then close ports
        """
        if self.running:
            self.stop()
        self.ready = False
        for port in self.ports:
            port.close()

    def get_ports(self):
        """
        Returns tuple of active ports
        """
        return self.ports

    def is_ready(self):
        """
        Returns True if set up and ports are open, else false
        """
        return self.ready
    
    def is_running(self):
        """
        Returns True if running, else false
        """
        return self.running

if __name__ == "__main__":
    try:
        print("Starting fedwatch")
        fw = Fedwatcher()
        fw.run(verbose=True)
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
