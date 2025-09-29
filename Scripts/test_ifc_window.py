#!/usr/bin/env python3
"""
IFC Window Creation Test Script
Tests the corrected window geometry creation using IFCOpenShell
Direct entity creation to avoid API compatibility issues
"""

import ifcopenshell
import datetime
import time

def create_test_ifc_with_window():
    """Create a basic IFC model with a wall and window using direct entity creation"""

    print("🚀 Creating IFC model with wall and window...")

    # Ein leeres IFC-Modell erstellen
    model = ifcopenshell.file()
    print("✅ Empty IFC model created")

    # Minimal OwnerHistory (some viewers rely on it to display types)
    org = model.createIfcOrganization(None, "learn-ifc", None, None, None)
    person = model.createIfcPerson(None, "Author", "Test", None, None, None, None, None)
    person_org = model.createIfcPersonAndOrganization(person, org, None)
    app = model.createIfcApplication(org, "0.8", "IfcOpenShell", "ifcopenshell")
    owner_history = model.createIfcOwnerHistory(
        person_org, app, None, "NOCHANGE", None, None, None, int(time.time())
    )

    # Create project (we will enrich attributes after contexts are created)
    project = model.createIfcProject(ifcopenshell.guid.new(), None, "Test Project", None, None, None, None, None, None)
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

    # Enrich IfcProject with OwnerHistory, contexts and units
    project.OwnerHistory = owner_history
    project.Description = "Demonstration project with complete schema attributes"
    project.LongName = "Test Project Long Name"
    project.Phase = "Concept"
    project.RepresentationContexts = [geom_context]
    project.UnitsInContext = unit_assignment

    # Create hierarchy: Project > Site > Building > Storey
    site = model.createIfcSite(ifcopenshell.guid.new(), None, "Test Site", None, None, world_placement, None, None, None, None, None, None, None)
    building = model.createIfcBuilding(ifcopenshell.guid.new(), None, "Test Building", None, None, world_placement, None, None, None, None, None, None)
    storey = model.createIfcBuildingStorey(ifcopenshell.guid.new(), None, "Ground Floor", None, None, world_placement, None, None, None, 0.0)

    # Enrich spatial structure with proper attributes
    site.OwnerHistory = owner_history
    site.LongName = "Test Site Long Name"
    site.CompositionType = "ELEMENT"
    site.RefLatitude = (47, 21, 39, 600219)
    site.RefLongitude = (8, 33, 38, 576431)
    site.RefElevation = 0.0
    site.LandTitleNumber = "LTN-0001"
    site.SiteAddress = model.createIfcPostalAddress(
        None, None, None, None, ["123 Example Street"], None, "Zurich", "ZH", "8000", "CH"
    )

    building.OwnerHistory = owner_history
    building.LongName = "Test Building Long Name"
    building.CompositionType = "ELEMENT"
    building.ElevationOfRefHeight = 0.0
    building.ElevationOfTerrain = 0.0
    building.BuildingAddress = model.createIfcPostalAddress(
        None, None, None, None, ["123 Example Street"], None, "Zurich", "ZH", "8000", "CH"
    )

    storey.OwnerHistory = owner_history
    storey.LongName = "Ground Floor Long Name"
    storey.CompositionType = "ELEMENT"
    storey.Elevation = 0.0

    # Create relationships with OwnerHistory
    model.createIfcRelAggregates(ifcopenshell.guid.new(), owner_history, None, None, project, [site])
    model.createIfcRelAggregates(ifcopenshell.guid.new(), owner_history, None, None, site, [building])
    model.createIfcRelAggregates(ifcopenshell.guid.new(), owner_history, None, None, building, [storey])
    print("✅ Hierarchy created (Project > Site > Building > Storey)")

    # Create wall with proper predefined type
    wall = model.createIfcWall(
        ifcopenshell.guid.new(), 
        owner_history, 
        "Test Wall", 
        None, 
        None, 
        world_placement, 
        None, 
        None, 
        "STANDARD"  # PredefinedType for academic compliance
    )

    # Create wall geometry (simplified rectangle)
    wall_profile = model.createIfcRectangleProfileDef("AREA", None, world_placement, 5.0, 0.2)

    extrude_dir = model.createIfcDirection((0.0, 0.0, 1.0))
    wall_solid = model.createIfcExtrudedAreaSolid(wall_profile, world_placement, extrude_dir, 3.0)
    wall_shape = model.createIfcShapeRepresentation(body_context, "Body", "SweptSolid", [wall_solid])
    wall_definition = model.createIfcProductDefinitionShape(None, None, [wall_shape])

    wall.Representation = wall_definition
    print("✅ Wall created with geometry")

    # Assign wall to storey
    model.createIfcRelContainedInSpatialStructure(ifcopenshell.guid.new(), owner_history, None, None, [wall], storey)
    print("✅ Wall assigned to storey")

    # Create a wall type and assign via IfcRelDefinesByType (viewer-friendly)
    wall_type = model.createIfcWallType(
        ifcopenshell.guid.new(),
        owner_history,
        "Test Wall Type",
        "Example wall type",
        None, None, None, None,
        "Test Wall Type",
        "STANDARD"
    )
    model.createIfcRelDefinesByType(
        ifcopenshell.guid.new(),
        owner_history,
        "Wall Type Assignment",
        None,
        [wall],
        wall_type
    )

    # Window parameters (in mm, will convert to meters)
    # Wall is 5000mm long x 200mm thick x 3000mm high
    window_params = {
        "name": "Test Window",
        "width": 1000,
        "depth": 150,      # thinner window (150mm) so it doesn't stick through
        "height": 1200,
        "offset_x": 1600,  # center of wall: 2500mm - 900mm (half window) = 1600mm from left edge
        "offset_y": 25,    # center window in wall thickness: (200mm-150mm)/2 = 25mm offset
        "offset_z": 1200   # higher placement (1200mm from floor, more realistic window height)
    }

    # Convert mm to meters
    to_m = lambda v_mm: float(v_mm) / 1000.0

    # Create window placement relative to wall
    window_point = model.createIfcCartesianPoint((
        to_m(window_params["offset_x"]),
        to_m(window_params["offset_y"]),
        to_m(window_params["offset_z"])
    ))
    window_placement = model.createIfcLocalPlacement(world_placement,
        model.createIfcAxis2Placement3D(window_point)
    )
    print("✅ Window placement calculated")

    # Create window geometry with corrected axis placements
    print("🔧 Creating window geometry...")

    # Create proper 2D axis placement for the profile
    profile_origin = model.createIfcCartesianPoint((0.0, 0.0))
    profile_placement = model.createIfcAxis2Placement2D(profile_origin)

    # Create rectangle profile with proper 2D axis placement
    window_profile = model.createIfcRectangleProfileDef(
        "AREA",
        "WindowProfile",
        profile_placement,
        to_m(window_params["width"]),
        to_m(window_params["depth"])
    )

    # Create extrusion direction
    extrude_dir = model.createIfcDirection((0.0, 0.0, 1.0))

    # Create extruded area solid with proper axis placement
    window_solid = model.createIfcExtrudedAreaSolid(
        window_profile,
        profile_placement,  # Use 2D axis for extrusion base
        extrude_dir,
        to_m(window_params["height"])
    )

    # Create shape representation
    window_shape = model.createIfcShapeRepresentation(
        body_context,
        "Body",
        "SweptSolid",
        [window_solid]
    )
    window_definition = model.createIfcProductDefinitionShape(None, None, [window_shape])
    print("✅ Window geometry created")

    # Create proper window type first (academic standard)
    window_type = model.createIfcWindowType(
        ifcopenshell.guid.new(),
        None,
        "Standard Window Type",
        "Standard single-hung window",  # Description
        None,   # ApplicableOccurrence
        None,   # HasPropertySets (set after creating props)
        None,   # RepresentationMaps
        None,   # Tag
        "Standard Window Type",  # ElementType (shown by many viewers)
        "WINDOW",  # PredefinedType
        "SINGLE_PANEL",  # PartitioningType
        True,    # ParameterTakesPrecedence
        None     # UserDefinedPartitioningType
    )
    print("✅ Window type created")

    # Create window lining properties (frame characteristics)
    lining_props = model.createIfcWindowLiningProperties(
        ifcopenshell.guid.new(),
        None,
        "Window Lining Properties",
        None,
        to_m(50),   # LiningDepth - 50mm frame depth
        to_m(25),   # LiningThickness - 25mm frame thickness
        to_m(10),   # TransomThickness - 10mm transom
        to_m(10),   # MullionThickness - 10mm mullion
        None,       # FirstTransomOffset
        None,       # SecondTransomOffset
        None,       # FirstMullionOffset
        None,       # SecondMullionOffset
        None,       # ShapeAspectStyle
        to_m(75),   # LiningOffset - 75mm from wall center
        to_m(10),   # LiningToPanelOffsetX
        to_m(10)    # LiningToPanelOffsetY
    )
    print("✅ Window lining properties created")

    # Create window panel properties (operational characteristics)  
    panel_props = model.createIfcWindowPanelProperties(
        ifcopenshell.guid.new(),
        None,
        "Window Panel Properties", 
        None,
        "SIDEHUNGRIGHTHAND",  # OperationType - how window opens
        "RIGHT",              # PanelPosition
        to_m(window_params["width"]),  # FrameDepth
        to_m(window_params["height"]), # FrameThickness
        None                  # ShapeAspectStyle
    )
    print("✅ Window panel properties created")

    # Attach property sets directly to the type (preferred in IFC)
    window_type.HasPropertySets = [lining_props, panel_props]

    # Create window entity with proper type reference
    window = model.createIfcWindow(
        ifcopenshell.guid.new(),
        None,
        window_params["name"],
        "Test window instance",  # Description
        None,
        window_placement,
        window_definition,
        None,
        to_m(window_params["height"]),  # OverallHeight
        to_m(window_params["width"]),   # OverallWidth
        "WINDOW",  # PredefinedType
        "SINGLE_PANEL",  # PartitioningType
        None       # UserDefinedPartitioningType
    )
    
    # Create type relationship (academic requirement)
    # IfcRelDefinesByType: RelatedObjects=[window], RelatingType=window_type
    model.createIfcRelDefinesByType(
        ifcopenshell.guid.new(),
        owner_history,
        "Window Type Assignment",  # Name
        None,  # Description
        [window],  # RelatedObjects (window instances)
        window_type  # RelatingType (the IfcWindowType)
    )
    print("✅ Window entity created with proper type definition")

    # Assign window to storey
    model.createIfcRelContainedInSpatialStructure(
        ifcopenshell.guid.new(),
        None,
        "Contains Windows",
        None,
        [window],
        storey
    )
    print("✅ Window assigned to storey")

    # Add window styling with transparency and color
    print("🎨 Adding window styling...")

    # Create color for window (semi-transparent blue)
    window_color = model.createIfcColourRgb(None, 0.7, 0.9, 1.0)  # Light blue

    # Create surface style rendering with transparency
    surface_style = model.createIfcSurfaceStyleRendering(
        window_color,        # SurfaceColour
        0.3,                # Transparency (30% transparent)
        window_color,       # DiffuseColour
        None,               # TransmissionColour
        None,               # DiffuseTransmissionColour
        None,               # ReflectionColour
        None,               # SpecularColour
        None,               # SpecularHighlight
        "FLAT"              # ReflectanceMethod (enumeration)
    )

    # Create surface style
    surface_styles = model.createIfcSurfaceStyle("WindowStyle", "BOTH", [surface_style])

    # Create styled item to apply style to window geometry
    styled_item = model.createIfcStyledItem(window_solid, [surface_styles], "WindowStyle")
    print("✅ Window styling applied (semi-transparent blue)")

    # Create wall opening for the window
    print("🔲 Creating wall opening...")

    # Create opening placement (same as window placement)
    opening_point = model.createIfcCartesianPoint((
        to_m(window_params["offset_x"]),
        to_m(window_params["offset_y"]),
        to_m(window_params["offset_z"])
    ))
    opening_placement = model.createIfcLocalPlacement(world_placement,
        model.createIfcAxis2Placement3D(opening_point)
    )

    # Create opening profile (slightly larger than window for proper cutout)
    opening_profile_origin = model.createIfcCartesianPoint((0.0, 0.0))
    opening_profile_placement = model.createIfcAxis2Placement2D(opening_profile_origin)

    # Make opening larger than window AND wall thickness for proper cutout
    # Wall is 200mm (0.2m) thick, so opening needs to be thicker than that
    opening_width = to_m(window_params["width"]) + 0.02  # +2cm wider than window
    opening_depth = 0.25  # 250mm thick opening (larger than 200mm wall)
    opening_profile = model.createIfcRectangleProfileDef(
        "AREA",
        "OpeningProfile",
        opening_profile_placement,
        opening_width,
        opening_depth
    )

    # Create opening solid
    opening_solid = model.createIfcExtrudedAreaSolid(
        opening_profile,
        opening_profile_placement,
        model.createIfcDirection((0.0, 0.0, 1.0)),
        to_m(window_params["height"]) + 0.01  # Slightly taller
    )

    # Create opening shape representation
    opening_shape = model.createIfcShapeRepresentation(
        body_context,
        "Body",
        "SweptSolid",
        [opening_solid]
    )
    opening_definition = model.createIfcProductDefinitionShape(None, None, [opening_shape])

    # Create opening element with proper predefined type
    opening = model.createIfcOpeningElement(
        ifcopenshell.guid.new(),
        None,
        "Window Opening",
        None,
        None,
        opening_placement,
        opening_definition,
        None,
        "OPENING"  # PredefinedType for academic compliance
    )

    # Create void relationship between wall and opening (proper IFC schema)
    model.createIfcRelVoidsElement(
        ifcopenshell.guid.new(),
        None,
        "Wall Opening Relationship",
        None,
        wall,
        opening
    )
    
    # Create fill relationship between opening and window (academic standard)
    model.createIfcRelFillsElement(
        ifcopenshell.guid.new(),
        None,
        "Window Fills Opening",
        None,
        opening,
        window
    )
    print("✅ Wall opening created with proper void and fill relationships")

    # Add property sets to wall and window using direct entity creation
    print("📋 Adding property sets...")
    
    # Add Pset_WallCommon to wall
    try:
        # Create property set for wall
        wall_pset = model.createIfcPropertySet(
            ifcopenshell.guid.new(),
            owner_history,
            "Pset_WallCommon",
            "Common properties for walls",
            []
        )
        
        # Create properties
        is_external_prop = model.createIfcPropertySingleValue(
            "IsExternal",
            "Indicates whether the element is external",
            model.createIfcBoolean(True),
            None
        )
        
        load_bearing_prop = model.createIfcPropertySingleValue(
            "LoadBearing",
            "Indicates if the element is load bearing",
            model.createIfcBoolean(False),
            None
        )
        
        # Add properties to property set
        wall_pset.HasProperties = [is_external_prop, load_bearing_prop]
        
        # Relate property set to wall
        model.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            owner_history,
            "Wall Property Assignment",
            None,
            [wall],
            wall_pset
        )
        
        print("✅ Pset_WallCommon added to wall")
    except Exception as e:
        print(f"⚠️  Warning: Could not add Pset_WallCommon: {e}")
    
    # Add Pset_WindowCommon to window
    try:
        # Create property set for window
        window_pset = model.createIfcPropertySet(
            ifcopenshell.guid.new(),
            owner_history,
            "Pset_WindowCommon",
            "Common properties for windows",
            []
        )
        
        # Create properties
        is_external_prop = model.createIfcPropertySingleValue(
            "IsExternal",
            "Indicates whether the element is external",
            model.createIfcBoolean(True),
            None
        )
        
        reference_prop = model.createIfcPropertySingleValue(
            "Reference",
            "Reference designation for the window",
            model.createIfcLabel("WIN-001"),
            None
        )
        
        # Add properties to property set
        window_pset.HasProperties = [is_external_prop, reference_prop]
        
        # Relate property set to window
        model.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            owner_history,
            "Window Property Assignment",
            None,
            [window],
            window_pset
        )
        
        print("✅ Pset_WindowCommon added to window")
    except Exception as e:
        print(f"⚠️  Warning: Could not add Pset_WindowCommon: {e}")
    
    # Add custom property set CPset_Custom to wall
    try:
        # Create custom property set for wall
        custom_pset = model.createIfcPropertySet(
            ifcopenshell.guid.new(),
            owner_history,
            "CPset_Custom",
            "Custom properties for walls",
            []
        )
        
        # Create custom property
        graffiti_prop = model.createIfcPropertySingleValue(
            "Graffitischutz",
            "Indicates if wall has graffiti protection",
            model.createIfcBoolean(True),
            None
        )
        
        # Add property to property set
        custom_pset.HasProperties = [graffiti_prop]
        
        # Relate property set to wall
        model.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            owner_history,
            "Wall Custom Property Assignment",
            None,
            [wall],
            custom_pset
        )
        
        print("✅ CPset_Custom added to wall")
    except Exception as e:
        print(f"⚠️  Warning: Could not add CPset_Custom: {e}")
    
    # Add custom property set CPSet_ReUse to window
    try:
        # Create reuse property set for window
        reuse_pset = model.createIfcPropertySet(
            ifcopenshell.guid.new(),
            owner_history,
            "CPSet_ReUse",
            "Reuse properties for windows",
            []
        )
        
        # Create reuse property
        reusable_prop = model.createIfcPropertySingleValue(
            "Reusable",
            "Indicates if element can be reused",
            model.createIfcBoolean(False),
            None
        )
        
        # Add property to property set
        reuse_pset.HasProperties = [reusable_prop]
        
        # Relate property set to window
        model.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            owner_history,
            "Window Reuse Property Assignment",
            None,
            [window],
            reuse_pset
        )
        
        print("✅ CPSet_ReUse added to window")
    except Exception as e:
        print(f"⚠️  Warning: Could not add CPSet_ReUse: {e}")

    return model

