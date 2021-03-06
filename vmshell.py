"""
VM shell class handles all shell related operations.
samuels (c)
2016
"""

import cmd
from vmutils import VmUtils


class VMShell(cmd.Cmd, object):
    def __init__(self, si, args):
        super(VMShell, self).__init__()
        self.si = si
        self.args = args
        self.file = None
        self.current_path = []
        # self.current_real_path = None
        self.hostname = args.host
        self._my_prompt = '[{0}@{1} {2}]# '.format(self.args.user, self.hostname, "/")

        self.content = si.RetrieveContent()
        self.current_folder = self.content.rootFolder
        self.vmutils = VmUtils()  # helper utils class

    @property
    def my_prompt(self):
        return self._my_prompt

    prompt = my_prompt

    def _redraw_prompt(self):
        self._my_prompt = '[{0}@{1} {2}]# '.format(self.args.user, self.hostname, self.current_folder.name)
        prompt = self.my_prompt

    def do_pwd(self, arg):
        path_2_display = []
        for p in self.current_path:
            path_2_display.append('/' + p)
        if not path_2_display:
            path_2_display = ['/']
        print("{0}".format("".join(path_2_display)))

    def do_ls(self, arg):
        VmUtils.print_folder(self.current_folder)

    def do_cd(self, arg):
        new_folder = None
        if arg == "..":  # backward navigation
            new_folder = self.current_folder.parent
        else:
            try:
                new_folder = VmUtils.get_folder_by_name(self.current_folder, arg)
            except AttributeError as att_error:
                print("{0}".format(att_error))
        if not new_folder:
            if arg != "..":
                print("{0}".format("cd: No such file or directory"))
                return
            else:
                return
        if arg != "..":
            self.current_path.append(new_folder.name)
        else:
            if self.current_path:
                self.current_path.pop()
        self.current_folder = new_folder
        self._redraw_prompt()

    def do_bye(self, arg):
        """Stop recording, close the turtle window, and exit:  BYE"""
        print('Thank you for using  vmcli')
        self.close()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
