import serial
import time
import multiprocessing as mp

class Fedwatch:
    # bitrate of serial from fed to pi
    # do not set above 57600, will lose data
    baud = 57600

    # number of seconds you want each port to wait for a response
    timeout = 1
    port1 = None
    port2  = None
    port3 = None
    port4 = None
    portpaths = None
    ports = tuple()
    ready = False

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
    
    def setup():
        """
        Initializes and opens all ports in the portpath tuple
        """
        for portpath in portpaths:
            port = serial.Serial(
                port = portpath,
                baudrate = self.baud,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout = timeout,
            )
            if not port.is_open:
                raise IOError("Serial port at % not opening" % portpath)
            ports += port
            self.ready = True
        
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
        for port in ports.get_ports():
            port.reset_input_buffer()
        while True:
            for port in ports.get_ports():
                if port.isWaiting():
                    if multi: 
                        mp.Process(target=readPort, args=(port, f, verbose)).start()
                    else: 
                        readPort(port, f, verbose)

            time.sleep(0.0009)  # loop without reading a port takes about 0.0001, total time ~1ms per loop

    def close():
        """
        Closes all serial ports and stops running
        """
        self.ready = False
        for port in ports:
            port.close()

    def get_ports():
        """
        Returns tuple of active ports
        """
        return self.ports

    def is_ready():
        """
        Returns True if set up and ports are open, else false
        """
        return self.ready

if __name__ == "__main__":
    fed = Fedwatch()
    fed.setup()
    fed.run(multi=True, verbose=True)
