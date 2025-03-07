import socket
import json
import time

def test_simple_command():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Connecting to Blender...")
        sock.connect(('localhost', 9876))
        print("Connected!")
        
        # Simple ping command
        command = {
            "type": "ping",
            "params": {}
        }
        
        print(f"Sending command: {json.dumps(command)}")
        sock.sendall(json.dumps(command).encode('utf-8'))
        
        print(f"Setting socket timeout: 10 seconds")
        sock.settimeout(10)
        
        print("Waiting for response...")
        try:
            response_data = sock.recv(65536)
            print(f"Received {len(response_data)} bytes")
            
            if response_data:
                response = json.loads(response_data.decode('utf-8'))
                print(f"Response: {response}")
            else:
                print("Received empty response")
        except socket.timeout:
            print("Socket timeout while waiting for response")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_simple_command()