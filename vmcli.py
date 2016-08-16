#!/usr/bin/python
"""
vCli - cli tool to manage VMWare VMs
"""

import cmd


class VMShell(cmd.Cmd):
    prompt = 'admin@LG-C11B-LNX]#'

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
