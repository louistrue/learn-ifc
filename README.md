# 🏗️ Learn IFC - Teaching & Learning openBIM Concepts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![IFC4](https://img.shields.io/badge/IFC-4.0-green.svg)](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/louistrue/learn-ifc/blob/main/BFH-25.ipynb)

A comprehensive educational repository for teaching and learning **Industry Foundation Classes (IFC)** and **openBIM** concepts using Python and IfcOpenShell. Perfect for students, educators, and professionals getting started with BIM programming.

## 🎯 Learning Objectives

This repository provides hands-on experience with:

- **IFC4 Standard**: Understanding the complete schema and data structure
- **BIM Programming**: Creating, modifying, and analyzing BIM models programmatically
- **Property Sets**: Standard (Pset) and custom properties for extended building information
- **Geometric Modeling**: 3D geometry creation and manipulation
- **BIM Relationships**: Spatial hierarchy, type definitions, and element relationships
- **Quality Assurance**: Model validation and IFC compliance checking
- **Interoperability**: Cross-platform BIM data exchange

## 🚀 Quick Start

### Option 1: Google Colab (Recommended for Beginners)
Click the "Open in Colab" badge above or use this direct link:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/louistrue/learn-ifc/blob/main/BFH-25.ipynb)

### Option 2: Local Installation
```bash
# Clone the repository
git clone https://github.com/louistrue/learn-ifc.git
cd learn-ifc

# Install dependencies
pip install ifcopenshell

# Run the main tutorial
python test_ifc_window.py
```

## 📚 Repository Structure

### 📓 **Educational Notebooks**
- **[`BFH-25.ipynb`](BFH-25.ipynb)** - Comprehensive tutorial (German) covering complete IFC model creation
- **[`HSLU_24_IFC.ipynb`](HSLU_24_IFC.ipynb)** - Advanced IFC concepts and techniques

### 🐍 **Python Scripts**
- **[`test_ifc_window.py`](test_ifc_window.py)** - Complete IFC model with wall, window, and property sets
- **[`create_small_house.py`](create_small_house.py)** - Multi-story building with multiple rooms and windows
- **[`add_property_sets.py`](add_property_sets.py)** - Standalone utility for adding property sets to existing IFC files

### 🏠 **Sample Models**
- **[`Modelle/`](Modelle/)** - Collection of example IFC files for learning and testing
  - Duplex models (Architecture, MEP, Electrical)
  - BIMcollab coordination examples
  - Various building types and complexities

### 🔧 **Validation & Quality**
- **[`IDS/`](IDS/)** - Information Delivery Specification files for model validation
- **[`BCF/`](BCF/)** - BIM Collaboration Format files for issue management

## 🎓 Educational Content

### **Tutorial 1: Complete IFC Model Creation**
**File:** [`BFH-25.ipynb`](BFH-25.ipynb) | **Language:** German | **Level:** Beginner to Intermediate

**What You'll Learn:**
- ✅ IFC4 project structure and spatial hierarchy
- ✅ Wall creation with proper geometry and properties
- ✅ Window modeling with openings and relationships
- ✅ Property Sets (standard and custom)
- ✅ Material assignments and styling
- ✅ Model validation and quality control

**Key Concepts Covered:**
- `IfcProject` → `IfcSite` → `IfcBuilding` → `IfcBuildingStorey` hierarchy
- `IfcWall` and `IfcWindow` creation with correct geometry
- `IfcOpeningElement` for wall penetrations
- `IfcRelVoidsElement` and `IfcRelFillsElement` relationships
- `Pset_WallCommon`, `Pset_WindowCommon` standard properties
- Custom property sets for extended building information

### **Tutorial 2: More IFC Techniques**
**File:** [`HSLU_24_IFC.ipynb`](HSLU_24_IFC.ipynb) | **Language:** German | **Level:** Intermediate to Advanced

## 🛠️ Core Technologies

- **[IfcOpenShell](http://ifcopenshell.org/)** - Python library for IFC file manipulation
- **[IFC4 Standard](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/)** - Industry Foundation Classes schema
- **Python 3.8+** - Programming language for BIM automation
- **Jupyter Notebooks** - Interactive learning environment

## 📖 Usage Examples

### Creating a Simple Wall
```python
import ifcopenshell

# Create a new IFC model
model = ifcopenshell.file()

# Create basic project structure
project = model.createIfcProject(ifcopenshell.guid.new(), None, "My Project")

# Create a wall with geometry
wall = model.createIfcWall(ifcopenshell.guid.new(), None, "Sample Wall")

# Save the model
model.write("my_model.ifc")
```

### Adding Property Sets
```python
# Add standard property set to wall
wall_pset = model.createIfcPropertySet(
    ifcopenshell.guid.new(), None, "Pset_WallCommon", "Wall properties", []
)

# Create properties
is_external = model.createIfcPropertySingleValue(
    "IsExternal", "External wall indicator", model.createIfcBoolean(True), None
)

# Link property set to wall
wall_pset.HasProperties = [is_external]
model.createIfcRelDefinesByProperties(
    ifcopenshell.guid.new(), None, "Wall Properties", None, [wall], wall_pset
)
```

### Using the Property Set Utility
```python
# Add property sets to existing IFC file
python add_property_sets.py existing_model.ifc output_with_properties.ifc
```

## 🎯 Learning Path

### **Beginner Level**
1. Start with [`BFH-25.ipynb`](BFH-25.ipynb) in Google Colab
2. Understand IFC hierarchy and basic concepts
3. Create your first wall and window
4. Experiment with different dimensions and properties

### **Intermediate Level**
1. Run [`test_ifc_window.py`](test_ifc_window.py) locally
2. Modify the script to add more elements
3. Explore the sample models in [`Modelle/`](Modelle/)
4. Learn about property sets and custom attributes

### **Advanced Level**
1. Study [`create_small_house.py`](create_small_house.py) for complex buildings
2. Work with [`HSLU_24_IFC.ipynb`](HSLU_24_IFC.ipynb) for advanced techniques
3. Implement IDS validation using files in [`IDS/`](IDS/)
4. Create your own BIM applications and workflows

## 🔍 Model Validation

All generated IFC models are validated for:
- ✅ **IFC4 Schema Compliance** - Correct entity usage and relationships
- ✅ **Geometric Integrity** - Valid 3D representations
- ✅ **Property Completeness** - Required and optional property sets
- ✅ **Relationship Consistency** - Proper spatial and logical connections
- ✅ **GUID Uniqueness** - Unique identifiers for all elements

## 🔗 Related Resources

### Standards & Documentation
- [buildingSMART International](https://www.buildingsmart.org/)
- [IFC4 Official Documentation](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/)
- [IfcOpenShell Documentation](http://ifcopenshell.org/docs)

---

**Happy Learning! 🎉** Start your BIM programming journey today with hands-on IFC modeling!