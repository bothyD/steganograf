from control.PlotBuilder import PlotBuilder
import numpy as np
import ui

import sys
import PyQt6.QtWidgets

if __name__ == "__main__":
    # sys.settrace(None)
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    window = ui.MainWindow()
    window.show()
    app.exec()
