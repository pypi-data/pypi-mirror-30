import sys
import subprocess
from PyQt5 import uic, QtWidgets, QtCore
import checkupdate

_appname = 'civiltools'
_version = '1.4'
_civiltools_mainpackages = ['civiltools']

main_window = uic.loadUiType('main_form.ui')[0]
about_window, about_base = uic.loadUiType('about.ui')

class FormWidget(QtWidgets.QWidget, main_window):

    def __init__(self):
        super(FormWidget, self).__init__()
        self.setupUi(self)
        self.about_Button.clicked.connect(self.about)
        self.section_Button.clicked.connect(self.run_section)
        self.cfactor_Button.clicked.connect(self.run_cfactor)
        self.punch_Button.clicked.connect(self.run_punch)
        self.record_Button.clicked.connect(self.run_record)
        self.about_Button.clicked.connect(self.about)
        self.update_Button.clicked.connect(self.check_for_updates)
    #----
    def run_section(self):
        subprocess.Popen(['python', '-m', 'applications.section.MainWindow'])
        
    def run_cfactor(self): 
        subprocess.Popen(['python', '-m', 'applications.cfactor.MainWindow'])   
           
    def run_punch(self):
        subprocess.Popen(['python', '-m', 'applications.punch.mainwindow']) 
        
    def run_record(self):
        subprocess.Popen(['python', '-m', 'applications.records.records.MainWindow']) 

    def about(self):
        self.child_win = AboutForm(self)
        self.child_win.show()

    def check_for_updates(self):
        try:
            status = checkupdate.check_few(_civiltools_mainpackages)
            if status[0]:
                msg_info = 'Check for packages update - OK'
                msg_text = status[1]
            else:
                msg_info = 'Check for packages update - !!! out to date !!!'
                msg_text = status[1]
            QtWidgets.QMessageBox.information(None, msg_info, status[1])
        except:
            QtWidgets.QMessageBox.information(None, 'Check for packages update', 'Checking failed !! ')


class AboutForm(about_base, about_window):
    def __init__(self, parent=None):
        super(AboutForm, self).__init__() 
        self.setupUi(self) 

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # translator = QtCore.QTranslator()
    # translator.load("main_form.qm")
    # app.installTranslator(translator)
    window = FormWidget()
    window.setWindowTitle(_appname + ' ' + _version)
    window.show()
    sys.exit(app.exec_())