#!/usr/bin/python
"""
vCli - cli tool to manage VMWare VMs
"""

import cmd
import socket


class VMShell(cmd.Cmd):
    def __init__(self):
        self.file = None
        self.hostname = socket.gethostname()
        self.prompt = '{0}@{1}]#'.format('Admin', self.hostname)
        cmd.Cmd.prompt = self.prompt

    def do_bye(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
        print('Thank you for using Turtle')
        self.close()
        #bye()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

if __name__ == '__main__':
    VMShell().cmdloop()
