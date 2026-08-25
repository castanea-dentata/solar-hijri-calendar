import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from .database import Database
from .ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Solar Hijri Calendar")
    app.setQuitOnLastWindowClosed(False)  # keep running in tray for reminders

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.warning(
            None, "No system tray detected",
            "Reminders will only be checked while the window is open, since "
            "no system tray was found on this desktop.",
        )

    db = Database()
    window = MainWindow(db)
    window.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
