#!/usr/bin/env python3
"""
IFC Fire Rating Enhancement Script

This script adds realistic fire ratings to an existing IFC model based on:
- Element types (walls, doors, slabs, beams, columns, etc.)
- Structural position (external vs internal walls)
- Building code standards (Swiss/European norms)
- Support for multiple languages (German, English, French)

Usage:
    python add_fire_ratings.py input.ifc output.ifc --language de
    python add_fire_ratings.py input.ifc output.ifc --language en
    python add_fire_ratings.py input.ifc output.ifc --language fr

Author: IFC Workshop Tool
Version: 1.0
"""

import ifcopenshell
import ifcopenshell.api
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple


class FireRatingConfig:
    """Configuration class for fire rating values and property sets."""

    # NOTE: FIRE_RATINGS replaced by language-specific FIRE_RATING_VALUES below
    # Legacy dictionary removed - use FIRE_RATING_VALUES instead

    # Property set names - ALWAYS English according to IFC schema
    PSET_NAMES = {
        "en": {
            "wall": "Pset_WallCommon",
            "door": "Pset_DoorCommon",
            "slab": "Pset_SlabCommon",
            "beam": "Pset_BeamCommon",
            "column": "Pset_ColumnCommon",
            "window": "Pset_WindowCommon",
            "stair": "Pset_StairCommon",
            "building": "Pset_BuildingCommon",
        },
        "de": {
            # German: Property set names MUST be English according to IFC schema
            "wall": "Pset_WallCommon",      # Not "Pset_WandAllgemein"
            "door": "Pset_DoorCommon",      # Not "Pset_TuerAllgemein"
            "slab": "Pset_SlabCommon",      # Not "Pset_PlatteAllgemein"
            "beam": "Pset_BeamCommon",      # Not "Pset_BalkenAllgemein"
            "column": "Pset_ColumnCommon",  # Not "Pset_SaeuleAllgemein"
            "window": "Pset_WindowCommon",  # Not "Pset_FensterAllgemein"
            "stair": "Pset_StairCommon",    # Not "Pset_TreppeAllgemein"
            "building": "Pset_BuildingCommon", # Not "Pset_GebaeudeAllgemein"
        },
        "fr": {
            # French: Property set names MUST be English according to IFC schema
            "wall": "Pset_WallCommon",      # Not "Pset_MurCommun"
            "door": "Pset_DoorCommon",      # Not "Pset_PorteCommune"
            "slab": "Pset_SlabCommon",      # Not "Pset_DalleCommune"
            "beam": "Pset_BeamCommon",      # Not "Pset_PoutreCommune"
            "column": "Pset_ColumnCommon",  # Not "Pset_PoteauCommun"
            "window": "Pset_WindowCommon",  # Not "Pset_FenetreCommune"
            "stair": "Pset_StairCommon",    # Not "Pset_EscalierCommun"
            "building": "Pset_BuildingCommon", # Not "Pset_BatimentCommun"
        },
        "ch": {
            # Switzerland: Property set names MUST be English according to IFC schema
            "wall": "Pset_WallCommon",
            "door": "Pset_DoorCommon",
            "slab": "Pset_SlabCommon",
            "beam": "Pset_BeamCommon",
            "column": "Pset_ColumnCommon",
            "window": "Pset_WindowCommon",
            "stair": "Pset_StairCommon",
            "building": "Pset_BuildingCommon",
        }
    }

    # Language-specific fire rating values (property names stay English)
    FIRE_RATING_VALUES = {
        "en": {
            # English fire ratings using European standard (EN 13501-2)
            # Realistic values for international building codes
            "external_wall": "REI 90",       # External walls - high fire resistance
            "internal_wall": "REI 60",       # Internal walls - standard separation
            "loadbearing_wall": "REI 90",    # Load-bearing internal walls
            "fire_separation_wall": "REI 120", # Fire compartment separation (higher rating)

            # Doors - European standards for fire doors
            "external_door": "EI2 30-C5-Sa", # External door with smoke control
            "internal_door": "EI2 30-C5",    # Internal door
            "fire_door": "EI2 60-C5-S200",  # Fire-rated door (60 min)

            # Structural elements - European construction standards
            "slab": "REI 60",                # Floor slabs (standard)
            "beam": "R 90",                  # Structural beams (load-bearing only)
            "column": "R 120",               # Structural columns (load-bearing only)
            "roof": "REI 30",                # Roof elements (lower requirement)

            # Special elements
            "stair": "R 60",                 # Stairs (load-bearing requirement)
            "window": "EW 30",               # Windows (fire resistance for frames)
        },
        "de": {
            # German fire ratings using DIN EN 13501-2 standard
            # Realistic values for German building regulations
            "external_wall": "REI 90",       # External walls - high fire resistance
            "internal_wall": "REI 60",       # Internal walls - standard separation
            "loadbearing_wall": "REI 90",    # Load-bearing internal walls
            "fire_separation_wall": "REI 120", # Fire compartment separation (higher rating)

            # Doors - German standards for fire doors
            "external_door": "EI2 30-C5-Sa", # External door with smoke control
            "internal_door": "EI2 30-C5",    # Internal door
            "fire_door": "EI2 60-C5-S200",  # Fire-rated door (60 min)

            # Structural elements - German construction standards
            "slab": "REI 60",                # Floor slabs (standard)
            "beam": "R 90",                  # Structural beams (load-bearing only)
            "column": "R 120",               # Structural columns (load-bearing only)
            "roof": "REI 30",                # Roof elements (lower requirement)

            # Special elements
            "stair": "R 60",                 # Stairs (load-bearing requirement)
            "window": "EW 30",               # Windows (fire resistance for frames)
        },
        "fr": {
            # French fire ratings using European standard (EN 13501-2)
            # Realistic values for French building regulations
            "external_wall": "REI 90",       # External walls - high fire resistance
            "internal_wall": "REI 60",       # Internal walls - standard separation
            "loadbearing_wall": "REI 90",    # Load-bearing internal walls
            "fire_separation_wall": "REI 120", # Fire compartment separation (higher rating)

            # Doors - European standards for fire doors (French notation)
            "external_door": "EI2 30-C5-Sa", # External door with smoke control
            "internal_door": "EI2 30-C5",    # Internal door
            "fire_door": "EI2 60-C5-S200",  # Fire-rated door (60 min)

            # Structural elements - European construction standards
            "slab": "REI 60",                # Floor slabs (standard)
            "beam": "R 90",                  # Structural beams (load-bearing only)
            "column": "R 120",               # Structural columns (load-bearing only)
            "roof": "REI 30",                # Roof elements (lower requirement)

            # Special elements
            "stair": "R 60",                 # Stairs (load-bearing requirement)
            "window": "EW 30",               # Windows (fire resistance for frames)
        },
        "ch": {
            # Swiss fire ratings using VKF/SNV standards and EN 13501-2
            # Based on Swiss Cantonal Fire Insurance Providers standards
            "external_wall": "REI 90",       # External walls - high fire resistance
            "internal_wall": "REI 60",       # Internal walls - standard separation
            "loadbearing_wall": "REI 90",    # Load-bearing internal walls
            "fire_separation_wall": "REI 120", # Fire compartment separation (higher rating)

            # Doors - Swiss standards (T for Tür, EI classification)
            "external_door": "T 30",         # Swiss fire door classification (30 min)
            "internal_door": "T 30",         # Swiss fire door classification (30 min)
            "fire_door": "T 60",            # Swiss fire-rated door (60 min)

            # Structural elements - Swiss construction standards
            "slab": "REI 60",                # Floor slabs (standard)
            "beam": "R 90",                  # Structural beams (load-bearing only)
            "column": "R 120",               # Structural columns (load-bearing only)
            "roof": "REI 30",                # Roof elements (lower requirement)

            # Special elements - Swiss classifications
            "stair": "R 60",                 # Stairs (load-bearing requirement)
            "window": "EI 30",               # Windows - Swiss window classification
        }
    }

    # Element type mappings
    ELEMENT_TYPE_MAP = {
        "IfcWall": "wall",
        "IfcDoor": "door",
        "IfcSlab": "slab",
        "IfcBeam": "beam",
        "IfcColumn": "column",
        "IfcWindow": "window",
        "IfcStair": "stair",
        "IfcStairFlight": "stair",
    }


