#!/usr/bin/env python3
"""
Airtable + IFC Integration Demo

Demonstrates how external data (fire ratings, costs, fabrication data) can be stored
in Airtable and linked to IFC elements via IfcDocumentReference, proving that not
all BIM data needs to be embedded in IFC files.

This script:
1. Opens existing IFC model (03_BIMcollab_Example_STR.ifc)
2. Extracts all IfcBuildingElement entities (walls, slabs, beams, columns)
3. Creates Airtable records with mock data for each element
4. Adds IfcDocumentReference entities linking to Airtable records
5. Links references to elements via IfcRelAssociatesDocument
6. Saves augmented IFC file with external references

Students will see:
- IFC geometry remains unchanged
- External data (costs, fire ratings) stored in Airtable
- IfcDocumentReference links enable bidirectional sync
- Proof that not all data must be in IFC files
"""

import ifcopenshell
import json
import random
import datetime
from pathlib import Path
from pyairtable import Api
from pyairtable.formulas import match


def load_config(config_path="airtable_config.json"):
    """Load Airtable configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def get_building_elements(ifc_model):
    """Extract all IfcBuildingElement entities from IFC model"""
    elements = []
    
    # Get all building element types
    element_types = [
        'IfcWall', 'IfcWallStandardCase',
        'IfcSlab', 'IfcBeam', 'IfcColumn',
        'IfcBuildingElementProxy', 'IfcMember',
        'IfcPlate', 'IfcRoof', 'IfcCurtainWall'
    ]
    
    for element_type in element_types:
        elements.extend(ifc_model.by_type(element_type))
    
    return elements


def generate_mock_properties(element):
    """Generate mock data for element properties"""
    element_type = element.is_a()
    
    # Fire ratings based on element type
    fire_ratings = {
        'IfcWall': ['F30', 'F60', 'F90'],
        'IfcWallStandardCase': ['F30', 'F60', 'F90'],
        'IfcSlab': ['F30', 'F60', 'F90', 'F120'],
        'IfcBeam': ['F30', 'F60', 'F90'],
        'IfcColumn': ['F30', 'F60', 'F90', 'F120'],
        'IfcRoof': ['F30', 'F60'],
    }
    
    fire_rating = random.choice(fire_ratings.get(element_type, ['F30', 'F60']))
    
    # Cost basis based on element type
    if element_type in ['IfcWall', 'IfcWallStandardCase']:
        cost_basis = 'm2'
        unit_cost = round(random.uniform(50, 200), 2)  # €/m2
    elif element_type in ['IfcSlab', 'IfcRoof']:
        cost_basis = 'm2'
        unit_cost = round(random.uniform(80, 300), 2)  # €/m2
    elif element_type in ['IfcBeam', 'IfcColumn', 'IfcMember']:
        cost_basis = 'm'
        unit_cost = round(random.uniform(150, 500), 2)  # €/m
    else:
        cost_basis = 'ea'
        unit_cost = round(random.uniform(100, 1000), 2)  # €/ea
    
    # Try to get quantity from IFC if available
    quantity = None
    if hasattr(element, 'IsDefinedBy') and element.IsDefinedBy:
        for rel in element.IsDefinedBy:
            if rel.is_a('IfcRelDefinesByProperties'):
                prop_set = rel.RelatingPropertyDefinition
                if prop_set.is_a('IfcElementQuantity'):
                    for qty in prop_set.Quantities:
                        if qty.is_a('IfcQuantityArea'):
                            quantity = qty.AreaValue
                            break
                        elif qty.is_a('IfcQuantityLength'):
                            quantity = qty.LengthValue
                            break
    
    return {
        'fire_rating': fire_rating,
        'unit_cost': unit_cost,
        'cost_basis': cost_basis,
        'quantity': quantity if quantity else round(random.uniform(1, 100), 2)
    }


def generate_mock_fabrication():
    """Generate mock fabrication data"""
    suppliers = [
        'Betonwerk AG', 'Stahlbau Müller', 'Holzbau Schneider',
        'Prefab Concrete Ltd', 'Steel Structures Inc', 'Timber Solutions GmbH'
    ]
    
    statuses = ['ordered', 'in production', 'delivered']
    
    return {
        'supplier': random.choice(suppliers),
        'lead_time_days': random.randint(7, 60),
        'status': random.choice(statuses)
    }


def create_airtable_records(api, config, elements):
    """Create Airtable records for all elements"""
    props_table = api.table(config['base_id'], config['tables']['properties'])
    fab_table = api.table(config['base_id'], config['tables']['fabrication'])
    
    field_maps = config['field_mappings']
    props_fields = field_maps['properties']
    fab_fields = field_maps['fabrication']
    
    records_created = []
    element_guid_to_record_id = {}
    
    print(f"\nCreating Airtable records for {len(elements)} elements...")
    
    # Process in batches (Airtable allows up to 10 records per batch)
    batch_size = 10
    for i in range(0, len(elements), batch_size):
        batch = elements[i:i+batch_size]
        props_batch = []
        fab_batch = []
        
        for element in batch:
            guid = element.GlobalId
            element_type = element.is_a()
            name = element.Name if hasattr(element, 'Name') and element.Name else f"{element_type} {guid[:8]}"
            
            # Generate mock data
            props = generate_mock_properties(element)
            fab = generate_mock_fabrication()
            
            # Create properties record
            props_record = {
                props_fields['ifc_guid']: guid,
                props_fields['element_type']: element_type,
                props_fields['fire_rating']: props['fire_rating'],
                props_fields['unit_cost']: props['unit_cost'],
                props_fields['cost_basis']: props['cost_basis'],
                props_fields['last_updated']: datetime.datetime.now().isoformat()
            }
            # Note: Quantity is NOT stored in Airtable - it comes from IFC model geometry only
            props_batch.append(props_record)
            
            # Create fabrication record
            fab_record = {
                fab_fields['ifc_guid']: guid,
                fab_fields['supplier']: fab['supplier'],
                fab_fields['lead_time_days']: fab['lead_time_days'],
                fab_fields['status']: fab['status']
            }
            # Note: Material is NOT stored in Airtable - it comes from IFC model properties only
            fab_batch.append(fab_record)
        
        # Create records in Airtable
        try:
            props_response = props_table.batch_create(props_batch)
            fab_response = fab_table.batch_create(fab_batch)
            
            # Map GUIDs to record IDs
            for props_rec, fab_rec, element in zip(props_response, fab_response, batch):
                guid = element.GlobalId
                element_guid_to_record_id[guid] = {
                    'properties_id': props_rec['id'],
                    'fabrication_id': fab_rec['id'],
                    'properties_url': f"https://airtable.com/{config['base_id']}/{config['tables']['properties']}/{props_rec['id']}",
                    'fabrication_url': f"https://airtable.com/{config['base_id']}/{config['tables']['fabrication']}/{fab_rec['id']}"
                }
                records_created.append(guid)
            
            print(f"  Created batch {i//batch_size + 1} ({len(batch)} elements)")
            
        except Exception as e:
            print(f"  ERROR: Error creating batch {i//batch_size + 1}: {e}")
            raise
    
    print(f"Successfully created {len(records_created)} Airtable records")
    return element_guid_to_record_id


def add_document_references(ifc_model, element_guid_to_record_id, owner_history):
    """Add IfcDocumentReference entities and link them to elements"""
    
    print(f"\nAdding IfcDocumentReference entities to IFC model...")
    
    # Get base_id from config (we'll need to reload or pass it)
    references_added = 0
    
    for guid, record_info in element_guid_to_record_id.items():
        try:
            # Find element by GUID
            element = ifc_model.by_id(guid)
            if not element:
                # Try to find by iterating
                found = False
                for elem in get_building_elements(ifc_model):
                    if elem.GlobalId == guid:
                        element = elem
                        found = True
                        break
                if not found:
                    continue
            
            # Create IfcDocumentReference for properties
            # IFC2X3 vs IFC4 have different signatures
            if ifc_model.schema == "IFC2X3":
                # IFC2X3: IfcDocumentReference inherits from IfcExternalReference
                # Parameter order: Location, ItemReference, Name
                props_doc_ref = ifc_model.createIfcDocumentReference(
                    record_info['properties_url'],     # Location (URL first!)
                    record_info['properties_id'],      # ItemReference
                    "External Properties"              # Name
                )
                
                fab_doc_ref = ifc_model.createIfcDocumentReference(
                    record_info['fabrication_url'],    # Location (URL first!)
                    record_info['fabrication_id'],     # ItemReference
                    "Fabrication Data"                 # Name
                )
            else:
                # IFC4: GlobalId, OwnerHistory, Name, Description, Location, Identification, ReferencedDocument
                props_doc_ref = ifc_model.createIfcDocumentReference(
                    ifcopenshell.guid.new(),
                    owner_history,
                    "External Properties",
                    f"Fire rating and cost data stored in Airtable",
                    record_info['properties_url'],  # Location
                    record_info['properties_id'],   # Identification
                    None  # ReferencedDocument
                )
                
                fab_doc_ref = ifc_model.createIfcDocumentReference(
                    ifcopenshell.guid.new(),
                    owner_history,
                    "Fabrication Data",
                    f"Supplier and procurement information stored in Airtable",
                    record_info['fabrication_url'],  # Location
                    record_info['fabrication_id'],   # Identification
                    None  # ReferencedDocument
                )
            
            # Link references to element via IfcRelAssociatesDocument
            ifc_model.createIfcRelAssociatesDocument(
                ifcopenshell.guid.new(),
                owner_history,
                "External Properties Reference",
                f"Links {element.is_a()} to Airtable properties",
                [element],
                props_doc_ref
            )
            
            ifc_model.createIfcRelAssociatesDocument(
                ifcopenshell.guid.new(),
                owner_history,
                "Fabrication Data Reference",
                f"Links {element.is_a()} to Airtable fabrication data",
                [element],
                fab_doc_ref
            )
            
            # Create custom property set CPSet_Airtable for visibility in IFC viewers
            # This makes the Airtable links easily visible without needing to parse IfcDocumentReference
            airtable_props = []
            
            # Properties Record URL
            props_url_prop = ifc_model.createIfcPropertySingleValue(
                "Airtable_Properties_URL",
                "URL to Airtable properties record",
                ifc_model.createIfcText(record_info['properties_url']),
                None
            )
            airtable_props.append(props_url_prop)
            
            # Properties Record ID
            props_id_prop = ifc_model.createIfcPropertySingleValue(
                "Airtable_Properties_RecordID",
                "Airtable record ID for properties",
                ifc_model.createIfcText(record_info['properties_id']),
                None
            )
            airtable_props.append(props_id_prop)
            
            # Fabrication Record URL
            fab_url_prop = ifc_model.createIfcPropertySingleValue(
                "Airtable_Fabrication_URL",
                "URL to Airtable fabrication record",
                ifc_model.createIfcText(record_info['fabrication_url']),
                None
            )
            airtable_props.append(fab_url_prop)
            
            # Fabrication Record ID
            fab_id_prop = ifc_model.createIfcPropertySingleValue(
                "Airtable_Fabrication_RecordID",
                "Airtable record ID for fabrication",
                ifc_model.createIfcText(record_info['fabrication_id']),
                None
            )
            airtable_props.append(fab_id_prop)
            
            # Create the property set
            airtable_pset = ifc_model.createIfcPropertySet(
                ifcopenshell.guid.new(),
                owner_history,
                "CPSet_Airtable",
                "Custom property set containing Airtable external references",
                airtable_props
            )
            
            # Link property set to element
            ifc_model.createIfcRelDefinesByProperties(
                ifcopenshell.guid.new(),
                owner_history,
                "Airtable External References",
                f"Links {element.is_a()} to Airtable data via custom property set",
                [element],
                airtable_pset
            )
            
            references_added += 1
            
        except Exception as e:
            print(f"  WARNING: Error adding reference for {guid}: {e}")
            continue
    
    print(f"Added {references_added} IfcDocumentReference entities")
    return references_added


def query_airtable_data(api, config, sample_guids, ifc_model):
    """Query Airtable to demonstrate reading external data"""
    props_table = api.table(config['base_id'], config['tables']['properties'])
    fab_table = api.table(config['base_id'], config['tables']['fabrication'])
    
    field_maps = config['field_mappings']
    props_fields = field_maps['properties']
    
    print(f"\nQuerying Airtable for sample elements...")
    
    for guid in sample_guids[:5]:  # Show first 5
        try:
            # Find element in IFC to get quantity
            element = None
            try:
                element = ifc_model.by_id(guid)
            except:
                for elem in get_building_elements(ifc_model):
                    if elem.GlobalId == guid:
                        element = elem
                        break
            
            # Get quantity from IFC model geometry
            quantity = None
            if element and hasattr(element, 'IsDefinedBy') and element.IsDefinedBy:
                for rel in element.IsDefinedBy:
                    if rel.is_a('IfcRelDefinesByProperties'):
                        prop_set = rel.RelatingPropertyDefinition
                        if prop_set.is_a('IfcElementQuantity'):
                            for qty in prop_set.Quantities:
                                if qty.is_a('IfcQuantityArea'):
                                    quantity = qty.AreaValue
                                    break
                                elif qty.is_a('IfcQuantityLength'):
                                    quantity = qty.LengthValue
                                    break
            
            # Query properties table
            formula = match({props_fields['ifc_guid']: guid})
            props_records = props_table.all(formula=formula)
            
            if props_records:
                props = props_records[0]['fields']
                print(f"\n  Element: {guid[:8]}...")
                print(f"    Type: {props.get(props_fields['element_type'], 'N/A')}")
                print(f"    Fire Rating: {props.get(props_fields['fire_rating'], 'N/A')}")
                print(f"    Unit Cost: {props.get(props_fields['unit_cost'], 'N/A')} €/{props.get(props_fields['cost_basis'], 'N/A')}")
                if quantity:
                    print(f"    Quantity (from IFC): {quantity:.2f}")
                    print(f"    Total Cost: {props.get(props_fields['unit_cost'], 0) * quantity:.2f} €")
                else:
                    print(f"    Quantity: Not available in IFC model")
        
        except Exception as e:
            print(f"  WARNING: Error querying {guid}: {e}")
    
    print(f"\nQuery demonstration complete")


def main():
    """Main execution function"""
    print("=" * 70)
    print("Airtable + IFC Integration Demo")
    print("=" * 70)
    print("\nThis demo shows how external data can be stored in Airtable")
    print("and linked to IFC elements via IfcDocumentReference.\n")
    
    # Load configuration
    try:
        config = load_config()
        if config['api_token'] == 'YOUR_AIRTABLE_PERSONAL_ACCESS_TOKEN_HERE':
            print("ERROR: Please configure airtable_config.json with your Airtable credentials")
            print("   1. Get your Personal Access Token from https://airtable.com/create/tokens")
            print("   2. Create a base with two tables: 'Element Properties' and 'Fabrication Data'")
            print("   3. Update airtable_config.json with your base_id and table IDs")
            return
    except FileNotFoundError:
        print("ERROR: airtable_config.json not found")
        return
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return
    
    # Initialize Airtable API
    api = Api(config['api_token'])
    
    # Load IFC model
    ifc_path = Path("Modelle/BFH-25/03_BIMcollab_Example_STR.ifc")
    if not ifc_path.exists():
        print(f"ERROR: IFC file not found at {ifc_path}")
        return
    
    print(f"\nLoading IFC model: {ifc_path}")
    model = ifcopenshell.open(str(ifc_path))
    
    # Note: IfcDocumentReference exists in both IFC2X3 and IFC4
    # ifcopenshell handles schema differences automatically
    schema_version = model.schema
    print(f"IFC Schema: {schema_version}")
    
    # Get owner history (create if doesn't exist)
    owner_history = None
    if model.by_type("IfcOwnerHistory"):
        owner_history = model.by_type("IfcOwnerHistory")[0]
    else:
        # Create minimal owner history
        org = model.createIfcOrganization(None, "Airtable Integration Demo", None, None, None)
        person = model.createIfcPerson(None, "Demo", "User", None, None, None, None, None)
        person_org = model.createIfcPersonAndOrganization(person, org, None)
        app = model.createIfcApplication(org, "1.0", "Airtable-IFC Demo", "airtable-ifc-demo")
        import time
        owner_history = model.createIfcOwnerHistory(
            person_org, app, None, "NOCHANGE", None, None, None, int(time.time())
        )
    
    # Extract building elements
    print("\nExtracting building elements from IFC...")
    elements = get_building_elements(model)
    print(f"Found {len(elements)} building elements")
    
    if len(elements) == 0:
        print("ERROR: No building elements found in IFC file")
        return
    
    # Show element type breakdown
    element_types = {}
    for elem in elements:
        elem_type = elem.is_a()
        element_types[elem_type] = element_types.get(elem_type, 0) + 1
    
    print("\nElement type breakdown:")
    for elem_type, count in sorted(element_types.items()):
        print(f"  {elem_type}: {count}")
    
    # Create Airtable records
    try:
        element_guid_to_record_id = create_airtable_records(api, config, elements)
    except Exception as e:
        print(f"ERROR creating Airtable records: {e}")
        return
    
    # Add document references to IFC
    references_added = add_document_references(model, element_guid_to_record_id, owner_history)
    
    # Save augmented IFC file
    output_path = Path("Modelle/BFH-25/03_BIMcollab_Example_STR_with_Airtable.ifc")
    print(f"\nSaving augmented IFC model to: {output_path}")
    model.write(str(output_path))
    print(f"IFC file saved successfully")
    
    # Demonstrate querying Airtable
    sample_guids = list(element_guid_to_record_id.keys())
    query_airtable_data(api, config, sample_guids, model)
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)
    print(f"Processed {len(elements)} building elements")
    print(f"Created {len(element_guid_to_record_id)} Airtable records")
    print(f"Added {references_added} IfcDocumentReference entities")
    print(f"Saved augmented IFC file: {output_path}")
    print("\nKey Takeaway:")
    print("   Geometric data remains in IFC, business data (costs, fire ratings,")
    print("   fabrication status) stored externally in Airtable and linked via")
    print("   IfcDocumentReference. Changes in Airtable update without modifying IFC!")
    print("=" * 70)


if __name__ == "__main__":
    main()

