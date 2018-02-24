import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget,\
    QPushButton, QAction, QLineEdit, QMessageBox, QGridLayout, QLabel,\
    QCheckBox, QComboBox, QSpinBox
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
### For high dpi screen
# from PyQt5 import QtCore
# if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    # QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

# if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    # QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

import click


def text_param(opt):
    param = QLabel(opt.name)
    value = QLineEdit()
    value.setText(opt.default)
    if opt.hide_input:
        value.setEchoMode(QLineEdit.Password)

    # set tip
    param.setToolTip(opt.help)
    # add validator
    if isinstance(opt.type, click.types.IntParamType) and opt.nargs == 1:
        value.setValidator(QtGui.QIntValidator())
    elif isinstance(opt.type, click.types.FloatParamType) and opt.nargs == 1:
        value.setValidator(QtGui.QDoubleValidator())

    def to_command():
        return [opt.opts[0], value.text()]
    return [param, value], to_command


def bool_flag_param(opt):
    checkbox = QCheckBox(opt.name)
    if opt.default:
        checkbox.setCheckState(2)
    # set tip
    checkbox.setToolTip(opt.help)

    def to_command():
        if checkbox.checkState():
            return [opt.opts[0]]
        else:
            return opt.secondary_opts
    return [checkbox], to_command

def choice_param(opt):
    param = QLabel(opt.name)
    # set tip
    param.setToolTip(opt.help)
    cb = QComboBox()
    cb.addItems(opt.type.choices)

    def to_command():
        return [opt.opts[0], cb.currentText()]
    return [param, cb], to_command

def count_param(opt):
    param = QLabel(opt.name)
    # set tip
    param.setToolTip(opt.help)

    sb = QSpinBox()

    def to_command():
        return [opt.opts[0]] * int(sb.text())
    return [param, sb], to_command


def opt_to_widget(opt):
    if opt.is_bool_flag:
        return bool_flag_param(opt)
    elif opt.count:
        return count_param(opt)
    elif isinstance(opt.type, click.types.Choice):
        return choice_param(opt)
    else:
        return text_param(opt)


class App(QWidget):

    def __init__(self, func, run_exit):
        super().__init__()
        self.func = func
        self.title = func.name
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 140
        self.run_exit = run_exit
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.params_func = []
        for i, para in enumerate(self.func.params):
            widget, value_func = opt_to_widget(para)
            self.params_func.append(value_func)
            for idx, w in enumerate(widget):
                if isinstance(w, QtWidgets.QLayout):
                    self.grid.addLayout(w, i, idx)
                else:
                    self.grid.addWidget(w, i, idx)
        # Create a button in the window
        self.button = QPushButton('run', self)
        self.grid.addWidget(self.button, i+1, 0)
        # self.button.move(20, 80)

        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.setLayout(self.grid)

        self.show()

    @pyqtSlot()
    def on_click(self):
        sys.argv = [self.func.name]
        for value_func in self.params_func:
            sys.argv += value_func()
        print(sys.argv)
        self.func(standalone_mode=self.run_exit)


def gui_it(click_func, run_exit=False):
    app = QApplication(sys.argv)
    ex = App(click_func, run_exit)
    # if exit:
    sys.exit(app.exec_())
