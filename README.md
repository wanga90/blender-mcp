# BlenderMCP - Blender Model Context Protocol Integration

BlenderMCP connects Blender to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Blender. This integration enables AI-assisted 3D modeling, scene manipulation, and rendering.

## Features

- **Two-way communication**: Connect Claude AI to Blender through a socket-based server
- **Object manipulation**: Create, modify, and delete 3D objects in Blender
- **Material control**: Apply and modify materials and colors
- **Scene inspection**: Get detailed information about the current Blender scene
- **Code execution**: Run arbitrary Python code in Blender from Claude

## Components

The system consists of two main components:

1. **Blender Addon (`blender_mcp_addon.py`)**: A Blender addon that creates a socket server within Blender to receive and execute commands
2. **MCP Server (`blender_mcp_server.py`)**: A Python server that implements the Model Context Protocol and connects to the Blender addon

## Installation

### Prerequisites

- Blender 3.0 or newer
- Python 3.7 or newer
- MCP library (`pip install mcp`)

### Quick Start

Run blender-mcp without installing it permanently (pipx will automatically download and run the package):

```bash
pipx run blender-mcp
```

If you don't have pipx installed, you can install it with:

```bash
python -m pip install pipx
```

### Claude for Desktop Integration

Update your `claude_desktop_config.json` (located in `~/Library/Application\ Support/Claude/claude_desktop_config.json` on macOS and `%APPDATA%/Claude/claude_desktop_config.json` on Windows) to include the following:

```json
{
    "mcpServers": {
        "blender": {
            "command": "pipx",
            "args": [
                "run",
                "blender-mcp"
            ]
        }
    }
}
```

This configuration allows Claude for Desktop to automatically start the Blender MCP server when needed. The pipx command will handle both downloading and running the package in one step.

### Installing the Blender Addon

1. Open Blender
2. Go to Edit > Preferences > Add-ons
3. Click "Install..." and select the `blender_mcp_addon.py` file
4. Enable the addon by checking the box next to "Interface: Blender MCP"

### Setting up the MCP Server

1. Install the required Python packages:
   ```
   pip install mcp
   ```
2. Run the MCP server:
   ```
   python blender_mcp_server.py
   ```

## Usage

### Starting the Connection

1. In Blender, go to the 3D View sidebar (press N if not visible)
2. Find the "BlenderMCP" tab
3. Set the port number (default: 9876)
4. Click "Start MCP Server"
5. Make sure the MCP server is running in your terminal

### Using with Claude

Once connected, Claude can interact with Blender using the following capabilities:

#### Resources

- `blender://ping` - Check connectivity
- `blender://simple` - Get basic Blender information
- `blender://scene` - Get detailed scene information
- `blender://object/{object_name}` - Get information about a specific object

#### Tools

- `create_primitive` - Create basic primitive objects with optional color
- `set_object_property` - Set a single property of an object
- `create_object` - Create a new object with detailed parameters
- `modify_object` - Modify an existing object's properties
- `delete_object` - Remove an object from the scene
- `set_material` - Apply or create materials for objects
- `execute_blender_code` - Run arbitrary Python code in Blender

### Example Commands

Here are some examples of what you can ask Claude to do:

- "Create a blue cube at position [0, 1, 0]"
- "Make the cube red"
- "Create a sphere and place it above the cube"
- "Get information about the current scene"
- "Delete the cube"

## Troubleshooting

- **Connection issues**: Make sure both the Blender addon server and the MCP server are running
- **Command failures**: Check the console in Blender for error messages
- **Timeout errors**: Try simplifying your requests or breaking them into smaller steps

## Technical Details

### Communication Protocol

The system uses a simple JSON-based protocol over TCP sockets:

- **Commands** are sent as JSON objects with a `type` and optional `params`
- **Responses** are JSON objects with a `status` and `result` or `message`

### Security Considerations

The `execute_blender_code` tool allows running arbitrary Python code in Blender, which can be powerful but potentially dangerous. Use with caution in production environments.

## Limitations

- The connection is local only (localhost)
- Large data transfers may cause timeouts
- Complex operations might need to be broken down into smaller steps

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your license information here]
