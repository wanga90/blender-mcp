# blender_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context, Image
import socket
import json
import asyncio
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlenderMCPServer")

@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict
    
    def connect(self) -> bool:
        """Connect to the Blender addon socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Blender: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Blender addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Blender: {str(e)}")
            finally:
                self.sock = None

    # Replace the single recv call with this chunked approach
    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        sock.settimeout(10.0)
        
        try:
            while True:
                chunk = sock.recv(buffer_size)
                if not chunk:
                    break
                chunks.append(chunk)
                
                # Check if we've received a complete JSON object
                try:
                    data = b''.join(chunks)
                    json.loads(data.decode('utf-8'))
                    # If we get here, it parsed successfully
                    logger.info(f"Received complete response ({len(data)} bytes)")
                    return data
                except json.JSONDecodeError:
                    # Incomplete JSON, continue receiving
                    continue
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
            
        # Return whatever we got
        data = b''.join(chunks)
        if not data:
            raise Exception("Empty response received")
        return data

# Then in send_command:
# response_data = self.sock.recv(65536)

    
    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Blender and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # Set a timeout for receiving
            self.sock.settimeout(30.0)  # Increased timeout
            
            # Receive the response
            # response_data = self.sock.recv(65536)  # Increase buffer size for larger responses
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Blender error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Blender"))
            
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Blender")
            # Try to reconnect
            self.disconnect()
            if self.connect():
                logger.info("Reconnected to Blender after timeout")
            raise Exception("Timeout waiting for Blender response")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Blender: {str(e)}")
            # Try to log what was received
            if response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Blender: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Blender: {str(e)}")
            # Try to reconnect
            self.disconnect()
            if self.connect():
                logger.info("Reconnected to Blender")
            raise Exception(f"Communication error with Blender: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    blender = BlenderConnection(host="localhost", port=9876)
    
    try:
        # Connect to Blender on startup
        connected = blender.connect()
        if not connected:
            logger.warning("Could not connect to Blender on startup. Make sure the Blender addon is running.")
        
        # Return the Blender connection in the context
        yield {"blender": blender}
    finally:
        # Disconnect from Blender on shutdown
        blender.disconnect()
        logger.info("Disconnected from Blender")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "BlenderMCP",
    description="Blender integration through the Model Context Protocol",
    lifespan=server_lifespan
)

# Resource endpoints

# Global connection for resources (workaround since resources can't access context)
_blender_connection = None

def get_blender_connection():
    global _blender_connection
    if _blender_connection is None:
        _blender_connection = BlenderConnection(host="localhost", port=9876)
        _blender_connection.connect()
    return _blender_connection

@mcp.resource("blender://ping")
def ping_blender() -> str:
    """Simple ping to test Blender connectivity"""
    blender = get_blender_connection()
    
    try:
        result = blender.send_command("ping")
        return f"Ping successful: {json.dumps(result)}"
    except Exception as e:
        return f"Ping failed: {str(e)}"

@mcp.resource("blender://simple")
def get_simple_info() -> str:
    """Get simplified information from Blender"""
    blender = get_blender_connection()
    
    try:
        result = blender.send_command("get_simple_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting simple info: {str(e)}"

@mcp.resource("blender://scene")
def get_scene_info() -> str:
    """
    Get information about the current Blender scene, including all objects, 
    materials, camera settings, and render configuration.
    """
    blender = get_blender_connection()
    
    try:
        scene_info = blender.send_command("get_scene_info")
        return json.dumps(scene_info, indent=2)
    except Exception as e:
        return f"Error getting scene info: {str(e)}"


@mcp.resource("blender://object/{object_name}")
def get_object_info(object_name: str) -> str:
    """
    Get detailed information about a specific object in the Blender scene.
    
    Parameters:
    - object_name: The name of the object to get information about
    """
    blender = get_blender_connection()
    
    try:
        object_info = blender.send_command("get_object_info", {"name": object_name})
        return json.dumps(object_info, indent=2)
    except Exception as e:
        return f"Error getting object info: {str(e)}"

# Tool endpoints

@mcp.tool()
def create_object(
    ctx: Context,
    type: str = "CUBE",
    name: str = None,
    location: List[float] = None,
    rotation: List[float] = None,
    scale: List[float] = None
) -> str:
    """
    Create a new object in the Blender scene.
    
    Parameters:
    - type: Object type (CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, EMPTY, CAMERA, LIGHT)
    - name: Optional name for the object
    - location: Optional [x, y, z] location coordinates
    - rotation: Optional [x, y, z] rotation in radians
    - scale: Optional [x, y, z] scale factors
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    # Set default values for missing parameters
    loc = location or [0, 0, 0]
    rot = rotation or [0, 0, 0]
    sc = scale or [1, 1, 1]
    
    try:
        params = {
            "type": type,
            "location": loc,
            "rotation": rot,
            "scale": sc
        }
        
        if name:
            params["name"] = name
            
        result = blender.send_command("create_object", params)
        return f"Created {type} object: {result['name']}"
    except Exception as e:
        return f"Error creating object: {str(e)}"

