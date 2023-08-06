# -*- coding: utf-8 -*-


class LTPFileError(FileNotFoundError):
    def __init__(self):
        super(LTPFileError, self).__init__("LTP model not exist."
                                           " Please download models (v3.3.1) in following url: "
                                           "http://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569")


class InstallError(ImportError):
    def __init__(self, name):
        super(InstallError, self).__init__('Please install "{}" first, "pip install {}".'.format(name, name))


class LTPInstallError(InstallError):
    def __init__(self):
        super(LTPInstallError, self).__init__('pyltp')


class JiebaInstallError(InstallError):
    def __init__(self):
        super(JiebaInstallError, self).__init__('jieba')


class ThulacInstallError(InstallError):
    def __init__(self):
        super(ThulacInstallError, self).__init__('thulac')


class NLPIRInstallError(InstallError):
    def __init__(self):
        super(NLPIRInstallError, self).__init__('pynlpir')
