__author__ = 'gallochri'
__version__ = '0.0.6'
__license__ = 'GPLv3 license'

import requests
from PyQt5.QtWidgets import QMainWindow, QApplication

from glMAC.mainwindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.button_search.clicked.connect(self.search_button_clicked)
        self.comboBox_services.activated.connect(self.service_lookup)

        def action_about():
            QApplication.instance().aboutQt()
        self.action_about.triggered.connect(action_about)

    def service_lookup(self):
        print(self.comboBox_services.currentIndex())

    def search_button_clicked(self):
        mac_address = self.input_mac.text()
        if self.comboBox_services.currentIndex() == 0:
            vendor_api = "https://macvendors.co/api/vendorname/"
        else:
            vendor_api = "http://api.macvendors.com/"

        r = requests.get(url="%s%s" % (vendor_api, mac_address))
        print("Request : %s%s" % (vendor_api, mac_address))
        print("Response: ", r)
        # r = requests.get(url="http://api.macvendors.com/%s" % mac_address)
        self.output_vendor.setText(r.text)

