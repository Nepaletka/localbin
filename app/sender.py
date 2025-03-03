import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    """Placeholder for standalone execution."""
    pass

def send_clipboard_to_user(user, clipboard):
    """Send clipboard data to a specific user via socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((user, 9000))
            data = clipboard.encode('utf-8')
            sock.sendall(data)
            logging.info("Data sent to user %s", user)
        return True
    except Exception as e:
        logging.error("Connection error with %s: %s", user, e)
        return False

if __name__ == '__main__':
    main()