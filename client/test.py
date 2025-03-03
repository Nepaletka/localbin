import sys
import socket
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class SocketListener(QObject):
    messageReceived = pyqtSignal(str, str)

    def __init__(self, host="0.0.0.0", port=9000, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.running = False
        self.thread = None
        self.sock = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception as e:
                logging.debug("Socket close error: %s", e)
        if self.thread:
            self.thread.quit()
            self.thread.wait(2000)
            self.thread = None

    def run(self):
        server_address = (self.host, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.sock.bind(server_address)
            self.sock.listen(5)
            self.sock.settimeout(1)
            logging.info("Сервер запущен на %s:%s", *server_address)
            
            while self.running:
                try:
                    client_socket, address = self.sock.accept()
                    ip = address[0]
                    logging.debug("Подключение от %s", ip)
                    self.handle_client(client_socket, ip)
                except socket.timeout:
                    continue
                except Exception as e:
                    logging.error("Ошибка accept: %s", e)
                    break
        finally:
            self.sock.close()
            logging.info("Сервер остановлен")

    def handle_client(self, client_socket, ip):
        with client_socket:
            try:
                client_socket.settimeout(1)
                while self.running:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode().strip()
                    if message == "HELLO":
                        client_socket.send(b"READY")
                    else:
                        self.messageReceived.emit(ip, message)
            except socket.timeout:
                pass
            except Exception as e:
                logging.error("Ошибка клиента %s: %s", ip, e)

class BackgroundClient(QObject):
    def __init__(self, app: QApplication, icon_path: str = ""):
        super().__init__()
        self.app = app
        self.trayIcon = QSystemTrayIcon(QIcon(icon_path))
        self.trayIcon.setToolTip("Clipboard Client")
        
        menu = QMenu()
        restart_action = QAction("Перезапустить сервер", self.app)
        restart_action.triggered.connect(self.restart_server)
        
        exit_action = QAction("Выход", self.app)
        exit_action.triggered.connect(self.exit_application)
        
        menu.addAction(restart_action)
        menu.addAction(exit_action)
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.show()
        
        self.listener = SocketListener()
        self.listener.messageReceived.connect(self.on_message)
        self.listener.start()

    def restart_server(self):
        self.listener.stop()
        self.listener = SocketListener()
        self.listener.messageReceived.connect(self.on_message)
        self.listener.start()
        logging.info("Сервер перезапущен")

    def exit_application(self):
        self.listener.stop()
        self.app.quit()

    def on_message(self, ip: str, message: str):
        msg = QMessageBox()
        msg.setWindowTitle("Новые данные")
        msg.setText(f"Получено сообщение от {ip}\nРазрешить вставить данные в буфер обмена?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            QApplication.clipboard().setText(message)
            logging.info("Буфер обновлён данными от %s", ip)
        else:
            logging.info("Обновление отклонено")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Ошибка", "Системный трей недоступен")
        sys.exit(1)
        
    client = BackgroundClient(app, "icon.png")  # Укажите путь к иконке
    sys.exit(app.exec())