class ModelAnalyzer:
    """Analyzes the IFC model structure to classify elements intelligently."""

    def __init__(self, model, language: str = "en"):
        self.model = model
        self.language = language
        self.buildings = []
        self.storeys = []
        self.spaces = []
        self._analyze_structure()

    def _analyze_structure(self):
        """Analyze the building structure for context."""
        self.buildings = list(self.model.by_type("IfcBuilding"))
        self.storeys = list(self.model.by_type("IfcBuildingStorey"))
        self.spaces = list(self.model.by_type("IfcSpace"))

        print(f"Found {len(self.buildings)} building(s)")
        print(f"Found {len(self.storeys)} storey(s)")
        print(f"Found {len(self.spaces)} space(s)")

    def classify_wall(self, wall) -> str:
        """
        Classify a wall as external, loadbearing, or internal.
        This is a simplified classification - in practice, you'd need more sophisticated
        spatial analysis or manual classification.
        """
        # Check if wall is in building envelope (simplified heuristic)
        for rel in getattr(wall, "ContainedInStructure", []):
            relating_structure = getattr(rel, "RelatingStructure", None)
            if relating_structure and relating_structure.is_a("IfcBuilding"):
                # This is likely an external wall
                return "external_wall"

        # Check if it's a load-bearing wall (simplified check)
        if hasattr(wall, "IsDefinedBy") and wall.IsDefinedBy:
            for rel in wall.IsDefinedBy:
                if hasattr(rel, "RelatingPropertyDefinition"):
                    prop_def = rel.RelatingPropertyDefinition
                    if hasattr(prop_def, "Name") and "load" in prop_def.Name.lower():
                        return "loadbearing_wall"

        # Default to internal wall
        return "internal_wall"

    def classify_door(self, door) -> str:
        """Classify door type."""
        # Check if door is external (simplified)
        for rel in getattr(door, "ContainedInStructure", []):
            relating_structure = getattr(rel, "RelatingStructure", None)
            if relating_structure and relating_structure.is_a("IfcBuilding"):
                return "external_door"

        # Check for fire door properties
        if hasattr(door, "IsDefinedBy") and door.IsDefinedBy:
            for rel in door.IsDefinedBy:
                if hasattr(rel, "RelatingPropertyDefinition"):
                    prop_def = rel.RelatingPropertyDefinition
                    if hasattr(prop_def, "Name") and ("fire" in prop_def.Name.lower() or "brand" in prop_def.Name.lower()):
                        return "fire_door"

        return "internal_door"

    def get_element_classification(self, element) -> Tuple[str, str]:
        """Get the classification and fire rating for an element."""
        element_type = element.is_a()

        if element_type == "IfcWall":
            classification = self.classify_wall(element)
        elif element_type == "IfcDoor":
            classification = self.classify_door(element)
        elif element_type in ["IfcSlab", "IfcBeam", "IfcColumn", "IfcWindow", "IfcStair", "IfcStairFlight"]:
            # Map IFC element types to fire rating classifications
            type_mapping = {
                "IfcSlab": "slab",
                "IfcBeam": "beam",
                "IfcColumn": "column",
                "IfcWindow": "window",
                "IfcStair": "stair",
                "IfcStairFlight": "stair"
            }
            classification = type_mapping.get(element_type, "internal_wall")
        else:
            # Default classification for unknown types
            classification = "internal_wall"

        return classification, FireRatingConfig.FIRE_RATING_VALUES[self.language].get(classification, "30 min")


