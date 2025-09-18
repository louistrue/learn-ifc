#!/usr/bin/env python3
"""
Add Property Sets to IFC Elements
Demonstrates how to add standard and custom property sets to walls and windows
"""

import ifcopenshell
import ifcopenshell.guid

def add_property_sets_to_model(ifc_file_path, output_file_path=None):
    """
    Add property sets to walls and windows in an existing IFC model
    
    Args:
        ifc_file_path (str): Path to input IFC file
        output_file_path (str): Path for output file (optional, defaults to input + "_with_psets")
    """
    
    # Open the IFC model
    model = ifcopenshell.open(ifc_file_path)
    print(f"📂 Opened IFC file: {ifc_file_path}")
    
    # Get owner history (needed for creating relationships)
    owner_history = model.by_type("IfcOwnerHistory")[0] if model.by_type("IfcOwnerHistory") else None
    
    # Get all walls and windows
    walls = model.by_type("IfcWall")
    windows = model.by_type("IfcWindow")
    
    print(f"🏗️  Found {len(walls)} walls and {len(windows)} windows")
    
    # Add property sets to walls
    for i, wall in enumerate(walls):
        print(f"\n📋 Processing Wall {i+1}: {wall.Name or 'Unnamed'}")
        
        # Add Pset_WallCommon
        wall_pset = model.createIfcPropertySet(
            ifcopenshell.guid.new(),
            owner_history,
            "Pset_WallCommon",
            "Common properties for walls",
            []
        )
        
        # Create properties for Pset_WallCommon
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
            f"Wall {i+1} Pset_WallCommon Assignment",
            None,
            [wall],
            wall_pset
        )
        print("  ✅ Added Pset_WallCommon (IsExternal=True, LoadBearing=False)")
        
        # Add custom property set CPset_Custom
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
            f"Wall {i+1} CPset_Custom Assignment",
            None,
            [wall],
            custom_pset
        )
        print("  ✅ Added CPset_Custom (Graffitischutz=True)")
    
    # Add property sets to windows
    for i, window in enumerate(windows):
        print(f"\n🪟 Processing Window {i+1}: {window.Name or 'Unnamed'}")
        
        # Add Pset_WindowCommon
        window_pset = model.createIfcPropertySet(
            ifcopenshell.guid.new(),
            owner_history,
            "Pset_WindowCommon",
            "Common properties for windows",
            []
        )
        
        # Create properties for Pset_WindowCommon
        is_external_prop = model.createIfcPropertySingleValue(
            "IsExternal",
            "Indicates whether the element is external", 
            model.createIfcBoolean(True),
            None
        )
        
        reference_prop = model.createIfcPropertySingleValue(
            "Reference",
            "Reference designation for the window",
            model.createIfcLabel(f"WIN-{i+1:03d}"),
            None
        )
        
        # Add properties to property set
        window_pset.HasProperties = [is_external_prop, reference_prop]
        
        # Relate property set to window
        model.createIfcRelDefinesByProperties(
            ifcopenshell.guid.new(),
            owner_history,
            f"Window {i+1} Pset_WindowCommon Assignment",
            None,
            [window],
            window_pset
        )
        print(f"  ✅ Added Pset_WindowCommon (IsExternal=True, Reference=WIN-{i+1:03d})")
        
        # Add custom property set CPSet_ReUse
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
            f"Window {i+1} CPSet_ReUse Assignment",
            None,
            [window],
            reuse_pset
        )
        print("  ✅ Added CPSet_ReUse (Reusable=False)")
    
    # Save the updated model
    if output_file_path is None:
        output_file_path = ifc_file_path.replace('.ifc', '_with_psets.ifc')
    
    model.write(output_file_path)
    print(f"\n💾 Saved updated model to: {output_file_path}")
    
    return output_file_path

def validate_property_sets(ifc_file_path):
    """Validate that property sets were added correctly"""
    
    model = ifcopenshell.open(ifc_file_path)
    
    walls = model.by_type("IfcWall")
    windows = model.by_type("IfcWindow")
    prop_rels = model.by_type("IfcRelDefinesByProperties")
    
    print(f"\n🔍 Validation Results:")
    print(f"  📊 Found {len(walls)} walls, {len(windows)} windows")
    print(f"  📋 Found {len(prop_rels)} property relationships")
    
    # Check wall property sets
    for wall in walls:
        wall_psets = []
        for rel in prop_rels:
            if wall in rel.RelatedObjects:
                if hasattr(rel.RelatingPropertyDefinition, 'Name'):
                    pset_name = rel.RelatingPropertyDefinition.Name
                    wall_psets.append(pset_name)
                    
                    # Check specific properties
                    if pset_name == "Pset_WallCommon":
                        pset = rel.RelatingPropertyDefinition
                        for prop in pset.HasProperties:
                            if prop.Name == "IsExternal":
                                print(f"    ✅ Wall {wall.Name}: IsExternal = {prop.NominalValue.wrappedValue}")
                            elif prop.Name == "LoadBearing":
                                print(f"    ✅ Wall {wall.Name}: LoadBearing = {prop.NominalValue.wrappedValue}")
                    elif pset_name == "CPset_Custom":
                        pset = rel.RelatingPropertyDefinition
                        for prop in pset.HasProperties:
                            if prop.Name == "Graffitischutz":
                                print(f"    ✅ Wall {wall.Name}: Graffitischutz = {prop.NominalValue.wrappedValue}")
        
        print(f"  🏗️  Wall '{wall.Name or 'Unnamed'}' has property sets: {wall_psets}")
    
    # Check window property sets  
    for window in windows:
        window_psets = []
        for rel in prop_rels:
            if window in rel.RelatedObjects:
                if hasattr(rel.RelatingPropertyDefinition, 'Name'):
                    pset_name = rel.RelatingPropertyDefinition.Name
                    window_psets.append(pset_name)
                    
                    # Check specific properties
                    if pset_name == "Pset_WindowCommon":
                        pset = rel.RelatingPropertyDefinition
                        for prop in pset.HasProperties:
                            if prop.Name == "IsExternal":
                                print(f"    ✅ Window {window.Name}: IsExternal = {prop.NominalValue.wrappedValue}")
                            elif prop.Name == "Reference":
                                print(f"    ✅ Window {window.Name}: Reference = {prop.NominalValue.wrappedValue}")
                    elif pset_name == "CPSet_ReUse":
                        pset = rel.RelatingPropertyDefinition
                        for prop in pset.HasProperties:
                            if prop.Name == "Reusable":
                                print(f"    ✅ Window {window.Name}: Reusable = {prop.NominalValue.wrappedValue}")
        
        print(f"  🪟 Window '{window.Name or 'Unnamed'}' has property sets: {window_psets}")

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python add_property_sets.py <input_ifc_file> [output_ifc_file]")
        print("\nExample:")
        print("  python add_property_sets.py model.ifc")
        print("  python add_property_sets.py model.ifc model_with_props.ifc")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Add property sets
        output_path = add_property_sets_to_model(input_file, output_file)
        
        # Validate the results
        validate_property_sets(output_path)
        
        print("\n🎉 Property sets added successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
