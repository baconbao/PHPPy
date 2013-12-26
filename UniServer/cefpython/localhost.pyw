# An example of embedding CEF Python in PyQt4 application.
# Extended by mbrostami : Thanks to CEF Python

import platform
if platform.architecture()[0] != "32bit":
    raise Exception("Architecture not supported: %s" % platform.architecture()[0])
 
import os, sys ,subprocess ,fileinput 
import json
libcef_dll = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
        'libcef.dll')
if os.path.exists(libcef_dll):
    # Import the local module.
    if 0x02070000 <= sys.hexversion < 0x03000000:
        import cefpython_py27 as cefpython
    elif 0x03000000 <= sys.hexversion < 0x04000000:
        import cefpython_py32 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    # Import the package.
    from cefpython3 import cefpython

from PyQt4 import QtGui
from PyQt4 import QtCore 
def GetApplicationPath(file=None):
    import re, os
    # If file is None return current directory without trailing slash.
    if file is None:
        file = ""
    # Only when relative path.
    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        if hasattr(sys, "frozen"):
            path = os.path.dirname(sys.executable)
        else:
            path = os.getcwd()
        #elif "sys.argv[0]" in globals():
        #    path = os.path.dirname(os.path.realpath(sys.argv[0]))
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        path = path + os.sep + file
        path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path
    return str(file)

def ExceptHook(excType, excValue, traceObject):
    import traceback, os, time, codecs
    # This hook does the following: in case of exception write it to
    # the "error.log" file, display it to the console, shutdown CEF
    # and exit application immediately by ignoring "finally" (os._exit()).
    errorMsg = "\n".join(traceback.format_exception(excType, excValue,
            traceObject))
    errorFile = GetApplicationPath("error.log")
    try:
        appEncoding = cefpython.g_applicationSettings["string_encoding"]
    except:
        appEncoding = "utf-8"
    if type(errorMsg) == bytes:
        errorMsg = errorMsg.decode(encoding=appEncoding, errors="replace")
    try:
        with codecs.open(errorFile, mode="a", encoding=appEncoding) as fp:
            fp.write("\n[%s] %s\n" % (
                    time.strftime("%Y-%m-%d %H:%M:%S"), errorMsg))
    except:
        print("cefpython: WARNING: failed writing to error file: %s" % (
                errorFile))
    # Convert error message to ascii before printing, otherwise
    # you may get error like this:
    # | UnicodeEncodeError: 'charmap' codec can't encode characters
    errorMsg = errorMsg.encode("ascii", errors="replace")
    errorMsg = errorMsg.decode("ascii", errors="replace")
    print("\n"+errorMsg+"\n")
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    os._exit(1)

class MainWindow(QtGui.QMainWindow):
    mainFrame = None 
    apache = None
    mysql = None
    def __init__(self): 
        new_apache_config_file = open(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/apache2/conf/httpd.conf",'w')
        for line in fileinput.input(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/apache2/conf/httpd-default.conf"):#, inplace=True
            if(line.find("{DIRECTORY}") > -1):
                new_apache_config_file.write(line.replace("{DIRECTORY}", os.path.dirname(os.path.abspath(sys.argv[0]))+"/../"))
            else:
                new_apache_config_file.write(line)
                #print "%s" % (line),
        new_apache_config_file.close()  
        new_apache_config_file = open(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/php/php.ini",'w')
        for line in fileinput.input(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/php/php-sample.ini"):#, inplace=True
            if(line.find("{DIRECTORY}") > -1):
                new_apache_config_file.write(line.replace("{DIRECTORY}", os.path.dirname(os.path.abspath(sys.argv[0]))+"/../"))
            else:
                new_apache_config_file.write(line)
                #print "%s" % (line),
        new_apache_config_file.close()   
        new_apache_config_file = open(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/mysql/my.ini",'w')
        for line in fileinput.input(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/mysql/my-sample.ini"):#, inplace=True
            if(line.find("{DIRECTORY}") > -1):
                new_apache_config_file.write(line.replace("{DIRECTORY}", os.path.dirname(os.path.abspath(sys.argv[0]))+"/../"))
            else:
                new_apache_config_file.write(line)
                #print "%s" % (line),
        new_apache_config_file.close()   
        #print "%d: %s" % (fileinput.filelineno(), line),
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        os.system('taskkill /f /im mysqld1.exe')
        self.apache = subprocess.Popen(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/apache2/bin/httpd1.exe" ,startupinfo=startupinfo)
        self.mysql = subprocess.Popen(os.path.dirname(os.path.abspath(sys.argv[0])) +"/../usr/local/mysql/bin/mysqld1.exe" ,startupinfo=startupinfo)
        super(MainWindow, self).__init__(None)
        #self.createMenu()
        self.mainFrame = MainFrame(self)
        self.setCentralWidget(self.mainFrame)
        self.resize(1024, 600)
        self.setWindowTitle('MBR Optimizer')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def createMenu(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(QtGui.QAction("Open", self))
        filemenu.addAction(QtGui.QAction("Exit", self))
        aboutmenu = menubar.addMenu("&About")

    def focusInEvent(self, event):
        cefpython.WindowUtils.OnSetFocus(int(self.centralWidget().winId()), 0, 0, 0)

    def closeEvent(self, event):
        self.mainFrame.browser.CloseBrowser()

class MainFrame(QtGui.QWidget):
    browser = None

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(int(self.winId()))
        self.browser = cefpython.CreateBrowserSync(windowInfo,
                browserSettings={},
                navigateUrl=GetApplicationPath("http://127.0.0.1"))
        self.show()

    def moveEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

    def resizeEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

class CefApplication(QtGui.QApplication):
    timer = None

    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.createTimer()

    def createTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(10)

    def onTimer(self):
        # The proper way of doing message loop should be:
        # 1. In createTimer() call self.timer.start(0)
        # 2. In onTimer() call MessageLoopWork() only when
        #    QtGui.QApplication.instance()->hasPendingEvents() returns False.
        # But... there is a bug in Qt, hasPendingEvents() returns always true.
        cefpython.MessageLoopWork()

    def stopTimer(self):
        # Stop the timer after Qt message loop ended, calls to MessageLoopWork()
        # should not happen anymore.
        self.timer.stop()

if __name__ == '__main__':
    #print("PyQt version: %s" % QtCore.PYQT_VERSION_STR)
    #print("QtCore version: %s" % QtCore.qVersion())

    sys.excepthook = ExceptHook
    settings = {}
    settings["log_file"] = GetApplicationPath("debug.log")
    settings["log_severity"] = cefpython.LOGSEVERITY_INFO
    settings["release_dcheck_enabled"] = True # Enable only when debugging
    settings["browser_subprocess_path"] = "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess")
    cefpython.Initialize(settings)

    app = CefApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
    app.stopTimer()

    # Need to destroy QApplication(), otherwise Shutdown() fails.
    # Unset main window also just to be safe.
    del mainWindow
    del app

    cefpython.Shutdown()