class FireRatingManager:
    """Manages the addition of fire ratings to IFC elements."""

    def __init__(self, model: ifcopenshell.file, language: str = "en"):
        self.model = model
        self.language = language
        self.analyzer = ModelAnalyzer(model, language)
        self.pset_names = FireRatingConfig.PSET_NAMES.get(language, FireRatingConfig.PSET_NAMES["en"])

    def get_pset_name(self, element_type: str) -> str:
        """Get the appropriate property set name for the element type."""
        base_type = FireRatingConfig.ELEMENT_TYPE_MAP.get(element_type, "wall")
        return self.pset_names.get(base_type, self.pset_names["wall"])

    def add_fire_rating_property(self, element, fire_rating: str) -> bool:
        """Add fire rating property to an element."""
        try:
            element_type = element.is_a()
            pset_name = self.get_pset_name(element_type)

            # Create or get existing property set
            pset = None
            for rel in getattr(element, "IsDefinedBy", []):
                if hasattr(rel, "RelatingPropertyDefinition"):
                    prop_def = rel.RelatingPropertyDefinition
                    if hasattr(prop_def, "Name") and prop_def.Name == pset_name:
                        pset = prop_def
                        break

            if pset is None:
                # Create new property set
                pset = self.model.createIfcPropertySet(
                    GlobalId=ifcopenshell.guid.new(),
                    OwnerHistory=None,
                    Name=pset_name,
                    Description=f"Fire rating properties in {self.language}",
                    HasProperties=[]
                )

                # Link property set to element
                rel_defines_by_properties = self.model.createIfcRelDefinesByProperties(
                    GlobalId=ifcopenshell.guid.new(),
                    OwnerHistory=None,
                    Name=f"Fire rating for {element.Name or element.GlobalId}",
                    Description=None,
                    RelatedObjects=[element],
                    RelatingPropertyDefinition=pset
                )

            # Add fire rating property
            fire_rating_prop = self.model.createIfcPropertySingleValue(
                Name="FireRating",
                Description=f"Fire resistance rating in {self.language}",
                NominalValue=self.model.createIfcText(fire_rating),
                Unit=None
            )

            # Update property set
            existing_properties = list(pset.HasProperties)
            existing_properties.append(fire_rating_prop)
            pset.HasProperties = existing_properties

            return True

        except Exception as e:
            print(f"Error adding fire rating to {element.GlobalId}: {e}")
            return False

    def process_all_elements(self) -> Dict[str, int]:
        """Process all relevant elements and add fire ratings."""
        results = {"processed": 0, "skipped": 0, "errors": 0}

        # Define elements to process
        element_types = [
            "IfcWall", "IfcDoor", "IfcSlab", "IfcBeam",
            "IfcColumn", "IfcWindow", "IfcStair", "IfcStairFlight"
        ]

        for element_type in element_types:
            elements = list(self.model.by_type(element_type))
            print(f"Processing {len(elements)} {element_type} elements...")

            for element in elements:
                classification, fire_rating = self.analyzer.get_element_classification(element)

                success = self.add_fire_rating_property(element, fire_rating)
                if success:
                    results["processed"] += 1
                    # Print some feedback for transparency
                    if results["processed"] <= 5:  # Limit console output
                        print(f"  ✓ {element.Name or element_type} ({element.GlobalId[:8]}...): {fire_rating}")
                else:
                    results["errors"] += 1

        return results


