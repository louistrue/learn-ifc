#!/usr/bin/env python3
"""
IFC Building Fire Safety Information Enhancement Script

This script adds fire safety and building classification information to higher-level
IFC entities (IfcProject, IfcSite, IfcBuilding, IfcBuildingStorey).

Educational Purpose:
- Demonstrates property assignment to project/site/building/storey entities
- Shows different levels of fire safety classification in building models
- Provides realistic values for building safety parameters
- Helps students understand the hierarchy of IFC properties

Swiss Fire Safety Standards (VKF) Integration:
- QSS (Quality Assurance System) classification for sites
- Building category classification according to VKF standards
- Maximum occupancy calculations for different storey types

Usage:
    python add_building_fire_info.py input.ifc output.ifc --language de
    python add_building_fire_info.py input.ifc output.ifc --language en
    python add_building_fire_info.py input.ifc output.ifc --language fr

Author: IFC Workshop Tool
Version: 3.0 - Building Level Fire Safety Edition
"""

import ifcopenshell
import ifcopenshell.api
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple


class FireSafetyConfig:
    """Configuration class for fire safety values and property sets."""

    # Property set names for different entity types - ALWAYS English per IFC schema
    PSET_NAMES = {
        "en": {
            "project": "Pset_ProjectCommon",
            "site": "Pset_SiteCommon",
            "building": "Pset_BuildingCommon",
            "storey": "Pset_BuildingStoreyCommon",
        },
        "de": {
            "project": "Pset_ProjectCommon",
            "site": "Pset_SiteCommon",
            "building": "Pset_BuildingCommon",
            "storey": "Pset_BuildingStoreyCommon",
        },
        "fr": {
            "project": "Pset_ProjectCommon",
            "site": "Pset_SiteCommon",
            "building": "Pset_BuildingCommon",
            "storey": "Pset_BuildingStoreyCommon",
        },
        "ch": {
            "project": "Pset_ProjectCommon",
            "site": "Pset_SiteCommon",
            "building": "Pset_BuildingCommon",
            "storey": "Pset_BuildingStoreyCommon",
        }
    }

    # Fire safety values by language
    FIRE_SAFETY_VALUES = {
        "en": {
            "site_qss_level": "QSS Level 3",  # Quality Safety System Level 3
            "building_category": "Medium-rise building",  # VKF building category
            "building_vkf_category": "Medium height building",
            "storey_occupancy_basement": 5,      # Realistic occupancy per storey type
            "storey_occupancy_ground": 50,
            "storey_occupancy_upper": 30,
            "storey_occupancy_roof": 10,
        },
        "de": {
            "site_qss_level": "QSS Stufe 3",     # Quality Safety System Level 3
            "building_category": "Gebäude mittlerer Höhe",  # Medium-rise building
            "building_vkf_category": "Gebäude mittlerer Höhe",
            "storey_occupancy_basement": 5,      # Realistic occupancy per storey type
            "storey_occupancy_ground": 50,
            "storey_occupancy_upper": 30,
            "storey_occupancy_roof": 10,
        },
        "fr": {
            "site_qss_level": "QSS Niveau 3",    # Quality Safety System Level 3
            "building_category": "Bâtiment de hauteur moyenne",  # Medium-rise building
            "building_vkf_category": "Bâtiment de hauteur moyenne",
            "storey_occupancy_basement": 5,      # Realistic occupancy per storey type
            "storey_occupancy_ground": 50,
            "storey_occupancy_upper": 30,
            "storey_occupancy_roof": 10,
        },
        "ch": {
            "site_qss_level": "QSS Stufe 3",     # Swiss QSS classification
            "building_category": "Gebäudekategorie VKF",  # VKF building category
            "building_vkf_category": "Gebäude mittlerer Höhe",  # Medium height building
            "storey_occupancy_basement": 5,      # Realistic occupancy per storey type
            "storey_occupancy_ground": 50,
            "storey_occupancy_upper": 30,
            "storey_occupancy_roof": 10,
        }
    }