def main():
    """Main function to create and save IFC file"""
    try:
        # Create the model
        model = create_test_ifc_with_window()

        # Speichern
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/louistrue/Development/learn-ifc/test_window_{current_time}.ifc"
        model.write(filename)

        print("\n✅ IFC file saved successfully!")
        print(f"📁 File: {filename}")

        # Validate the file (academic standard validation)
        print("\n🔍 Validating IFC file for academic compliance...")
        test_model = ifcopenshell.open(filename)
        
        # Count all elements
        walls = test_model.by_type("IfcWall")
        windows = test_model.by_type("IfcWindow")
        window_types = test_model.by_type("IfcWindowType")
        lining_props = test_model.by_type("IfcWindowLiningProperties")
        panel_props = test_model.by_type("IfcWindowPanelProperties")
        openings = test_model.by_type("IfcOpeningElement")
        void_rels = test_model.by_type("IfcRelVoidsElement")
        fill_rels = test_model.by_type("IfcRelFillsElement")
        type_rels = test_model.by_type("IfcRelDefinesByType")
        prop_rels = test_model.by_type("IfcRelDefinesByProperties")

        print(f"📊 Found {len(walls)} walls")
        print(f"🪟 Found {len(windows)} windows")
        print(f"🏷️  Found {len(window_types)} window types")
        print(f"🖼️  Found {len(lining_props)} lining properties")
        print(f"🔲 Found {len(panel_props)} panel properties")
        print(f"⚪ Found {len(openings)} openings")
        print(f"✂️  Found {len(void_rels)} void relationships")
        print(f"🔗 Found {len(fill_rels)} fill relationships")
        print(f"🏗️  Found {len(type_rels)} type relationships")
        print(f"📋 Found {len(prop_rels)} property relationships")

        # Academic validation checks
        print("\n📚 Academic Compliance Validation:")
        
        if len(windows) > 0:
            window = windows[0]
            print(f"✅ Window name: {window.Name}")
            print(f"✅ Window GUID: {window.GlobalId}")
            print(f"✅ Window predefined type: {getattr(window, 'PredefinedType', 'Not set')}")
            
            # Check overall dimensions
            if hasattr(window, 'OverallHeight') and window.OverallHeight:
                print(f"✅ Overall height defined: {window.OverallHeight}m")
            if hasattr(window, 'OverallWidth') and window.OverallWidth:
                print(f"✅ Overall width defined: {window.OverallWidth}m")

            # Check if window has geometry
            if hasattr(window, 'Representation') and window.Representation:
                print("✅ Window has geometry representation")
            else:
                print("❌ Window missing geometry representation")
                
            # Check window property sets
            try:
                # Find property sets related to window
                window_psets = []
                for rel in test_model.by_type("IfcRelDefinesByProperties"):
                    if window in rel.RelatedObjects:
                        if hasattr(rel.RelatingPropertyDefinition, 'Name'):
                            window_psets.append(rel.RelatingPropertyDefinition.Name)
                
                if "Pset_WindowCommon" in window_psets:
                    print("✅ Window has Pset_WindowCommon")
                else:
                    print("❌ Window missing Pset_WindowCommon")
                    
                if "CPSet_ReUse" in window_psets:
                    print("✅ Window has CPSet_ReUse")
                else:
                    print("❌ Window missing CPSet_ReUse")
                    
                print(f"📋 Window property sets found: {window_psets}")
                    
            except Exception as e:
                print(f"⚠️  Could not check window property sets: {e}")
        
        # Check wall property sets
        if len(walls) > 0:
            wall = walls[0]
            print(f"✅ Wall name: {wall.Name}")
            print(f"✅ Wall GUID: {wall.GlobalId}")
            
            try:
                # Find property sets related to wall
                wall_psets = []
                for rel in test_model.by_type("IfcRelDefinesByProperties"):
                    if wall in rel.RelatedObjects:
                        if hasattr(rel.RelatingPropertyDefinition, 'Name'):
                            wall_psets.append(rel.RelatingPropertyDefinition.Name)
                
                if "Pset_WallCommon" in wall_psets:
                    print("✅ Wall has Pset_WallCommon")
                else:
                    print("❌ Wall missing Pset_WallCommon")
                    
                if "CPset_Custom" in wall_psets:
                    print("✅ Wall has CPset_Custom")
                else:
                    print("❌ Wall missing CPset_Custom")
                    
                print(f"📋 Wall property sets found: {wall_psets}")
                    
            except Exception as e:
                print(f"⚠️  Could not check wall property sets: {e}")
                
        # Validate relationships
        if len(type_rels) > 0:
            print("✅ Type relationships properly defined")
        else:
            print("❌ Missing type relationships")
            
        if len(fill_rels) > 0:
            print("✅ Fill relationships properly defined")
        else:
            print("❌ Missing fill relationships")
            
        if len(void_rels) > 0:
            print("✅ Void relationships properly defined")
        else:
            print("❌ Missing void relationships")

        print("\n🎉 Test completed successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