@mcp.tool()
def modify_object(
    ctx: Context,
    name: str,
    location: List[float] = None,
    rotation: List[float] = None,
    scale: List[float] = None,
    visible: bool = None
) -> str:
    """
    Modify an existing object in the Blender scene.
    
    Parameters:
    - name: Name of the object to modify
    - location: Optional [x, y, z] location coordinates
    - rotation: Optional [x, y, z] rotation in radians
    - scale: Optional [x, y, z] scale factors
    - visible: Optional boolean to set visibility
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    try:
        params = {"name": name}
        
        if location is not None:
            params["location"] = location
        if rotation is not None:
            params["rotation"] = rotation
        if scale is not None:
            params["scale"] = scale
        if visible is not None:
            params["visible"] = visible
            
        result = blender.send_command("modify_object", params)
        return f"Modified object: {result['name']}"
    except Exception as e:
        return f"Error modifying object: {str(e)}"

@mcp.tool()
def delete_object(ctx: Context, name: str) -> str:
    """
    Delete an object from the Blender scene.
    
    Parameters:
    - name: Name of the object to delete
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    try:
        result = blender.send_command("delete_object", {"name": name})
        return f"Deleted object: {result['deleted']}"
    except Exception as e:
        return f"Error deleting object: {str(e)}"

@mcp.tool()
def set_material(
    ctx: Context,
    object_name: str,
    material_name: str = None,
    color: List[float] = None
) -> str:
    """
    Set or create a material for an object.
    
    Parameters:
    - object_name: Name of the object to assign the material to
    - material_name: Optional name of the material to use/create
    - color: Optional [r, g, b] or [r, g, b, a] color values (0.0-1.0)
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    try:
        params = {
            "object_name": object_name
        }
        
        if material_name:
            params["material_name"] = material_name
        
        if color:
            params["color"] = color
            
        result = blender.send_command("set_material", params)
        
        if "material" in result:
            return f"Set material '{result['material']}' on object '{result['object']}'"
        else:
            return f"Error setting material: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error setting material: {str(e)}"

@mcp.tool()
def render_scene(
    ctx: Context,
    output_path: str = None,
    resolution_x: int = None,
    resolution_y: int = None
) -> str:
    """
    Render the current Blender scene.
    
    Parameters:
    - output_path: Optional path to save the rendered image
    - resolution_x: Optional horizontal resolution in pixels
    - resolution_y: Optional vertical resolution in pixels
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    try:
        params = {}
        
        if output_path:
            params["output_path"] = output_path
        
        if resolution_x is not None:
            params["resolution_x"] = resolution_x
            
        if resolution_y is not None:
            params["resolution_y"] = resolution_y
            
        result = blender.send_command("render_scene", params)
        
        if result.get("rendered"):
            if output_path:
                return f"Scene rendered and saved to {result['output_path']} at resolution {result['resolution'][0]}x{result['resolution'][1]}"
            else:
                return f"Scene rendered at resolution {result['resolution'][0]}x{result['resolution'][1]}"
        else:
            return "Error rendering scene"
    except Exception as e:
        return f"Error rendering scene: {str(e)}"

