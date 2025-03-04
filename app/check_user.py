import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main(host):
    """Check if a host is ready by sending HELLO and expecting READY."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.01)
            sock.connect((host, 9000))
            sock.sendall(b"HELLO")
            response = sock.recv(4096).decode('utf-8')
            if response == "READY":
                logging.info("%s is ready for connection", host)
                return host
            else:
                logging.warning("%s did not respond correctly", host)
                return None
    except Exception as e:
        logging.error("Connection error with %s: %s", host, e)
        return None

if __name__ == '__main__':
    main("127.0.0.1")