from fbs_runtime.application_context import ApplicationContext
import requests
import csv
import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, 
                             QWidget, QPushButton, QVBoxLayout, 
                             QLineEdit, QTextEdit, QLabel, QMessageBox)
from PyQt5.QtGui import QPixmap
from sys import platform


userUrl = "https://my.accounting.pe/api/v1/company/673/user"
addressUrl = "https://my.accounting.pe/api/v1/company/673/payroll/user"
headers = {
    'Content-Type': 'application/json',
    'X-Token': 'T0dxL4vbYTWLLoP'
}


def msgbtn(i):
    print("Button pressed is:", i.text())
    if i.text() == "OK":
        print("ok")
    else:
        sys.exit()


def showdialog(title, info, detail):
    msg = QMessageBox()
    #msg.setIcon(QMessageBox.Information)
    msg.setText(title)
    msg.setInformativeText(info)
    #msg.setDetailedText(detail)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.buttonClicked.connect(msgbtn)

    #layout = QVBoxLayout(msg)

    msg.exec_()


def user(token):

    headers["X-Token"] = token
    response = requests.get(userUrl, headers=headers)
    try:
        response.raise_for_status()
        if response.ok:
            users = response.json()
            result = []

            for value in users['users']:
                result.append((value['name'], value['id']))
            return result

    except requests.exceptions.RequestException as e:
        title = "Error"
        info = "Kolla att du är ansluten till ett nätverk och angivit korrekt token"
        showdialog(title, info, str(e))


def address(token):

    headers["X-Token"] = token
    response = requests.get(addressUrl, headers=headers)

    try:
        response.raise_for_status()
        if response.ok:
            addresses = response.json()
            result = []
            for address in addresses['payroll-user-readables']:
                result.append((address['user'],
                               address['address1'],
                               address['address2'],
                               address['zip-code'],
                               address['state'],
                               address['phone']
                               ))
            return result

    except requests.exceptions.RequestException as e:
        title = "Error"
        info = "Kolla att du är ansluten till ett netverk och angivit korrekt token"
        showdialog(title, info, str(e))


def combine(token):
    user_result = user(token)
    address_result = address(token)
    combine_list = []
    if user_result and address_result:
        for us in user_result:
            for adr in address_result:
                if us[1] == adr[0]['id']:
                    combine_list.append(
                        (us[0], adr[1], adr[2], adr[3], adr[4], adr[5]))

    return combine_list


def generate_csv(token):

    address_list = combine(token)

    desktop = ""
    if platform == "darwin":
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    elif platform == "win32":
        desktop = os.path.join(os.path.join(
            os.environ['USERPROFILE']), 'Desktop')

    with open(desktop+'/addresslist.csv', 'w+', newline="", encoding='utf-8-sig') as file:

        csv_out = csv.writer(file)
        csv_out.writerow(['name', 'address1', 'address2',
                          'zip-code', 'state', 'phone'])
        for row in address_list:
            csv_out.writerow(row)
        if(address_list):
            title = "Adresslista"
            info = "Filen är sparad på ditt skrivbord \n" + desktop
            showdialog(title, info, "Ses på dynaday")
        file.close()


def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Nova")
    layout = QVBoxLayout()
    #app.setStyleSheet("QPushButton { margin: 12ex; }")
    #image = QPixmap("./dyna.png")
    label = QLabel()
    label.setText("Lägg till din access token")

    #label2 = QLabel()
    #label2.setText("Testing")
    #pixmap = QPixmap('dyna.png')
    #label2.setPixmap(pixmap).scaled(100, 100)

    input_text = QLineEdit()

    btn = QPushButton('Hämta addresser')
    # layout.addWidget(label2)
    layout.addWidget(label)
    layout.addWidget(input_text, 1)
    layout.addWidget(btn)
    btn.clicked.connect(lambda: generate_csv(input_text.text()))
    window.setLayout(layout)
    window.show()
    app.exec_()


main()
