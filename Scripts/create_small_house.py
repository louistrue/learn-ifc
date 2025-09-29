#!/usr/bin/env python3
"""
IFC Small House Creation Script
Creates a complete 2-storey small house with walls, windows, doors, and flat slabs using IFCOpenShell
"""

import ifcopenshell
import datetime
import math

def create_wall_with_proper_joins(model, world_placement, world_z, world_x, body_context,
                                start_x, start_y, end_x, end_y, wall_name, base_height, wall_height):
    """Create a wall with proper IFC structure and corner joins"""

    # Calculate wall dimensions
    wall_length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

    # Calculate wall placement and rotation
    wall_center_x = (start_x + end_x) / 2
    wall_center_y = (start_y + end_y) / 2

    # Calculate rotation angle
    if start_x == end_x:  # Vertical wall
        angle = math.pi/2 if end_y > start_y else -math.pi/2
    else:  # Horizontal wall
        angle = 0 if end_x > start_x else math.pi

    # Create wall placement (at base of wall, not center)
    wall_point = model.createIfcCartesianPoint((wall_center_x, wall_center_y, base_height))
    if angle != 0:
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        wall_x_dir = model.createIfcDirection((cos_angle, sin_angle, 0.0))
        wall_placement = model.createIfcAxis2Placement3D(wall_point, world_z, wall_x_dir)
    else:
        wall_placement = model.createIfcAxis2Placement3D(wall_point, world_z, world_x)

    wall_local_placement = model.createIfcLocalPlacement(world_placement, wall_placement)

    # Create wall geometry with proper profile placement
    profile_origin = model.createIfcCartesianPoint((0.0, 0.0))
    profile_placement = model.createIfcAxis2Placement2D(profile_origin)
    wall_profile = model.createIfcRectangleProfileDef("AREA", None, profile_placement, wall_length, 0.2)

    extrude_dir = model.createIfcDirection((0.0, 0.0, 1.0))
    wall_solid = model.createIfcExtrudedAreaSolid(wall_profile, profile_placement, extrude_dir, wall_height)
    wall_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [wall_solid])
    wall_definition = model.createIfcProductDefinitionShape(None, None, [wall_shape])

    # Create wall entity with proper PredefinedType (following test_ifc_window.py pattern)
    wall = model.createIfcWall(
        ifcopenshell.guid.new(),
        None,
        wall_name,
        None,
        None,
        wall_local_placement,
        wall_definition,
        None,
        "STANDARD"  # PredefinedType for academic compliance
    )

    return wall

def create_slab(model, world_placement, body_context, length, width, base_z, thickness, slab_name):
    """Create a flat slab with proper IFC structure"""

    # Create slab placement at center
    slab_center_x = length / 2
    slab_center_y = width / 2
    slab_center_z = base_z

    slab_point = model.createIfcCartesianPoint((slab_center_x, slab_center_y, slab_center_z))
    slab_placement = model.createIfcLocalPlacement(world_placement, model.createIfcAxis2Placement3D(slab_point))

    # Create slab geometry
    profile_origin = model.createIfcCartesianPoint((0.0, 0.0))
    profile_placement = model.createIfcAxis2Placement2D(profile_origin)
    slab_profile = model.createIfcRectangleProfileDef("AREA", None, profile_placement, length, width)

    extrude_dir = model.createIfcDirection((0.0, 0.0, 1.0))
    slab_solid = model.createIfcExtrudedAreaSolid(slab_profile, profile_placement, extrude_dir, thickness)
    slab_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [slab_solid])
    slab_definition = model.createIfcProductDefinitionShape(None, None, [slab_shape])

    # Create slab entity with proper PredefinedType
    slab = model.createIfcSlab(
        ifcopenshell.guid.new(),
        None,
        slab_name,
        None,
        None,
        slab_placement,
        slab_definition,
        None,
        "FLOOR"  # PredefinedType for floor slabs
    )

    # Add slab styling (light gray concrete)
    if "Roof" in slab_name:
        slab_color = model.createIfcColourRgb(None, 0.7, 0.7, 0.7)  # Light gray for roof
    else:
        slab_color = model.createIfcColourRgb(None, 0.8, 0.8, 0.8)  # Slightly darker for floors

    surface_style = model.createIfcSurfaceStyleRendering(slab_color, 0.0, slab_color, None, None, None, None, None, "FLAT")
    surface_styles = model.createIfcSurfaceStyle("SlabStyle", "BOTH", [surface_style])
    styled_item = model.createIfcStyledItem(slab_solid, [surface_styles], "SlabStyle")

    return slab

