from abc import ABC
from widgets import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import json
import logging
import sys
import os
from dotenv import load_dotenv

class AppApi(ABC):
    def getValue(self,currency="USD"):
        try:
            load_dotenv()
            API_KEY = os.getenv("API_KEY")
        except FileNotFoundError:
            logging.error("Nie znaleziono klucza api")
            return None, None
        try:
            response = requests.get(f"https://exchange-rates.abstractapi.com/v1/live/?api_key={API_KEY}&base={currency}")
        except requests.exceptions.ConnectionError:
            logging.error("Nie udalo sie polaczyc z API")
            return None, None
        else:
            try:
                if response.status_code=="200":
                    raise ConnectionError("Nie polaczono z API")
            except:
                logging.error("Niepoprawny klucz API")
                return None, None
        content = response.json()
        try:
            return content['exchange_rates']
        except KeyError:
            logging.error("Bledna odpowiedz API")

class Calc(AppApi):
    def getCurrencies(self):
        try:
            req = self.getValue("USD")
            req['USD'] = 1
            print(req)
            cur = list(req.keys())
            self.exchange_rates = req
            return cur
        except AttributeError:
            return None
    def calcExchange(self, *, inputCurr, outputCurr, value):
        try:
            inRate = self.exchange_rates[inputCurr]
            outRate = self.exchange_rates[outputCurr]
            return str(round(1/inRate*outRate*float(value),3))
        except ValueError:
            logging.error("Zly format tekstu")

class UserGUI(Calc):
    def __init__(self, parent: QtWidgets.QMainWindow):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(parent)

        self.currs = self.getCurrencies()
        
        self.ui.comboBox.addItems(self.currs)
        self.ui.comboBox_2.addItems(self.currs)

        self.ui.pushButton.clicked.connect(self.calcHandler)
    def calcHandler(self):
        input = self.ui.comboBox.currentText()
        output = self.ui.comboBox_2.currentText()
        value = self.ui.lineEdit.text()
        result = self.calcExchange(inputCurr=input, outputCurr=output, value=value)
        if result is None: return
        self.ui.label.setText(result)

class App():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = UserGUI(self.MainWindow)
        self.MainWindow.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    App()