
from interface.main_window import MirelleWindow
from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MirelleWindow()
    window.show()

    sys.exit(app.exec())
