# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alyvix_object_selection_view.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(235, 272)
        self.listWidgetAlyObj = QtGui.QListWidget(Form)
        self.listWidgetAlyObj.setGeometry(QtCore.QRect(8, 28, 218, 191))
        self.listWidgetAlyObj.setObjectName(_fromUtf8("listWidgetAlyObj"))
        self.pushButtonNew = QtGui.QPushButton(Form)
        self.pushButtonNew.setGeometry(QtCore.QRect(8, 235, 60, 23))
        self.pushButtonNew.setObjectName(_fromUtf8("pushButtonNew"))
        self.pushButtonEdit = QtGui.QPushButton(Form)
        self.pushButtonEdit.setGeometry(QtCore.QRect(80, 235, 60, 23))
        self.pushButtonEdit.setObjectName(_fromUtf8("pushButtonEdit"))
        self.pushButtonRemove = QtGui.QPushButton(Form)
        self.pushButtonRemove.setGeometry(QtCore.QRect(151, 235, 75, 23))
        self.pushButtonRemove.setObjectName(_fromUtf8("pushButtonRemove"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(8, 7, 211, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayoutWidget = QtGui.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(8, 362, 218, 177))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButtonRF = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButtonRF.setObjectName(_fromUtf8("pushButtonRF"))
        self.gridLayout.addWidget(self.pushButtonRF, 0, 0, 1, 1)
        self.pushButtonTF = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButtonTF.setEnabled(True)
        self.pushButtonTF.setObjectName(_fromUtf8("pushButtonTF"))
        self.gridLayout.addWidget(self.pushButtonTF, 2, 0, 1, 1)
        self.pushButtonOF = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButtonOF.setEnabled(True)
        self.pushButtonOF.setObjectName(_fromUtf8("pushButtonOF"))
        self.gridLayout.addWidget(self.pushButtonOF, 3, 0, 1, 1)
        self.pushButtonIF = QtGui.QPushButton(self.gridLayoutWidget)
        self.pushButtonIF.setObjectName(_fromUtf8("pushButtonIF"))
        self.gridLayout.addWidget(self.pushButtonIF, 1, 0, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(Form)
        self.pushButtonCancel.setGeometry(QtCore.QRect(62, 547, 111, 23))
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.spinBoxDelay = QtGui.QSpinBox(Form)
        self.spinBoxDelay.setGeometry(QtCore.QRect(184, 332, 42, 22))
        self.spinBoxDelay.setMaximum(60)
        self.spinBoxDelay.setObjectName(_fromUtf8("spinBoxDelay"))
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(135, 333, 37, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pushButtonCC = QtGui.QPushButton(Form)
        self.pushButtonCC.setEnabled(True)
        self.pushButtonCC.setGeometry(QtCore.QRect(9, 632, 216, 23))
        self.pushButtonCC.setObjectName(_fromUtf8("pushButtonCC"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Alyvix - Select Finder", None))
        self.pushButtonNew.setText(_translate("Form", "New", None))
        self.pushButtonEdit.setText(_translate("Form", "Edit", None))
        self.pushButtonRemove.setText(_translate("Form", "Remove", None))
        self.label.setText(_translate("Form", "Alyvix Objects:", None))
        self.pushButtonRF.setText(_translate("Form", "Rect Finder", None))
        self.pushButtonTF.setText(_translate("Form", "Text Finder", None))
        self.pushButtonOF.setText(_translate("Form", "Object Finder", None))
        self.pushButtonIF.setText(_translate("Form", "Image Finder", None))
        self.pushButtonCancel.setText(_translate("Form", "Cancel", None))
        self.label_2.setText(_translate("Form", "Delay:", None))
        self.pushButtonCC.setText(_translate("Form", "Custom Code", None))