def main():
    """Main function to run the fire rating enhancement."""
    parser = argparse.ArgumentParser(
        description="Add realistic fire ratings to an IFC model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_fire_ratings.py input.ifc output.ifc --language en  # European standards
  python add_fire_ratings.py model.ifc enhanced.ifc --language de  # German standards
  python add_fire_ratings.py batiment.ifc batiment_fire.ifc --language fr  # French standards
  python add_fire_ratings.py haus.ifc haus_feuer.ifc --language ch  # Swiss VKF standards

Language Support:
  - en: European fire rating values (EN 13501-2) - EI2 30-C5, EW 30
  - de: German fire rating values (DIN EN 13501-2) - EI2 30-C5, EW 30
  - fr: French fire rating values (EN 13501-2) - EI2 30-C5, EW 30
  - ch: Swiss fire rating values (VKF) - T 30, EI 30 (different classifications!)

IFC Schema Compliance:
  - Property set names: Always English (Pset_WallCommon, Pset_DoorCommon, etc.)
  - Property names: Always English (FireRating)
  - Property values: Standard-specific (varies by country regulations)
        """
    )

    parser.add_argument("input_file", help="Path to the input IFC file")
    parser.add_argument("output_file", help="Path to save the enhanced IFC file")
    parser.add_argument(
        "--language", "-l",
        choices=["en", "de", "fr", "ch"],
        default="en",
        help="Language/Standard for fire rating values (property set names are always English per IFC schema)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    # Load the model
    try:
        print(f"Loading IFC model: {args.input_file}")
        model = ifcopenshell.open(str(input_path))
        print(f"✓ Loaded model with {len(list(model))} entities")
    except Exception as e:
        print(f"Error loading IFC file: {e}")
        sys.exit(1)

    # Process the model
    try:
        print(f"\nAnalyzing model structure...")
        manager = FireRatingManager(model, args.language)

        print(f"\nAdding fire ratings ({args.language})...")
        results = manager.process_all_elements()

        # Save the enhanced model
        print(f"\nSaving enhanced model: {args.output_file}")
        model.write(args.output_file)

        # Summary
        print("✓ Fire rating enhancement completed!")
        print(f"  Processed: {results['processed']} elements")
        print(f"  Errors: {results['errors']}")
        print(f"  Language: {args.language}")
        print(f"  Output: {args.output_file}")

    except Exception as e:
        print(f"Error processing model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
