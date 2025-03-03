import socket
import threading
import logging
import pyperclip

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    """Start the client server to listen for connections."""
    server_address = ("0.0.0.0", 9000)  # Listen on all interfaces
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(server_address)
        sock.listen(5)
        logging.info("Client started and listening on %s:%s", *server_address)

        while True:
            client, address = sock.accept()
            logging.info("Connection from %s", address)
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()

def handle_client(client_socket):
    """Handle incoming client connections and clipboard operations."""
    with client_socket as sock:
        try:
            request = sock.recv(1024).decode("utf-8")
            if request == "HELLO":
                clipboard_data = pyperclip.paste()
                # Test clipboard accessibility
                pyperclip.copy('TEST')
                if pyperclip.paste() == "TEST":
                    pyperclip.copy(clipboard_data)
                    sock.send(b"READY")
                    logging.info("Sent READY confirmation")
                else:
                    logging.error("Clipboard access error")
                    sock.send(b"ERROR")
            else:
                pyperclip.copy(request)
                logging.info("Clipboard updated: %s", request)
        except Exception as e:
            logging.error("Request handling error: %s", e)

if __name__ == '__main__':
    main()