class BuildingFireSafetyManager:
    """Manages fire safety information for building entities."""

    def __init__(self, model: ifcopenshell.file, language: str = "en"):
        self.model = model
        self.language = language
        self.config = FireSafetyConfig()
        self.pset_names = self.config.PSET_NAMES.get(language, self.config.PSET_NAMES["en"])
        self.fire_values = self.config.FIRE_SAFETY_VALUES.get(language, self.config.FIRE_SAFETY_VALUES["en"])

        # Get existing OwnerHistory for IFC2X3 compatibility
        self.owner_history = self._get_or_create_owner_history()

    def _get_or_create_owner_history(self):
        """Get existing OwnerHistory or create a minimal one for IFC2X3 compatibility."""
        try:
            # Try to get existing OwnerHistory
            owner_histories = list(self.model.by_type("IfcOwnerHistory"))
            if owner_histories:
                return owner_histories[0]  # Use the first existing one
        except:
            pass

        # If no OwnerHistory exists, try to get one from an existing entity
        try:
            # Look for any entity that has OwnerHistory
            for entity in self.model:
                if hasattr(entity, "OwnerHistory") and entity.OwnerHistory:
                    return entity.OwnerHistory
                break  # Just check the first few entities
        except:
            pass

        # As a last resort, create a minimal OwnerHistory
        # This is for IFC2X3 compatibility - in practice, you'd want proper ownership tracking
        try:
            # Create minimal required entities for OwnerHistory
            person = self.model.createIfcPersonAndOrganization(
                ThePerson=None,
                TheOrganization=None,
                Roles=None
            )

            application = self.model.createIfcApplication(
                ApplicationDeveloper=None,
                Version=None,
                ApplicationFullName="Fire Safety Enhancement Tool",
                ApplicationIdentifier="FSET-v3.0"
            )

            # Create a minimal OwnerHistory
            owner_history = self.model.createIfcOwnerHistory(
                OwningUser=person,
                OwningApplication=application,
                State=None,
                ChangeAction=None,
                LastModifiedDate=None,
                LastModifyingUser=None,
                LastModifyingApplication=None,
                CreationDate=None
            )
            return owner_history
        except Exception as e:
            print(f"  ⚠️  Could not create OwnerHistory: {e}")
            return None

    def add_fire_safety_property(self, entity, property_name: str, property_value, property_type: str = "text") -> bool:
        """
        Add a fire safety property to an entity.

        Args:
            entity: The IFC entity to add property to
            property_name: Name of the property (English only per IFC schema)
            property_value: Value of the property
            property_type: Type of property value ("text", "integer", "real")
        """
        try:
            # Determine property set name based on entity type
            entity_type = entity.is_a()
            if "Project" in entity_type:
                pset_name = self.pset_names["project"]
            elif "Site" in entity_type:
                pset_name = self.pset_names["site"]
            elif "Building" in entity_type:
                pset_name = self.pset_names["building"]
            elif "BuildingStorey" in entity_type:
                pset_name = self.pset_names["storey"]
            else:
                pset_name = self.pset_names["building"]  # Default fallback

            # Check if property set already exists
            pset = None
            if hasattr(entity, "IsDefinedBy"):
                for rel in entity.IsDefinedBy:
                    if hasattr(rel, "RelatingPropertyDefinition"):
                        prop_def = rel.RelatingPropertyDefinition
                        if hasattr(prop_def, "Name") and prop_def.Name == pset_name:
                            pset = prop_def
                            break

            if pset is None:
                # Create new property set
                pset = self.model.createIfcPropertySet(
                    GlobalId=ifcopenshell.guid.new(),
                    OwnerHistory=self.owner_history,  # Use existing or created OwnerHistory
                    Name=pset_name,
                    Description=f"Fire safety properties in {self.language}",
                    HasProperties=[]
                )

                # Link property set to entity
                rel_defines_by_properties = self.model.createIfcRelDefinesByProperties(
                    GlobalId=ifcopenshell.guid.new(),
                    OwnerHistory=self.owner_history,  # Use existing or created OwnerHistory
                    Name=f"Fire safety for {entity.Name or entity.GlobalId}",
                    Description=None,
                    RelatedObjects=[entity],
                    RelatingPropertyDefinition=pset
                )

            # Create the property based on type
            if property_type == "integer":
                nominal_value = self.model.createIfcInteger(property_value)
            elif property_type == "real":
                nominal_value = self.model.createIfcReal(property_value)
            else:  # text as default
                nominal_value = self.model.createIfcText(str(property_value))

            # Create the property
            fire_safety_prop = self.model.createIfcPropertySingleValue(
                Name=property_name,
                Description=f"Fire safety property in {self.language}",
                NominalValue=nominal_value,
                Unit=None
            )

            # Add property to property set
            existing_properties = list(pset.HasProperties)
            existing_properties.append(fire_safety_prop)
            pset.HasProperties = existing_properties

            return True

        except Exception as e:
            print(f"  ❌ Error adding {property_name} to {entity.GlobalId}: {e}")
            return False

    def classify_storey_type(self, storey) -> str:
        """
        Classify a storey based on its elevation and name to determine occupancy.
        """
        storey_name = getattr(storey, "Name", "") or ""
        storey_name_str = str(storey_name).lower()

        # Get storey elevation
        elevation = 0.0
        if hasattr(storey, "Elevation"):
            elevation = float(storey.Elevation) if storey.Elevation else 0.0

        # Classification logic
        if elevation < 0:
            return "basement"
        elif elevation == 0 or "ground" in storey_name_str or "erdgeschoss" in storey_name_str or "rez-de-chaussée" in storey_name_str:
            return "ground"
        elif "roof" in storey_name_str or "dach" in storey_name_str or "toit" in storey_name_str:
            return "roof"
        else:
            return "upper"

    def add_site_fire_safety(self, site) -> bool:
        """Add fire safety classification to site."""
        success_count = 0

        # Add QSS Level
        if self.add_fire_safety_property(site, "SiteFireSafetyLevel", self.fire_values["site_qss_level"]):
            success_count += 1
            print(f"  ✅ Site Fire Safety Level: {self.fire_values['site_qss_level']}")

        # Add additional site safety information
        if self.add_fire_safety_property(site, "SiteSafetyClassification", "QSS Certified"):
            success_count += 1

        return success_count > 0

    def add_building_fire_safety(self, building) -> bool:
        """Add fire safety classification to building."""
        success_count = 0

        # Add VKF building category
        if self.add_fire_safety_property(building, "BuildingFireCategory", self.fire_values["building_vkf_category"]):
            success_count += 1
            print(f"  ✅ Building Fire Category: {self.fire_values['building_vkf_category']}")

        # Add building height classification
        if self.add_fire_safety_property(building, "BuildingHeightCategory", self.fire_values["building_category"]):
            success_count += 1

        # Add fire safety compliance
        if self.add_fire_safety_property(building, "FireSafetyCompliance", "VKF Standards Compliant"):
            success_count += 1

        return success_count > 0

    def add_storey_fire_safety(self, storey) -> bool:
        """Add fire safety information to building storey."""
        success_count = 0

        # Classify storey type and get appropriate occupancy
        storey_type = self.classify_storey_type(storey)
        occupancy = self.fire_values[f"storey_occupancy_{storey_type}"]

        # Add maximum occupancy
        if self.add_fire_safety_property(storey, "MaximumOccupancy", occupancy, "integer"):
            success_count += 1
            print(f"  ✅ Storey Occupancy ({storey_type}): {occupancy} persons")

        # Add storey fire safety classification
        storey_safety_class = f"Storey {storey_type.title()} - Fire Compartment"
        if self.add_fire_safety_property(storey, "StoreyFireClassification", storey_safety_class):
            success_count += 1

        # Add escape route information
        if storey_type == "ground":
            escape_routes = 2
        else:
            escape_routes = 1

        if self.add_fire_safety_property(storey, "EscapeRoutesCount", escape_routes, "integer"):
            success_count += 1

        return success_count > 0

    def process_all_building_entities(self) -> Dict[str, int]:
        """Process all building-level entities and add fire safety information."""
        results = {"sites": 0, "buildings": 0, "storeys": 0, "total_properties": 0}

        # Process sites
        sites = list(self.model.by_type("IfcSite"))
        print(f"🔍 Processing {len(sites)} site(s)...")
        for site in sites:
            if self.add_site_fire_safety(site):
                results["sites"] += 1
                results["total_properties"] += 1

        # Process buildings
        buildings = list(self.model.by_type("IfcBuilding"))
        print(f"🏢 Processing {len(buildings)} building(s)...")
        for building in buildings:
            if self.add_building_fire_safety(building):
                results["buildings"] += 1
                results["total_properties"] += 3  # We add 3 properties per building

        # Process building storeys
        storeys = list(self.model.by_type("IfcBuildingStorey"))
        print(f"🏠 Processing {len(storeys)} storey(s)...")
        for storey in storeys:
            if self.add_storey_fire_safety(storey):
                results["storeys"] += 1
                results["total_properties"] += 3  # We add 3 properties per storey

        return results

    def show_fire_safety_summary(self):
        """Show a summary of fire safety classifications used."""
        print("\n" + "="*60)
        print("🔥 FIRE SAFETY CLASSIFICATION SUMMARY")
        print("="*60)
        print(f"🌍 Language/Standard: {self.language.upper()}")
        print(f"🏗️  Site Classification: {self.fire_values['site_qss_level']}")
        print(f"🏢 Building Category: {self.fire_values['building_vkf_category']}")
        print("\n📊 Occupancy by Storey Type:")
        print(f"   • Basement: {self.fire_values['storey_occupancy_basement']} persons")
        print(f"   • Ground: {self.fire_values['storey_occupancy_ground']} persons")
        print(f"   • Upper floors: {self.fire_values['storey_occupancy_upper']} persons")
        print(f"   • Roof: {self.fire_values['storey_occupancy_roof']} persons")

        print("""
💡 Educational Notes:
   • QSS (Quality Safety System) is a Swiss fire safety certification
   • VKF = Vereinigung Kantonaler Feuerversicherungen (Swiss fire insurance association)
   • Building categories determine required fire safety measures
   • Occupancy calculations are crucial for evacuation planning""")


