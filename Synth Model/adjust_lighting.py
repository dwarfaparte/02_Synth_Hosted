"""
Blender Lighting Adjustment Script
Automatically adjusts scene lighting to be more natural and less harsh

Usage:
1. Open your Blender file (synthesizer.blend)
2. Go to the Scripting workspace
3. Open this script or paste it into the Text Editor
4. Click "Run Script" or press Alt+P
"""

import bpy
import math

def adjust_lighting():
    """Main function to adjust all lighting in the scene"""

    print("=" * 50)
    print("Starting Lighting Adjustment")
    print("=" * 50)

    # 1. Adjust existing lights
    adjust_existing_lights()

    # 2. Adjust world environment lighting
    adjust_world_lighting()

    # 3. Configure render settings for softer shadows
    configure_render_settings()

    # 4. Optionally add three-point lighting if scene has few lights
    setup_three_point_lighting()

    print("=" * 50)
    print("Lighting adjustment complete!")
    print("=" * 50)


def adjust_existing_lights():
    """Reduce intensity and increase softness of existing lights"""
    print("\n--- Adjusting Existing Lights ---")

    lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']

    if not lights:
        print("No lights found in scene")
        return

    for light_obj in lights:
        light = light_obj.data
        old_energy = light.energy

        # Reduce light intensity based on type
        if light.type == 'SUN':
            light.energy = min(light.energy, 2.0)  # Cap sun strength at 2.0
            if old_energy > 2.0:
                light.energy = 1.0
        elif light.type == 'POINT':
            light.energy = min(light.energy, 200)  # Cap point lights at 200W
            if old_energy > 500:
                light.energy = 100
        elif light.type == 'SPOT':
            light.energy = min(light.energy, 300)  # Cap spot lights
            if old_energy > 500:
                light.energy = 150
        elif light.type == 'AREA':
            light.energy = min(light.energy, 200)
            if old_energy > 500:
                light.energy = 100
            # Increase area light size for softer shadows
            if light.size < 2.0:
                light.size = 2.0

        # Enable soft shadows for spot lights
        if light.type == 'SPOT':
            light.shadow_soft_size = 0.25

        print(f"  {light_obj.name} ({light.type}): {old_energy:.1f} → {light.energy:.1f}")


def adjust_world_lighting():
    """Reduce environment/world lighting intensity"""
    print("\n--- Adjusting World Lighting ---")

    world = bpy.context.scene.world

    if world and world.use_nodes:
        nodes = world.node_tree.nodes

        # Find Background shader node
        for node in nodes:
            if node.type == 'BACKGROUND':
                old_strength = node.inputs['Strength'].default_value
                # Reduce strength to a more natural level
                new_strength = min(old_strength, 0.6)
                if old_strength > 1.5:
                    new_strength = 0.5
                node.inputs['Strength'].default_value = new_strength
                print(f"  World background strength: {old_strength:.2f} → {new_strength:.2f}")
    else:
        print("  World has no nodes or doesn't exist")


def configure_render_settings():
    """Configure render settings for softer, more natural lighting"""
    print("\n--- Configuring Render Settings ---")

    scene = bpy.context.scene

    # Eevee settings
    if scene.render.engine == 'BLENDER_EEVEE':
        eevee = scene.eevee
        eevee.use_soft_shadows = True
        eevee.shadow_cube_size = '2048'
        eevee.shadow_cascade_size = '2048'
        eevee.use_gtao = True  # Ambient occlusion
        eevee.gtao_distance = 0.2
        print("  Eevee: Enabled soft shadows and ambient occlusion")

    # Cycles settings
    elif scene.render.engine == 'CYCLES':
        cycles = scene.cycles
        cycles.use_adaptive_sampling = True
        print("  Cycles: Enabled adaptive sampling")


def setup_three_point_lighting():
    """Add three-point lighting setup if scene has very few lights"""
    print("\n--- Three-Point Lighting Setup ---")

    existing_lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']

    if len(existing_lights) >= 3:
        print("  Scene already has sufficient lights. Skipping three-point setup.")
        return

    # Get scene center (approximate)
    if bpy.context.selected_objects:
        center = sum((obj.location for obj in bpy.context.selected_objects),
                     bpy.mathutils.Vector()) / len(bpy.context.selected_objects)
    else:
        center = bpy.mathutils.Vector((0, 0, 0))

    distance = 5.0

    # Key Light (main light)
    if not any(obj.name.startswith("KeyLight") for obj in existing_lights):
        create_area_light("KeyLight",
                         location=(center.x + distance, center.y - distance, center.z + distance),
                         energy=100,
                         size=3.0)
        print("  Created Key Light")

    # Fill Light (softer, opposite side)
    if not any(obj.name.startswith("FillLight") for obj in existing_lights):
        create_area_light("FillLight",
                         location=(center.x - distance, center.y - distance/2, center.z + distance/2),
                         energy=40,
                         size=4.0)
        print("  Created Fill Light")

    # Rim Light (back light for edge definition)
    if not any(obj.name.startswith("RimLight") for obj in existing_lights):
        create_area_light("RimLight",
                         location=(center.x, center.y + distance, center.z + distance),
                         energy=30,
                         size=2.0)
        print("  Created Rim Light")


def create_area_light(name, location, energy, size):
    """Helper function to create an area light"""
    # Create light data
    light_data = bpy.data.lights.new(name=name, type='AREA')
    light_data.energy = energy
    light_data.size = size

    # Create light object
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location

    # Point light toward origin
    direction = bpy.mathutils.Vector((0, 0, 0)) - bpy.mathutils.Vector(location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    light_object.rotation_euler = rot_quat.to_euler()

    return light_object


# Run the adjustment
if __name__ == "__main__":
    adjust_lighting()
