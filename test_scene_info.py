import socket
import json
import time

def test_scene_info():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Connecting to Blender...")
        sock.connect(('localhost', 9876))
        print("Connected!")
        
        # Scene info command
        command = {
            "type": "get_scene_info",
            "params": {}
        }
        
        print(f"Sending command: {json.dumps(command)}")
        sock.sendall(json.dumps(command).encode('utf-8'))
        
        print(f"Setting socket timeout: 15 seconds")
        sock.settimeout(15)
        
        print("Waiting for response...")
        try:
            # Receive data in chunks
            chunks = []
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                chunks.append(chunk)
                
                # Try to parse the JSON to see if we have a complete response
                try:
                    data = b''.join(chunks)
                    json.loads(data.decode('utf-8'))
                    # If we get here, we have a complete response
                    break
                except json.JSONDecodeError:
                    # Incomplete JSON, continue receiving
                    continue
            
            data = b''.join(chunks)
            print(f"Received {len(data)} bytes")
            
            if data:
                response = json.loads(data.decode('utf-8'))
                print(f"Response status: {response.get('status')}")
                if response.get('status') == 'success':
                    result = response.get('result', {})
                    print(f"Scene name: {result.get('name')}")
                    print(f"Object count: {result.get('object_count')}")
                    print(f"Objects returned: {len(result.get('objects', []))}")
                else:
                    print(f"Error: {response.get('message')}")
            else:
                print("Received empty response")
        except socket.timeout:
            print("Socket timeout while waiting for response")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
    finally:
        sock.close()

if __name__ == "__main__":
    test_scene_info() 