import os


class Autodesk3dsmax(object):

    def __init__(self):
        super(Autodesk3dsmax, self).__init__()

        self.exe_filename = None
        self.max_root = None
        self.version = None
        self.version_str = None
        self.icon = None
        self.bit = None

        self.startup_script_path = None

    def filein_script_code(self, script_filename):
        """
        生成filein脚本的mxs代码
        :param script_filename:
        """
        code = 'try(filein @"{}";)catch(print ("error_filein:"+@"{}"))'.format(script_filename, script_filename)
        return code

    def ready_data_from_finder(self, data):
        self.exe_filename = data['path']
        self.version = data['version']
        self.version_str = data['version_string']
        self.icon = data['icon']
        self.bit = data['bit']

        self.max_root = os.path.dirname(self.exe_filename)

        self.startup_script_path = os.path.join(self.max_root, 'scripts\Startup')

    def install_startup_script(self, filename, data):
        """
        安装启动脚本
        :param data:
        """
        full_script_filename = os.path.join(self.startup_script_path, file_in_name)

        with open(full_script_filename, 'wb') as f:
            f.write(data.encode())
            return True

    def uninstall_startup_script(self, filename):
        """
        卸载启动脚本
        """
        full_script_filename = os.path.join(self.startup_script_path, file_in_name)
        if os.path.exists(full_script_filename):
            os.remove(full_script_filename)

    def is_install_startup_script(self, filename, code=None):
        """
        是否安装过启动脚本
        data = 脚本内容
        :rtype: object
        """

        full_script_filename = os.path.join(self.startup_script_path, file_in_name)
        if not os.path.exists(full_script_filename):
            return False

        with open(full_script_filename, 'rb') as f:
            old_code = f.read()

        if old_code != code.encode():
            return False

        return True


if __name__ == '__main__':
    data = {'bit': '64',
            'icon': {'large': 'C:\\Program Files\\Autodesk\\3ds Max '
                              '2014\\UI_ln/Icons/ATS/ATSScene.ico',
                     'small': 'C:\\Program Files\\Autodesk\\3ds Max '
                              '2014\\UI_ln/Icons/ATS/ATSScene.ico'},
            'path': 'C:\\Program Files\\Autodesk\\3ds Max 2014\\3dsmax.exe',
            'version': 1604200000,
            'version_string': '3dsmax 2014'}

    a = Autodesk3dsmax()
    a.ready_data_from_finder(data)

    file_in_code = a.filein_script_code(r"E:\XDL_MANAGER3\plug-ins\3dsmax\xdl_init.ms")
    file_in_name = 'kjj_init.ms'

    print(file_in_code)

    print(a.is_install_startup_script(file_in_name, file_in_code))
    print(a.install_startup_script(file_in_name, file_in_code))
