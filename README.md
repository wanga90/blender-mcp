# BlenderMCP Setup Guide

This guide will walk you through setting up BlenderMCP, which allows Claude to communicate with Blender through the Model Context Protocol (MCP).

## Prerequisites

- Blender 3.0 or newer
- Python 3.9 or newer
- Claude Desktop or Cursor
- Basic familiarity with Blender and Python

## Installation Steps

### 1. Install the BlenderMCP Addon in Blender

1. Save the `blender_addon.py` file to your computer
2. Open Blender
3. Go to Edit > Preferences > Add-ons
4. Click "Install..." and select the `blender_addon.py` file
5. Enable the addon by checking the box next to "Interface: Blender MCP"

### 2. Set Up the MCP Server

1. Install the MCP Python package:
   ```bash
   pip install "mcp[cli]"
   ```

2. Save the `blender_mcp_server.py` file to your computer

3. Install the server in Claude Desktop:
   ```bash
   mcp install blender_mcp_server.py
   ```
   
   Alternatively, you can run the server in development mode:
   ```bash
   mcp dev blender_mcp_server.py
   ```

### 3. Start the Blender Server

1. In Blender, go to the 3D View
2. Open the sidebar (press N if it's not visible)
3. Select the "BlenderMCP" tab
4. Click "Start MCP Server" (default port is 9876)

### 4. Connect Claude to Blender

1. Open Claude Desktop
2. The BlenderMCP server should now be available in Claude's MCP connections
3. Start a conversation with Claude and you can now control Blender using natural language!

## Usage Examples

Here are some examples of commands you can give Claude to control Blender:

### Basic Scene Creation

```
Create a simple scene with a cube, sphere, and a ground plane.
```

### Manipulating Objects

```
Move the cube 2 units up along the Z-axis.
```

```
Scale the sphere to be twice its current size.
```

```
Rotate the cylinder 45 degrees around the Y-axis.
```

### Material Operations

```
Create a red glossy material and apply it to the cube.
```

```
Make the sphere blue with some metallic properties.
```

### Rendering

```
Render the current scene and save it to my desktop.
```

```
Change the render resolution to 1920x1080 and render the scene.
```

## Troubleshooting

### MCP Server Connection Issues

If Claude can't connect to the MCP server:

1. Make sure the Blender addon is running (check the BlenderMCP panel in Blender)
2. Verify the port number in Blender matches what the MCP server is expecting (default: 9876)
3. Restart the MCP server in Claude Desktop
4. Restart Blender and try again

### Addon Issues

If the Blender addon isn't working:

1. Check the Blender system console for error messages
2. Verify that the addon is enabled in Blender's preferences
3. Try reinstalling the addon

## Advanced Configuration

### Customizing the Port

You can change the default port (9876) in the BlenderMCP panel in Blender. If you change this port, you'll need to update the `BlenderConnection` in the MCP server code accordingly.

### Adding New Commands

The system is designed to be extensible. You can add new commands by:

1. Adding new methods to the `BlenderMCPServer` class in the Blender addon
2. Adding corresponding tools or resources to the MCP server

## Security Considerations

- The `execute_blender_code` tool allows arbitrary code execution within Blender. Use with caution!
- The socket connection between the MCP server and Blender is not encrypted or authenticated.
- Always review the commands Claude suggests before allowing them to execute in Blender.



---

# BlenderMCP Usage Examples

These examples demonstrate the natural language capabilities and show how Claude can understand scene context and provide intelligent assistance.

## Basic Scene Creation

### Example 1: Creating a Simple Scene

**User**: "Create a basic scene with a cube sitting on a plane."

**Claude's Understanding and Actions**:
1. Recognizes need for a ground plane and a cube object
2. Creates a plane at origin with appropriate scale
3. Creates a cube positioned above the plane
4. Sets basic materials for visibility
5. Ensures camera and lighting are properly positioned

**MCP Tools Used**:
- `create_object` tool for the plane and cube
- `set_material` tool for materials
- `modify_object` tool for positioning

### Example 2: Building a Table

**User**: "I want to create a simple table with four legs."

**Claude's Understanding and Actions**:
1. Creates a flattened cube for the tabletop
2. Creates four cylinders for table legs
3. Positions legs at the corners of the tabletop
4. Applies appropriate materials
5. Reports back the created objects and their relationships

**Implementation via BlenderMCP**:
```python
# Create tabletop
tabletop = blender.send_command("create_object", {
    "type": "CUBE",
    "name": "Tabletop",
    "location": [0, 0, 1],
    "scale": [2, 1, 0.1]
})

# Create and position legs
leg_positions = [
    [1.8, 0.8, 0.5],  # front-right
    [1.8, -0.8, 0.5], # back-right
    [-1.8, 0.8, 0.5], # front-left
    [-1.8, -0.8, 0.5] # back-left
]

for i, pos in enumerate(leg_positions):
    leg = blender.send_command("create_object", {
        "type": "CYLINDER",
        "name": f"Leg_{i+1}",
        "location": pos,
        "scale": [0.1, 0.1, 0.5]
    })
```

## Object Manipulation

### Example 3: Moving and Scaling Objects

**User**: "Make the cube twice as big and move it 3 units higher."

**Claude's Understanding and Actions**:
1. Identifies the cube in the scene
2. Uses `modify_object` tool to scale it by a factor of 2
3. Adjusts the z-coordinate to move it upward
4. Reports the new position and scale

### Example 4: Complex Transformation

**User**: "Arrange five spheres in a circular pattern around the origin."

**Claude's Understanding and Actions**:
1. Calculates positions in a circular pattern using trigonometry
2. Creates five spheres with appropriate positioning
3. Possibly applies different materials for visibility

**Implementation via BlenderMCP**:
```python
import math

# Calculate positions in a circle
radius = 3
num_spheres = 5
for i in range(num_spheres):
    angle = 2 * math.pi * i / num_spheres
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    # Create sphere at calculated position
    sphere = blender.send_command("create_object", {
        "type": "SPHERE",
        "name": f"Sphere_{i+1}",
        "location": [x, y, 1],
        "scale": [0.5, 0.5, 0.5]
    })
    
    # Apply different colors
    hue = i / num_spheres
    r, g, b = hsv_to_rgb(hue, 0.8, 0.8)
    blender.send_command("set_material", {
        "object_name": sphere["name"],
        "color": [r, g, b]
    })
```

## Material and Appearance

### Example 5: Creating and Applying Materials

**User**: "Create a glossy red material and apply it to the cube."

**Claude's Understanding and Actions**:
1. Uses `set_material` tool with appropriate color values
2. May use `execute_blender_code` for more advanced material settings
3. Reports back the material creation and assignment

### Example 6: Scene Lighting

**User**: "Make the scene brighter with a three-point lighting setup."

**Claude's Understanding and Actions**:
1. Creates three lights (key, fill, and back)
2. Positions them appropriately for three-point lighting
3. Sets different intensities for each light
4. May adjust the existing environment lighting

**Implementation via BlenderMCP**:
```python
# Create key light (main light)
key_light = blender.send_command("create_object", {
    "type": "LIGHT",
    "name": "Key_Light",
    "location": [4, -4, 5]
})

# Create fill light (softer, fills shadows)
fill_light = blender.send_command("create_object", {
    "type": "LIGHT",
    "name": "Fill_Light", 
    "location": [-4, -2, 3]
})

# Create back light (rim light)
back_light = blender.send_command("create_object", {
    "type": "LIGHT",
    "name": "Back_Light",
    "location": [0, 5, 4]
})

# Set light properties using execute_code
blender.send_command("execute_code", {
    "code": """
import bpy
# Set key light properties
key = bpy.data.objects['Key_Light']
key.data.energy = 1000
key.data.type = 'AREA'

# Set fill light properties
fill = bpy.data.objects['Fill_Light']
fill.data.energy = 400
fill.data.type = 'AREA'

# Set back light properties
back = bpy.data.objects['Back_Light']
back.data.energy = 600
back.data.type = 'AREA'
"""
})
```

## Advanced Scene Creation

### Example 7: Architectural Elements

**User**: "Create a simple house with walls, a roof, and windows."

**Claude's Understanding and Actions**:
1. Creates multiple objects to form the structure
2. Positions them according to architectural understanding
3. Uses appropriate materials for different elements
4. Reports the structure creation with a breakdown of elements

### Example 8: Terrain Generation

**User**: "Can you create a simple mountain landscape?"

**Claude's Understanding and Actions**:
1. Creates a plane as the base terrain
2. Uses `execute_blender_code` to add displacement or sculpting
3. Applies appropriate textures and materials
4. Sets up environment lighting for landscape visualization

**Implementation via BlenderMCP**:
```python
# Create a plane for the terrain
terrain = blender.send_command("create_object", {
    "type": "PLANE",
    "name": "Terrain",
    "location": [0, 0, 0],
    "scale": [10, 10, 1]
})

# Use Python code to add subdivisions and displacement
blender.send_command("execute_code", {
    "code": """
import bpy
import random

# Get the terrain object
terrain = bpy.data.objects['Terrain']

# Add subdivision modifier
subsurf = terrain.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 5
subsurf.render_levels = 5

# Add displacement modifier
displace = terrain.modifiers.new(name="Displace", type='DISPLACE')

# Create a new texture for displacement
tex = bpy.data.textures.new('Mountain', type='CLOUDS')
tex.noise_scale = 1.5
displace.texture = tex
displace.strength = 2.0

# Apply modifiers
bpy.context.view_layer.objects.active = terrain
bpy.ops.object.modifier_apply(modifier="Subdivision")
bpy.ops.object.modifier_apply(modifier="Displace")

# Set material
if 'Terrain_Mat' not in bpy.data.materials:
    mat = bpy.data.materials.new(name="Terrain_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs[0].default_value = (0.08, 0.258, 0.12, 1.0)  # Green color
    terrain.data.materials.append(mat)
"""
})
```

## Animation and Rendering

### Example 9: Simple Animation

**User**: "Create a 30-frame animation of the cube rotating around the Y-axis."

**Claude's Understanding and Actions**:
1. Sets up keyframes for the cube's rotation
2. Configures animation settings
3. Reports back the animation setup and how to play it

**Implementation via BlenderMCP**:
```python
# Use execute_code to set up animation
blender.send_command("execute_code", {
    "code": """
import bpy
import math

# Get the cube
cube = bpy.data.objects.get('Cube')
if not cube:
    # Create a cube if it doesn't exist
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
    cube = bpy.context.active_object
    cube.name = 'Cube'

# Set animation length
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 30

# Set first keyframe at frame 1
scene.frame_set(1)
cube.rotation_euler = (0, 0, 0)
cube.keyframe_insert(data_path="rotation_euler")

# Set final keyframe at frame 30
scene.frame_set(30)
cube.rotation_euler = (0, 2*math.pi, 0)  # Full 360-degree rotation
cube.keyframe_insert(data_path="rotation_euler")
"""
})
```

### Example 10: Rendering and Output

**User**: "Render the scene with a resolution of 1920x1080 and save it to my desktop."

**Claude's Understanding and Actions**:
1. Uses `render_scene` tool with appropriate parameters
2. Sets resolution and output path
3. Initiates rendering process
4. Reports back when rendering is complete

## Debugging and Scene Analysis

### Example 11: Scene Inspection

**User**: "What objects are currently in my scene?"

**Claude's Understanding and Actions**:
1. Uses `get_scene_info` resource to fetch scene data
2. Analyzes the object list
3. Provides a formatted summary of all objects, their types, and positions

### Example 12: Troubleshooting

**User**: "Why can't I see the sphere in the render?"

**Claude's Understanding and Actions**:
1. Uses resources to check scene and object information
2. Checks visibility settings, materials, and camera position
3. Provides diagnostic information and suggested fixes

**Potential Fixes via BlenderMCP**:
```python
# Check sphere visibility and material
sphere_info = blender.send_command("get_object_info", {"name": "Sphere"})

# Make sure it's visible
if not sphere_info.get("visible", True):
    blender.send_command("modify_object", {
        "name": "Sphere",
        "visible": True
    })

# Check if it has a material, add one if missing
if not sphere_info.get("materials"):
    blender.send_command("set_material", {
        "object_name": "Sphere",
        "color": [0.2, 0.4, 0.8]
    })

# Check if it's in camera view
blender.send_command("execute_code", {
    "code": """
import bpy
# Select sphere
sphere = bpy.data.objects.get('Sphere')
if sphere:
    bpy.ops.object.select_all(action='DESELECT')
    sphere.select_set(True)
    # Frame selected in camera view
    bpy.ops.view3d.camera_to_view_selected()
"""
})
```

## Real-Time Collaboration

### Example 13: Iterative Design

**User**: "I don't like how the table looks. Make the legs thicker and the tabletop wider."

**Claude's Understanding and Actions**:
1. Identifies existing objects (tabletop and legs)
2. Modifies their properties based on the feedback
3. Shows before/after comparison and asks for further feedback

### Example 14: Guided Tutorial

**User**: "I'm new to Blender. Can you help me create a simple character?"

**Claude's Understanding and Actions**:
1. Breaks down the process into manageable steps
2. Creates basic shapes for the character parts
3. Guides through joining and posing
4. Provides educational context along with actions

These examples showcase how Claude can interact with Blender through natural language using the BlenderMCP integration, providing an intuitive way to create and modify 3D content without needing to know the details of Blender's interface or Python API.