def create_small_house():
    """Create a complete 2-storey small house IFC model"""

    print("🏠 Creating 2-storey small house IFC model...")

    # Create empty IFC model
    model = ifcopenshell.file()
    print("✅ Empty IFC model created")

    # Create project
    project = model.createIfcProject(ifcopenshell.guid.new(), None, "Small House Project", None, None, None, None, None, None)
    print("✅ Project created")

    # Create units
    length_unit = model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
    area_unit = model.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
    volume_unit = model.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE")
    unit_assignment = model.createIfcUnitAssignment([length_unit, area_unit, volume_unit])
    print("✅ Units created")

    # Create geometric contexts
    world_origin = model.createIfcCartesianPoint((0.0, 0.0, 0.0))
    world_z = model.createIfcDirection((0.0, 0.0, 1.0))
    world_x = model.createIfcDirection((1.0, 0.0, 0.0))
    world_placement = model.createIfcAxis2Placement3D(world_origin, world_z, world_x)

    geom_context = model.createIfcGeometricRepresentationContext(
        None, "Model", 3, 1e-05, world_placement, world_z
    )
    body_context = model.createIfcGeometricRepresentationSubContext(
        "Body", "Model", None, None, None, None, geom_context, None, "MODEL_VIEW", None
    )
    print("✅ Geometric contexts created")

    # Create hierarchy: Project > Site > Building > Storeys
    site = model.createIfcSite(ifcopenshell.guid.new(), None, "House Site", None, None, world_placement, None, None, None, None, None, None, None)
    building = model.createIfcBuilding(ifcopenshell.guid.new(), None, "Small House", None, None, world_placement, None, None, None, None, None, None)

    # Create two storeys
    ground_storey = model.createIfcBuildingStorey(ifcopenshell.guid.new(), None, "Ground Floor", None, None, world_placement, None, None, None, 0.0)
    first_storey = model.createIfcBuildingStorey(ifcopenshell.guid.new(), None, "First Floor", None, None, world_placement, None, None, None, 3.0)

    # Create relationships
    model.createIfcRelAggregates(ifcopenshell.guid.new(), None, None, None, project, [site])
    model.createIfcRelAggregates(ifcopenshell.guid.new(), None, None, None, site, [building])
    model.createIfcRelAggregates(ifcopenshell.guid.new(), None, None, None, building, [ground_storey, first_storey])
    print("✅ Hierarchy created (Project > Site > Building > Storeys)")

    # House dimensions (in meters)
    house_length = 8.0  # 8m long
    house_width = 6.0   # 6m wide
    wall_height = 3.0   # 3m high per storey
    wall_thickness = 0.2  # 200mm thick
    slab_thickness = 0.2  # 200mm thick slabs

    # Create walls for both storeys
    walls = []
    wall_configs = [
        # [start_x, start_y, end_x, end_y, name]
        [0, 0, house_length, 0, "Front Wall"],      # Front wall
        [house_length, 0, house_length, house_width, "Right Wall"],  # Right wall
        [house_length, house_width, 0, house_width, "Back Wall"],    # Back wall
        [0, house_width, 0, 0, "Left Wall"]         # Left wall
    ]

    # Create walls for ground floor
    ground_walls = []
    for i, (start_x, start_y, end_x, end_y, wall_name) in enumerate(wall_configs):
        wall = create_wall_with_proper_joins(model, world_placement, world_z, world_x, body_context,
                                           start_x, start_y, end_x, end_y, wall_name, 0.0, wall_height)
        ground_walls.append(wall)
        walls.append(wall)

        # Assign wall to ground storey
        model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, None, None, [wall], ground_storey)

    # Create walls for first floor
    first_walls = []
    for i, (start_x, start_y, end_x, end_y, wall_name) in enumerate(wall_configs):
        wall = create_wall_with_proper_joins(model, world_placement, world_z, world_x, body_context,
                                           start_x, start_y, end_x, end_y, f"{wall_name} - First Floor", wall_height, wall_height)
        first_walls.append(wall)
        walls.append(wall)

        # Assign wall to first storey
        model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, None, None, [wall], first_storey)

    print(f"✅ Created {len(walls)} walls (4 ground + 4 first floor)")

    # Create window type with proper properties (following test_ifc_window.py pattern)
    window_type = model.createIfcWindowType(
        ifcopenshell.guid.new(),
        None,
        "Standard Window Type",
        "Standard single-hung window",
        None,   # ApplicableOccurrence
        None,   # HasPropertySets (set after creating props)
        None,   # RepresentationMaps
        None,   # Tag
        "Standard Window Type",  # ElementType
        "WINDOW",  # PredefinedType
        "SINGLE_PANEL",  # PartitioningType
        True,    # ParameterTakesPrecedence
        None     # UserDefinedPartitioningType
    )

    # Create window lining properties (frame characteristics)
    lining_props = model.createIfcWindowLiningProperties(
        ifcopenshell.guid.new(),
        None,
        "Window Lining Properties",
        None,
        0.05,   # LiningDepth - 50mm frame depth
        0.025,  # LiningThickness - 25mm frame thickness
        0.01,   # TransomThickness - 10mm transom
        0.01,   # MullionThickness - 10mm mullion
        None,   # FirstTransomOffset
        None,   # SecondTransomOffset
        None,   # FirstMullionOffset
        None,   # SecondMullionOffset
        None,   # ShapeAspectStyle
        0.075,  # LiningOffset - 75mm from wall center
        0.01,   # LiningToPanelOffsetX
        0.01    # LiningToPanelOffsetY
    )

    # Create window panel properties (operational characteristics)
    panel_props = model.createIfcWindowPanelProperties(
        ifcopenshell.guid.new(),
        None,
        "Window Panel Properties",
        None,
        "SIDEHUNGRIGHTHAND",  # OperationType
        "RIGHT",              # PanelPosition
        1.5,                  # FrameDepth (window width)
        1.2,                  # FrameThickness (window height)
        None                  # ShapeAspectStyle
    )

    # Attach property sets to window type
    window_type.HasPropertySets = [lining_props, panel_props]
    print("✅ Created window type with properties")

    # Create door type with properties
    door_type = model.createIfcDoorType(
        ifcopenshell.guid.new(),
        None,
        "Standard Door Type",
        "Standard hinged door",
        None,   # ApplicableOccurrence
        None,   # HasPropertySets
        None,   # RepresentationMaps
        None,   # Tag
        "Standard Door Type",  # ElementType
        "DOOR", # PredefinedType
        "SINGLE_SWING_RIGHT",  # OperationType
        True,   # ParameterTakesPrecedence
        None    # UserDefinedOperationType
    )
    print("✅ Created door type with properties")

    # Add windows to front and back walls on both storeys
    window_configs = [
        # [storey, wall_index, offset_from_start, window_name]
        [0, 0, 2.0, "Ground Front Window 1"],  # Ground front wall, 2m from left
        [0, 0, 6.0, "Ground Front Window 2"],  # Ground front wall, 6m from left
        [0, 2, 3.0, "Ground Back Window"],     # Ground back wall, 3m from left
        [1, 0, 2.0, "First Front Window 1"],   # First front wall, 2m from left
        [1, 0, 6.0, "First Front Window 2"],   # First front wall, 6m from left
        [1, 2, 3.0, "First Back Window"],      # First back wall, 3m from left
    ]

    # Get all walls organized by storey
    all_walls = [ground_walls, first_walls]

    for storey_idx, wall_idx, offset, window_name in window_configs:
        wall = all_walls[storey_idx][wall_idx]
        storey = ground_storey if storey_idx == 0 else first_storey
        base_z = 0.0 if storey_idx == 0 else wall_height

        # Window parameters - adjusted depth to stick out but not inside
        window_width = 1.5
        window_height = 1.2
        window_depth = 0.25  # 250mm thick window (thicker than 200mm wall)
        window_sill_height = base_z + 1.0

        # Calculate window position relative to wall center
        wall_config = wall_configs[wall_idx]
        start_x, start_y, end_x, end_y = wall_config[0:4]
        wall_length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

        # Position along wall (offset from wall start)
        t = offset / wall_length
        window_x = start_x + t * (end_x - start_x)
        window_y = start_y + t * (end_y - start_y)

        # Adjust for wall thickness (center window on wall, sticking out)
        if start_x == end_x:  # Vertical wall
            offset_x = wall_thickness/2 if wall_idx == 1 else -wall_thickness/2  # Right or left wall
            offset_y = 0
        else:  # Horizontal wall
            offset_x = 0
            offset_y = 0  # Center window on wall thickness

        window_point = model.createIfcCartesianPoint((window_x + offset_x, window_y + offset_y, window_sill_height))
        window_placement = model.createIfcLocalPlacement(world_placement, model.createIfcAxis2Placement3D(window_point))

        # Create window geometry
        profile_origin = model.createIfcCartesianPoint((0.0, 0.0))
        profile_placement = model.createIfcAxis2Placement2D(profile_origin)
        window_profile = model.createIfcRectangleProfileDef("AREA", "WindowProfile", profile_placement, window_width, window_depth)
        window_solid = model.createIfcExtrudedAreaSolid(window_profile, profile_placement, model.createIfcDirection((0.0, 0.0, 1.0)), window_height)
        window_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [window_solid])
        window_definition = model.createIfcProductDefinitionShape(None, None, [window_shape])

        # Create window entity with proper PredefinedType (following test_ifc_window.py pattern)
        window = model.createIfcWindow(
            ifcopenshell.guid.new(),
            None,
            window_name,
            None,
            None,
            window_placement,
            window_definition,
            None,
            window_height,  # OverallHeight
            window_width,   # OverallWidth
            "WINDOW",       # PredefinedType
            None,           # PartitioningType
            None            # UserDefinedPartitioningType
        )

        # Add window styling (semi-transparent blue)
        window_color = model.createIfcColourRgb(None, 0.7, 0.9, 1.0)
        surface_style = model.createIfcSurfaceStyleRendering(window_color, 0.4, window_color, None, None, None, None, None, "FLAT")
        surface_styles = model.createIfcSurfaceStyle("WindowStyle", "BOTH", [surface_style])
        styled_item = model.createIfcStyledItem(window_solid, [surface_styles], "WindowStyle")

        # Create window opening
        opening_width = window_width + 0.02
        opening_depth = wall_thickness + 0.05  # Larger than wall thickness
        opening_profile = model.createIfcRectangleProfileDef("AREA", "OpeningProfile", profile_placement, opening_width, opening_depth)
        opening_solid = model.createIfcExtrudedAreaSolid(opening_profile, profile_placement, model.createIfcDirection((0.0, 0.0, 1.0)), window_height + 0.01)
        opening_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [opening_solid])
        opening_definition = model.createIfcProductDefinitionShape(None, None, [opening_shape])
        opening = model.createIfcOpeningElement(ifcopenshell.guid.new(), None, f"{window_name} Opening", None, None, window_placement, opening_definition, None, "OPENING")

        # Create void relationship
        model.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, "Window Opening", None, wall, opening)

        # Create fill relationship (following test_ifc_window.py pattern)
        model.createIfcRelFillsElement(ifcopenshell.guid.new(), None, "Window Fills Opening", None, opening, window)

        # Create type relationship (academic requirement)
        model.createIfcRelDefinesByType(
            ifcopenshell.guid.new(),
            None,
            "Window Type Assignment",
            None,
            [window],  # RelatedObjects (window instances)
            window_type  # RelatingType (the IfcWindowType)
        )

        # Assign window to storey
        model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, "Contains Windows", None, [window], storey)

    print("✅ Added windows with openings to both storeys")

    # Add door to ground floor right wall (side wall)
    door_offset = 2.0  # 2m from front end of right wall
    door_width = 0.9
    door_height = 2.1
    door_depth = 0.25  # Same depth as windows for consistency

    # Calculate door position on right wall (wall index 1) with proper rotation
    right_wall_config = wall_configs[1]  # Right wall: [house_length, 0, house_length, house_width]
    door_x = house_length  # Center of right wall thickness
    door_y = door_offset  # 2m from front corner
    door_point = model.createIfcCartesianPoint((door_x, door_y, 0.0))
    
    # Rotate door 90 degrees to face outward from right wall
    door_y_dir = model.createIfcDirection((0.0, 1.0, 0.0))  # Door faces in Y direction
    door_axis = model.createIfcAxis2Placement3D(door_point, world_z, door_y_dir)
    door_placement = model.createIfcLocalPlacement(world_placement, door_axis)

    # Create door geometry
    profile_origin = model.createIfcCartesianPoint((0.0, 0.0))
    profile_placement = model.createIfcAxis2Placement2D(profile_origin)
    door_profile = model.createIfcRectangleProfileDef("AREA", "DoorProfile", profile_placement, door_width, door_depth)
    door_solid = model.createIfcExtrudedAreaSolid(door_profile, profile_placement, model.createIfcDirection((0.0, 0.0, 1.0)), door_height)
    door_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [door_solid])
    door_definition = model.createIfcProductDefinitionShape(None, None, [door_shape])

    # Create door entity with proper PredefinedType
    door = model.createIfcDoor(
        ifcopenshell.guid.new(),
        None,
        "Front Door",
        None,
        None,
        door_placement,
        door_definition,
        None,
        door_height,     # OverallHeight
        door_width,      # OverallWidth
        "DOOR",          # PredefinedType
        None,            # OperationType
        None             # UserDefinedOperationType
    )

    # Add door styling (brown wood)
    door_color = model.createIfcColourRgb(None, 0.6, 0.4, 0.2)
    door_surface_style = model.createIfcSurfaceStyleRendering(door_color, 0.0, door_color, None, None, None, None, None, "FLAT")
    door_surface_styles = model.createIfcSurfaceStyle("DoorStyle", "BOTH", [door_surface_style])
    door_styled_item = model.createIfcStyledItem(door_solid, [door_surface_styles], "DoorStyle")

    # Create door opening
    door_opening_width = door_width + 0.02
    door_opening_depth = wall_thickness + 0.05
    door_opening_profile = model.createIfcRectangleProfileDef("AREA", "DoorOpeningProfile", profile_placement, door_opening_width, door_opening_depth)
    door_opening_solid = model.createIfcExtrudedAreaSolid(door_opening_profile, profile_placement, model.createIfcDirection((0.0, 0.0, 1.0)), door_height + 0.01)
    door_opening_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [door_opening_solid])
    door_opening_definition = model.createIfcProductDefinitionShape(None, None, [door_opening_shape])
    door_opening = model.createIfcOpeningElement(ifcopenshell.guid.new(), None, "Door Opening", None, None, door_placement, door_opening_definition, None, "OPENING")

    # Create void relationship for door
    model.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, "Door Opening", None, ground_walls[1], door_opening)  # Ground right wall

    # Create fill relationship for door
    model.createIfcRelFillsElement(ifcopenshell.guid.new(), None, "Door Fills Opening", None, door_opening, door)

    # Create type relationship for door
    model.createIfcRelDefinesByType(
        ifcopenshell.guid.new(),
        None,
        "Door Type Assignment",
        None,
        [door],  # RelatedObjects (door instances)
        door_type  # RelatingType (the IfcDoorType)
    )

    # Assign door to ground storey
    model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, "Contains Door", None, [door], ground_storey)

    print("✅ Added door with opening to ground floor")

    # Create flat slabs for both storeys
    slabs = []

    # Ground floor slab (floor) - at ground level
    ground_slab_z = 0.0
    ground_slab = create_slab(model, world_placement, body_context, house_length, house_width, ground_slab_z, slab_thickness, "Ground Floor Slab")
    slabs.append(ground_slab)
    model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, "Contains Floor Slab", None, [ground_slab], ground_storey)

    # First floor slab (floor and ceiling) - at top of ground floor walls
    first_slab_z = wall_height
    first_slab = create_slab(model, world_placement, body_context, house_length, house_width, first_slab_z, slab_thickness, "First Floor Slab")
    slabs.append(first_slab)
    model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, "Contains Floor Slab", None, [first_slab], first_storey)

    # Roof slab (flat roof) - at top of first floor walls
    roof_slab_z = 2 * wall_height
    roof_slab = create_slab(model, world_placement, body_context, house_length, house_width, roof_slab_z, slab_thickness, "Roof Slab")
    slabs.append(roof_slab)
    model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), None, "Contains Roof Slab", None, [roof_slab], first_storey)

    print("✅ Added flat slabs for both storeys and roof")

    # Add wall materials
    concrete_material = model.createIfcMaterial("Concrete")
    for wall in walls:
        material_layer = model.createIfcMaterialLayer(concrete_material, 200, None)
        material_layer_set = model.createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = model.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", -100)
        model.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(), None, "Wall Material", None, [wall], material_layer_set_usage)

    # Add slab materials
    for slab in slabs:
        material_layer = model.createIfcMaterialLayer(concrete_material, 200, None)
        material_layer_set = model.createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = model.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS3", "POSITIVE", -100)
        model.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(), None, "Slab Material", None, [slab], material_layer_set_usage)

    print("✅ Added materials to walls and slabs")

    return model

