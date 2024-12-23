import socket
import logging
import datetime

# Configure logging to store captured traffic
logging.basicConfig(
    filename=f"captured_packets_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def start_udp_listener(host="0.0.0.0", port=9999):
    """
    Starts a UDP server to capture incoming packets and log their details.
    """
    print(f"Starting UDP listener on {host}:{port}...")
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Listening for packets on {host}:{port}")

    try:
        while True:
            # Receive packets (max UDP size: 65535 bytes)
            data, addr = sock.recvfrom(65535)
            src_ip, src_port = addr
            dst_ip, dst_port = sock.getsockname()

            # Log and display packet details
            packet_info = f"Source: {src_ip}:{src_port}, Destination: {dst_ip}:{dst_port}, Data: {data.hex()}"
            logging.info(packet_info)
            print(packet_info)

    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Host and port configuration
    host_ip = input("Enter the IP address to host (e.g., 0.0.0.0 for all interfaces): ")
    port = int(input("Enter the port to listen on (e.g., 9999): "))
    
    # Start the UDP listener
    start_udp_listener(host=host_ip, port=port)
