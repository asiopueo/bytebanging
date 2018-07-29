#!/usr/bin/env python

####################################################################
#
#   Node which requests commands and publishes on a twist topic
#
####################################################################

import cmd, sys
import math
import serial
import time

SERIAL_PORT = 'com3'



# Helper function
def parse(arg):
    #print (tuple(map(float, arg.split())))
    return tuple(map(float, arg.split()))


# ROS backend
class Interface(object):
    def __init__(self):
        # Serial port to publish motor control signals to
        # Lower boud rate to publish motor commands might be appropriate
        self.ser = serial.Serial(SERIAL_PORT, 9600, timeout=0)

    def send(self, deg):
        command = int(deg[0]).to_bytes(1, 'big')
        self.ser.write(command)
        print("Sent: {}".format(command))

        time.sleep(0.01)

        if self.ser.in_waiting:
            tmp = self.ser.read(self.ser.in_waiting)
            #tmp = int.from_bytes(tmp, 'big', signed=False)
            print("Received: {}".format(tmp))


    def quit(self):
        print('Shutting down node \'r_console\'...')
        #raise SystemExit()



# Frontend
class Shell(cmd.Cmd, object):
    def __init__(self):
        super(Shell, self).__init__()
        self.prompt = '(ByteBanging) $ '
        self.intro = 'Welcome to the ByteBanging-Shell. Enter \'help\' or \'?\' to list commands.\n'
        self.file = None # Later for waypoint files...
        self.interface = Interface()

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.
        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    # Basic commands:
    def do_send(self, arg):
        'Send bytes'
        self.interface.send(parse(arg))


    def do_quit(self, arg):
        'Quit shell and shutdown node.'
        quit()
        raise SystemExit()



if __name__=='__main__':
    Shell().cmdloop()




