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
        # for child in content.rootFolder.childEntity:

    @property
    def my_prompt(self):
        return self._my_prompt

    prompt = my_prompt

    def _redraw_prompt(self):
        path_2_display = ['/']
        for p in self.current_path:
            path_2_display.append('/' + p)
        path_2_display.append('/')
        self._my_prompt = '[{0}@{1} {2}]# '.format(self.args.user, self.hostname, ''.join(path_2_display))
        prompt = self.my_prompt

    def do_pwd(self, arg):
        print("{0}".format("".join(self.current_path)))

    def do_ls(self, arg):
        VmUtils.print_folder(self.current_folder)

    def do_cd(self, arg):
        new_folder = VmUtils.get_folder_by_name(self.current_folder, arg)
        if not new_folder:
            print("{0}".format("cd: No such file or directory"))
            return
        self.current_folder = new_folder
        self.current_path.append(new_folder.name)
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
