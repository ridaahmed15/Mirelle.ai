
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
    QDialog,
    QListWidget,
    QMessageBox
)

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from ai.ollama_client import MirelleAI


# ==========================================
# AI WORKER
# ==========================================

class AIWorker(QThread):

    finished = Signal(str)

    def __init__(self, ai, message):
        super().__init__()

        self.ai = ai
        self.message = message

    def run(self):

        try:
            reply = self.ai.chat(self.message)

        except Exception as e:
            reply = f"Something went wrong: {e}"

        self.finished.emit(reply)


# ==========================================
# SMART MEMORY VIEWER
# ==========================================

class MemoryViewerDialog(QDialog):

    def __init__(self, memory_manager, parent=None):

        super().__init__(parent)

        self.memory = memory_manager

        self.setWindowTitle("Mirelle | Smart Memory")
        self.resize(550, 500)

        self.setStyleSheet("""
            QDialog {
                background-color: #0b0e13;
                color: #e8edf5;
            }

            QLabel {
                color: #e8edf5;
            }

            QListWidget {
                background-color: #151b24;
                color: #e8edf5;
                border: 1px solid #273444;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }

            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #273444;
            }

            QListWidget::item:selected {
                background-color: #174d45;
            }

            QPushButton {
                background-color: #19b89a;
                color: #07130f;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #32d5b3;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(15)

        heading = QLabel("🧠 Mirelle's Smart Memory")

        heading.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
            color: #35d6b0;
        """)

        description = QLabel(
            "These are the important facts Mirelle remembers."
        )

        self.memory_list = QListWidget()

        # Buttons
        button_layout = QHBoxLayout()

        refresh_button = QPushButton("Refresh")
        delete_button = QPushButton("Delete Selected")
        close_button = QPushButton("Close")

        refresh_button.clicked.connect(self.load_memories)
        delete_button.clicked.connect(self.delete_selected)
        close_button.clicked.connect(self.close)

        button_layout.addWidget(refresh_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(close_button)

        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addWidget(self.memory_list, 1)
        layout.addLayout(button_layout)

        self.load_memories()

    # Load saved memories
    def load_memories(self):

        self.memory_list.clear()

        facts = self.memory.get_facts()

        if not facts:
            self.memory_list.addItem("No saved memories yet.")
            return

        for fact in facts:

            key = fact["key"]
            value = fact["value"]

            self.memory_list.addItem(
                f"{key.replace('_', ' ').title()}\n{value}"
            )

            item = self.memory_list.item(
                self.memory_list.count() - 1
            )

            item.setData(Qt.UserRole, key)

    # Delete selected memory
    def delete_selected(self):

        item = self.memory_list.currentItem()

        if item is None:

            QMessageBox.information(
                self,
                "Select Memory",
                "Please select a memory first."
            )

            return

        key = item.data(Qt.UserRole)

        if not key:
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this memory?\n\n{key}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:

            self.memory.delete_fact(key)

            self.load_memories()

            QMessageBox.information(
                self,
                "Memory Deleted",
                "The selected memory has been deleted."
            )


# ==========================================
# MAIN MIRELLE WINDOW
# ==========================================

class MirelleWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.ai = MirelleAI()
        self.worker = None

        self.setWindowTitle("Mirelle | AI Companion")
        self.resize(1000, 700)
        self.setMinimumSize(750, 550)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0e13;
            }

            QWidget {
                color: #e8edf5;
                font-family: Segoe UI;
            }

            QFrame#sidebar {
                background-color: #10151d;
                border-right: 1px solid #202b37;
            }

            QFrame#header {
                background-color: #10151d;
                border-bottom: 1px solid #202b37;
            }

            QTextEdit {
                background-color: #151b24;
                border: 1px solid #273444;
                border-radius: 12px;
                padding: 12px;
                color: #f0f3f8;
                font-size: 14px;
            }

            QPushButton {
                background-color: #19b89a;
                color: #07130f;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #32d5b3;
            }

            QPushButton:disabled {
                background-color: #35434a;
                color: #8d9b9c;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================================
        # SIDEBAR
        # ==================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        side_layout = QVBoxLayout(sidebar)

        side_layout.setContentsMargins(
            22, 25, 22, 20
        )

        logo = QLabel("MIRELLE")

        logo.setStyleSheet("""
            color: #35d6b0;
            font-size: 23px;
            font-weight: bold;
        """)

        tagline = QLabel("Your personal AI")

        tagline.setStyleSheet(
            "color: #788696; font-size: 12px;"
        )

        status = QLabel("●  LOCAL AI ONLINE")

        status.setStyleSheet(
            "color: #38c99e; margin-top: 25px;"
        )

        side_layout.addWidget(logo)
        side_layout.addWidget(tagline)
        side_layout.addWidget(status)

        # Smart Memory Button
        memory_button = QPushButton("🧠  Smart Memory")

        memory_button.setFixedHeight(45)

        memory_button.clicked.connect(
            self.open_memory_viewer
        )

        side_layout.addWidget(memory_button)

        side_layout.addStretch()

        version = QLabel("Mirelle • Version 0.3")

        version.setStyleSheet(
            "color: #657180; font-size: 11px;"
        )

        side_layout.addWidget(version)

        main_layout.addWidget(sidebar)

        # ==================================
        # MAIN CHAT AREA
        # ==================================

        chat_area = QWidget()

        chat_layout = QVBoxLayout(chat_area)

        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(75)

        header_layout = QHBoxLayout(header)

        header_layout.setContentsMargins(
            25, 10, 25, 10
        )

        title = QLabel("Mirelle")

        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        subtitle = QLabel("Your AI companion")

        subtitle.setStyleSheet(
            "color: #8492a3; font-size: 12px;"
        )

        title_box = QVBoxLayout()

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        chat_layout.addWidget(header)

        # Chat display
        self.chat_display = QTextEdit()

        self.chat_display.setReadOnly(True)

        self.chat_display.setFont(
            QFont("Segoe UI", 11)
        )

        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #0b0e13;
                border: none;
                padding: 25px;
            }
        """)

        chat_layout.addWidget(
            self.chat_display, 1
        )

        # Load previous chat history
        self.load_chat_history()

        # ==================================
        # MESSAGE INPUT
        # ==================================

        bottom = QWidget()

        bottom_layout = QHBoxLayout(bottom)

        bottom_layout.setContentsMargins(
            20, 15, 20, 20
        )

        bottom_layout.setSpacing(12)

        self.input_box = QTextEdit()

        self.input_box.setFixedHeight(65)

        self.input_box.setPlaceholderText(
            "Message Mirelle..."
        )

        self.send_button = QPushButton("Send")

        self.send_button.setFixedWidth(100)
        self.send_button.setFixedHeight(60)

        self.send_button.clicked.connect(
            self.send_message
        )

        bottom_layout.addWidget(
            self.input_box, 1
        )

        bottom_layout.addWidget(
            self.send_button
        )

        chat_layout.addWidget(bottom)

        main_layout.addWidget(
            chat_area, 1
        )

    # ==================================
    # OPEN MEMORY VIEWER
    # ==================================

    def open_memory_viewer(self):

        dialog = MemoryViewerDialog(
            self.ai.memory,
            self
        )

        dialog.exec()

    # ==================================
    # LOAD CHAT HISTORY
    # ==================================

    def load_chat_history(self):

        history = self.ai.conversation_history

        if not history:

            self.add_message(
                "Mirelle",
                "Hello! I'm Mirelle, your local AI companion. ❤️ "
                "I'm ready to talk with you."
            )

            return

        for message in history:

            if message["role"] == "user":

                self.add_message(
                    "You",
                    message["content"]
                )

            elif message["role"] == "assistant":

                self.add_message(
                    "Mirelle",
                    message["content"]
                )

        self.scroll_to_bottom()

    # ==================================
    # DISPLAY MESSAGE
    # ==================================

    def add_message(self, sender, message):

        if sender == "You":
            color = "#35d6b0"
        else:
            color = "#9bafff"

        safe_message = (
            message.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

        self.chat_display.append(
            f'<p style="margin-top:18px;">'
            f'<span style="color:{color}; font-weight:bold;">'
            f'{sender}</span><br>'
            f'<span style="color:#e1e7ef;">'
            f'{safe_message}</span>'
            f'</p>'
        )

        self.scroll_to_bottom()

    # ==================================
    # SCROLL TO BOTTOM
    # ==================================

    def scroll_to_bottom(self):

        scrollbar = (
            self.chat_display.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    # ==================================
    # SEND MESSAGE
    # ==================================

    def send_message(self):

        message = (
            self.input_box.toPlainText().strip()
        )

        if not message:
            return

        if (
            self.worker is not None
            and self.worker.isRunning()
        ):
            return

        self.add_message("You", message)

        self.input_box.clear()

        self.send_button.setEnabled(False)
        self.send_button.setText("Thinking...")

        self.worker = AIWorker(
            self.ai,
            message
        )

        self.worker.finished.connect(
            self.receive_reply
        )

        self.worker.start()

    # ==================================
    # RECEIVE AI RESPONSE
    # ==================================

    def receive_reply(self, reply):

        self.add_message("Mirelle", reply)

        self.send_button.setEnabled(True)
        self.send_button.setText("Send")


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MirelleWindow()

    window.show()

    sys.exit(app.exec())

