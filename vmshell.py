"""
VM shell class handles all shell related operations.
samuels (c)
2016
"""

import cmd


class VMShell(cmd.Cmd, object):
    def __init__(self, si, args):
        super(VMShell, self).__init__()
        self.si = si
        self.args = args
        self.file = None
        self.current_displayed_path = "/"
        self.current_real_path = None
        self.hostname = args.host
        self._my_prompt = '[{0}@{1} {2}]# '.format(args.user, self.hostname, self.current_displayed_path)

        self.content = si.RetrieveContent()
        #for child in content.rootFolder.childEntity:


    @property
    def my_prompt(self):
        return self._my_prompt

    prompt = my_prompt

    def do_pwd(self, arg):
        print("{0}".format(self.current_displayed_path))

    def do_ls(self, arg):
        try:
            print("{0}".format(self.content.rootFolder.name))
        except Exception:
            pass


    def do_bye(self, arg):
        """Stop recording, close the turtle window, and exit:  BYE"""
        print('Thank you for using  vmcli')
        self.close()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