def main():
    """Main function to create and save small house IFC file"""
    try:
        # Create the house model
        model = create_small_house()

        # Save the file
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/louistrue/Development/learn-ifc/small_house_{current_time}.ifc"
        model.write(filename)

        print(f"\n✅ Small house IFC file saved successfully!")
        print(f"📁 File: {filename}")

        # Validate the file
        print("\n🔍 Validating IFC file...")
        test_model = ifcopenshell.open(filename)
        
        # Count elements
        walls = test_model.by_type("IfcWall")
        windows = test_model.by_type("IfcWindow")
        doors = test_model.by_type("IfcDoor")
        slabs = test_model.by_type("IfcSlab")
        openings = test_model.by_type("IfcOpeningElement")
        styled_items = test_model.by_type("IfcStyledItem")
        storeys = test_model.by_type("IfcBuildingStorey")
        window_types = test_model.by_type("IfcWindowType")
        door_types = test_model.by_type("IfcDoorType")
        lining_props = test_model.by_type("IfcWindowLiningProperties")
        panel_props = test_model.by_type("IfcWindowPanelProperties")
        type_rels = test_model.by_type("IfcRelDefinesByType")

        print(f"🏢 Found {len(storeys)} storeys")
        print(f"🧱 Found {len(walls)} walls")
        print(f"🪟 Found {len(windows)} windows")
        print(f"🚪 Found {len(doors)} doors")
        print(f"🏗️  Found {len(slabs)} slabs")
        print(f"🔲 Found {len(openings)} openings")
        print(f"🎨 Found {len(styled_items)} styled items")
        print(f"🏷️  Found {len(window_types)} window types")
        print(f"🚪 Found {len(door_types)} door types")
        print(f"🖼️  Found {len(lining_props)} lining properties")
        print(f"📋 Found {len(panel_props)} panel properties")
        print(f"🔗 Found {len(type_rels)} type relationships")

        # House specifications
        print(f"\n🏠 2-Storey Small House Specifications:")
        print(f"   📐 Dimensions: 8.0m × 6.0m × 6.0m (2 storeys × 3.0m each)")
        print(f"   🧱 Wall thickness: 200mm")
        print(f"   🪟 Windows: 6 (3 per storey, 1.5m × 1.2m × 0.25m depth, semi-transparent blue)")
        print(f"   🚪 Door: 1 (0.9m × 2.1m × 0.25m depth, brown wood on right wall)")
        print(f"   🏗️  Slabs: 3 (ground floor, first floor, flat roof)")
        print(f"   🏢 Storeys: Ground Floor (0.0m) + First Floor (3.0m)")
        print(f"   🏷️  Types: Proper window and door types with properties")

        print(f"\n🎉 2-storey small house creation completed successfully!")
        
        return filename

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
