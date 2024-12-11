from SerialUi import SerialUi
from PyQt5.QtWidgets import QApplication
from SerialSetting import SerialSetting
import sys

if __name__ == '__main__':
    
    app = QApplication([])
    
    # serialui = SerialUi()
    # serialui.show()
    # app.exec_()
    ser = SerialSetting()

    sys.exit(app.exec_())