# -*- coding: utf-8 -*-

# Automatically generated - don't edit.
# Use `python setup.py build_ui` to update it.

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.retorePushButton = QtWidgets.QPushButton(self.groupBox)
        self.retorePushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.retorePushButton.setObjectName("retorePushButton")
        self.gridLayout.addWidget(self.retorePushButton, 0, 1, 1, 1)
        self.restoreLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.restoreLineEdit.setFrame(True)
        self.restoreLineEdit.setReadOnly(True)
        self.restoreLineEdit.setObjectName("restoreLineEdit")
        self.gridLayout.addWidget(self.restoreLineEdit, 0, 0, 1, 1)
        self.restoreTextBrowser = QtWidgets.QTextBrowser(self.groupBox)
        self.restoreTextBrowser.setObjectName("restoreTextBrowser")
        self.gridLayout.addWidget(self.restoreTextBrowser, 2, 0, 1, 1)
        self.detailsPushButton = QtWidgets.QPushButton(self.groupBox)
        self.detailsPushButton.setObjectName("detailsPushButton")
        self.gridLayout.addWidget(self.detailsPushButton, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.groupBox.setTitle(("Restore a Trained Model"))
        self.retorePushButton.setText(("..."))
        self.detailsPushButton.setText(("Details"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

