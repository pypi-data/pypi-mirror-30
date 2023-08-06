__author__ = 'gallochri'
__version__ = '0.0.1'
__license__ = 'GPLv3 license'

import requests
from PyQt5.QtWidgets import QMainWindow, QApplication

from glMAC.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.button_search.clicked.connect(self.search_button_clicked)

        def action_about():
            QApplication.instance().aboutQt()
        self.action_about.triggered.connect(action_about)

    def search_button_clicked(self):
        mac_address = self.input_mac.text()
        self.output_vendor.setText("Wait...")
        print("ok")
        r = requests.get(url="http://api.macvendors.com/%s" % mac_address)
        self.output_vendor.setText(r.text)