@mcp.tool()
def execute_blender_code(ctx: Context, code: str) -> str:
    """
    Execute arbitrary Blender Python code.
    
    WARNING: This tool allows executing any Python code in Blender's environment.
    Use with caution as it can modify or delete data.
    
    Parameters:
    - code: The Python code to execute in Blender's context
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    try:
        result = blender.send_command("execute_code", {"code": code})
        
        if result.get("executed"):
            return "Code executed successfully"
        else:
            return "Error executing code"
    except Exception as e:
        return f"Error executing code: {str(e)}"

@mcp.tool()
def create_3d_scene(ctx: Context, description: str) -> str:
    """
    Create a 3D scene based on a natural language description.
    This helper function interprets a description and creates the appropriate objects.
    
    Parameters:
    - description: A natural language description of the 3D scene to create
    """
    blender = ctx.request_context.lifespan_context.get("blender")
    if not blender:
        return "Not connected to Blender"
    
    # First, get the current scene to see what's there
    try:
        scene_info = blender.send_command("get_scene_info")
    except Exception as e:
        return f"Error accessing Blender scene: {str(e)}"
    
    # Parse the description and create a simple scene
    # This is a basic implementation - a more sophisticated version would use
    # natural language understanding to interpret the description more accurately
    
    response = "Creating scene based on your description:\n\n"
    
    try:
        # Split description into parts
        parts = description.lower().split()
        
        # Look for basic scene elements
        if any(word in parts for word in ["ground", "floor", "plane"]):
            # Create a ground plane
            ground = blender.send_command("create_object", {
                "type": "PLANE",
                "name": "Ground",
                "location": [0, 0, 0],
                "scale": [5, 5, 1]
            })
            response += f"✓ Created ground plane '{ground['name']}'\n"
            
            # Set material to gray
            blender.send_command("set_material", {
                "object_name": ground["name"],
                "color": [0.8, 0.8, 0.8]
            })
        
        # Look for cubes
        if any(word in parts for word in ["cube", "box"]):
            cube = blender.send_command("create_object", {
                "type": "CUBE",
                "name": "Cube",
                "location": [0, 0, 1],
                "scale": [1, 1, 1]
            })
            response += f"✓ Created cube '{cube['name']}'\n"
            
            # Set material to blue
            blender.send_command("set_material", {
                "object_name": cube["name"],
                "color": [0.2, 0.4, 0.8]
            })
        
        # Look for spheres
        if any(word in parts for word in ["sphere", "ball"]):
            sphere = blender.send_command("create_object", {
                "type": "SPHERE",
                "name": "Sphere",
                "location": [2, 2, 1],
                "scale": [1, 1, 1]
            })
            response += f"✓ Created sphere '{sphere['name']}'\n"
            
            # Set material to red
            blender.send_command("set_material", {
                "object_name": sphere["name"],
                "color": [0.8, 0.2, 0.2]
            })
        
        # Look for cylinders
        if any(word in parts for word in ["cylinder", "pipe", "tube"]):
            cylinder = blender.send_command("create_object", {
                "type": "CYLINDER",
                "name": "Cylinder",
                "location": [-2, -2, 1],
                "scale": [1, 1, 1]
            })
            response += f"✓ Created cylinder '{cylinder['name']}'\n"
            
            # Set material to green
            blender.send_command("set_material", {
                "object_name": cylinder["name"],
                "color": [0.2, 0.8, 0.2]
            })
        
        # Add a camera if not already in the scene
        if not any(obj.get("type") == "CAMERA" for obj in scene_info["objects"]):
            camera = blender.send_command("create_object", {
                "type": "CAMERA",
                "name": "Camera",
                "location": [7, -7, 5],
                "rotation": [0.9, 0, 2.6]  # Pointing at the origin
            })
            response += f"✓ Added camera '{camera['name']}'\n"
        
        # Add a light if not already in the scene
        if not any(obj.get("type") == "LIGHT" for obj in scene_info["objects"]):
            light = blender.send_command("create_object", {
                "type": "LIGHT",
                "name": "Light",
                "location": [4, 1, 6]
            })
            response += f"✓ Added light '{light['name']}'\n"
        
        response += "\nScene created! You can continue to modify it with specific commands."
        return response
    except Exception as e:
        return f"Error creating scene: {str(e)}"

# Prompts to help users interact with Blender

@mcp.prompt()
def create_simple_scene() -> str:
    """Create a simple Blender scene with basic objects"""
    return """
I'd like to create a simple scene in Blender. Please create:
1. A ground plane
2. A cube above the ground
3. A sphere to the side
4. Make sure there's a camera and light
5. Set different colors for the objects
"""

@mcp.prompt()
def animate_object() -> str:
    """Create keyframe animation for an object"""
    return """
I want to animate a cube moving from point A to point B over 30 frames.
Can you help me create this animation?
"""

@mcp.prompt()
def add_material() -> str:
    """Add a material to an object"""
    return """
I have a cube in my scene. Can you create a blue metallic material and apply it to the cube?
"""



# Main execution

def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()