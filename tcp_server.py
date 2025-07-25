import socket
import threading
import serial
import time
import signal
import sys

debug_output = True
shutdown_flag = threading.Event()
active_connections = []

def wait_for_serial(port_name, baud_rate):
    while not shutdown_flag.is_set():
        try:
            ser = serial.Serial(port_name, baud_rate, timeout=1)
            print(f"Serial port {port_name} opened.")
            return ser
        except serial.SerialException:
            print(f"Waiting for {port_name}...")
            time.sleep(0.5)
    return None

def handle_connection(conn, addr, serial_port_name, baud_rate):
    glove_ip = addr[0]
    print(f"{glove_ip} connected, assigned to {serial_port_name}")

    ser = wait_for_serial(serial_port_name, baud_rate)
    if not ser:
        print(f"Aborting connection handler for {serial_port_name}")
        conn.close()
        return

    conn_file = conn.makefile('rw')
    active_connections.append((conn, ser, conn_file))

    def messager():
        while not shutdown_flag.is_set():
            try:
                line = conn_file.readline()
                if not line:
                    break
                if debug_output:
                    print(f"[TCP->{serial_port_name}] {line.strip()}")
                ser.write((line.strip() + '\n').encode('utf-8'))
            except Exception as e:
                print(f"[ERROR] TCP->Serial ({serial_port_name}): {e}")
                break

    def responder():
        while not shutdown_flag.is_set():
            try:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    if debug_output:
                        print(f"[{serial_port_name}->TCP] {line}")
                    conn_file.write(line + '\n')
                    conn_file.flush()
            except Exception as e:
                print(f"[ERROR] Serial->TCP ({serial_port_name}): {e}")
                break

    t1 = threading.Thread(target=messager, daemon=True)
    t2 = threading.Thread(target=responder, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    conn_file.close()
    conn.close()
    ser.close()
    active_connections.remove((conn, ser, conn_file))
    print(f"[{serial_port_name}] Connection closed")

def start_server(config):
    left_glove_ip = config["left_glove_ip"]
    right_glove_ip = config["right_glove_ip"]
    left_port = config["left_glove_com_port"]
    right_port = config["right_glove_com_port"]
    baud_rate = config["baud_rate"]
    host = config["host_ip"]
    port = config["tcp_port"]

    print(f"\nStarting server on {host}:{port}")
    print(f"Waiting for connections from:\n Left Glove:  {left_glove_ip}\n Right Glove: {right_glove_ip}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    server.settimeout(1.0)  # Timeout allows periodic shutdown check

    def shutdown_handler(sig, frame):
        print("\nShutting down server...")
        shutdown_flag.set()
        server.close()
        for conn, ser, conn_file in active_connections:
            try:
                conn_file.close()
                conn.close()
                ser.close()
            except Exception:
                pass
        sys.exit(0)

    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, shutdown_handler)

    try:
        while not shutdown_flag.is_set():
            try:
                conn, addr = server.accept()
                ip = addr[0]
                if ip == left_glove_ip:
                    print("Left glove connected")
                    threading.Thread(target=handle_connection, args=(conn, addr, left_port, baud_rate), daemon=True).start()
                elif ip == right_glove_ip:
                    print("Right glove connected")
                    threading.Thread(target=handle_connection, args=(conn, addr, right_port, baud_rate), daemon=True).start()
                else:
                    print(f"Unknown device connected from {ip}. Please check config.json.")
                    conn.close()
            except socket.timeout:
                continue
    except Exception as e:
        print(f"Server error: {e}")
        shutdown_handler(None, None)