def main():
    """Main function to run the building fire safety enhancement."""
    parser = argparse.ArgumentParser(
        description="Add fire safety information to IFC building entities (site, building, storeys)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python add_building_fire_info.py model.ifc enhanced.ifc --language en  # English
  python add_building_fire_info.py haus.ifc haus_feuer.ifc --language de  # German
  python add_building_fire_info.py batiment.ifc batiment_feu.ifc --language fr  # French
  python add_building_fire_info.py gebaeude.ifc gebaeude_feuer.ifc --language ch  # Swiss

Fire Safety Standards:
  - Site: QSS (Quality Safety System) classification levels
  - Building: VKF (Swiss fire insurance) building categories
  - Storeys: Realistic maximum occupancy values by storey type
  - All classifications based on Swiss/European fire safety standards
        """
    )

    parser.add_argument("input_file", help="Path to the input IFC file")
    parser.add_argument("output_file", help="Path to save the enhanced IFC file")
    parser.add_argument(
        "--language", "-l",
        choices=["en", "de", "fr", "ch"],
        default="en",
        help="Language for fire safety classification descriptions"
    )
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show fire safety summary before processing"
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    # Load the model
    try:
        print(f"📂 Loading IFC model: {args.input_file}")
        model = ifcopenshell.open(str(input_path))
        print(f"✅ Loaded model with {len(list(model))} entities")
    except Exception as e:
        print(f"❌ Error loading IFC file: {e}")
        sys.exit(1)

    # Process the model
    try:
        print(f"\n🔍 Analyzing building structure...")
        manager = BuildingFireSafetyManager(model, args.language)

        # Show summary if requested
        if args.summary:
            manager.show_fire_safety_summary()

        print(f"\n🔥 Adding fire safety information ({args.language})...")
        results = manager.process_all_building_entities()

        # Save the enhanced model
        print(f"\n💾 Saving enhanced model: {args.output_file}")
        model.write(args.output_file)

        # Final summary
        print("\n" + "="*60)
        print("🎯 BUILDING FIRE SAFETY ENHANCEMENT COMPLETED!")
        print("="*60)
        print(f"  🏗️  Sites processed: {results['sites']}")
        print(f"  🏢 Buildings processed: {results['buildings']}")
        print(f"  🏠 Storeys processed: {results['storeys']}")
        print(f"  📊 Total properties added: {results['total_properties']}")
        print(f"  🌍 Language: {args.language}")
        print(f"  📄 Output: {args.output_file}")

        print("""
📚 Key Learning Points:
  • Fire safety properties added at building/site/storey level
  • Different entities require different fire safety classifications
  • QSS and VKF are Swiss fire safety standards
  • Occupancy calculations are essential for evacuation planning
  • This complements the door type properties from the previous script""")
    except Exception as e:
        print(f"❌ Error processing model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
