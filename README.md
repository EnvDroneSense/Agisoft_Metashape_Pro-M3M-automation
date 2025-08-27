# Metashape Automation Tools - Generic Version

This folder contains portable, generic versions of all Metashape automation tools with no hardcoded file paths. These scripts can be used in any project by simply configuring the required paths.

**Originally developed for DJI Mavic 3 Multispectral (M3M) drone data processing**, these scripts support both RGB and multispectral workflows for professional photogrammetry projects.

## Quick Start

### Method 1: Using the GUI Configuration Tool (Recommended)

1. **Launch the tool**: Double-click `start_config_tool_generic.bat`
2. **Configure paths**: Set script folder, DCIM, GCP, and output paths
3. **Select processing**: Choose RGB, MS, or Combined processing with single or multiple routes
4. **Generate commands**: Get ready-to-use Metashape console commands

### Method 2: Direct Script Usage

Load scripts directly in Metashape console with manual configuration.

## Tools Overview

### Configuration Tool
- **`config_tool_generic.py`** - GUI tool for generating Metashape console commands
- **`start_config_tool_generic.bat`** - Batch file to launch the configuration tool

### Automation Scripts

All scripts follow the naming pattern: `{type}_{mode}_automation_generic.py`

**Single Route Processing:**
- **`rgb_single_automation_generic.py`** - Process single RGB route
- **`ms_single_automation_generic.py`** - Process single multispectral route  
- **`rgb_ms_single_automation_generic.py`** - Process single route with RGB+MS combined

**Combined Route Processing:**
- **`rgb_combined_automation_generic.py`** - Process multiple RGB routes combined
- **`ms_combined_automation_generic.py`** - Process multiple multispectral routes combined
- **`rgb_ms_combined_automation_generic.py`** - Process multiple routes with RGB+MS combined

### Script Details

#### RGB Processing Scripts
- **Purpose**: Process RGB-only drone images
- **Input**: JPG files with 'D' identifier (e.g., DJI_20240515120000_0001_D.JPG)
- **Output**: Camera alignment, depth maps, point cloud, processing report
- **GCP Files**: `gcp_route_001.xml`, `gcp_route_002.xml`, etc.
- **M3M Support**: Optimized for DJI Mavic 3 Multispectral RGB sensor

#### MS Processing Scripts
- **Purpose**: Process multispectral drone images as Multi-Camera system
- **Input**: TIF files with MS band identifiers (G, NIR, R, RE)
- **Output**: Multispectral point cloud with band values for vegetation analysis
- **GCP Files**: `gcp_route_001_MS.xml`, `gcp_route_002_MS.xml`, etc.
- **M3M Support**: Native support for M3M's 4-band multispectral sensor array

#### Combined Processing Scripts
- **Purpose**: Process RGB and MS images together in combined Multi-Camera system
- **Input**: Both RGB (JPG) and MS (TIF) files
- **Output**: Full pipeline including mesh, texture, DEM, orthomosaic exports
- **GCP Files**: `gcp_route_001.xml`, `gcp_route_002.xml`, etc.
- **M3M Support**: Leverages M3M's synchronized RGB and multispectral capture capabilities

## Setup Instructions

### Prerequisites

#### Python Installation
If you don't have Python installed yet:

1. **Download Python**:
   - Go to [python.org/downloads](https://www.python.org/downloads/)
   - Download Python 3.8 or newer (3.9+ recommended)
   - Choose "Windows installer (64-bit)" for most systems

2. **Install Python**:
   - Run the installer as administrator
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Choose "Install Now" or customize installation location
   - Verify installation by opening Command Prompt and typing: `python --version`

3. **Alternative: Anaconda/Miniconda** (Recommended for data science):
   - Download from [anaconda.com](https://www.anaconda.com/products/distribution)
   - Includes Python + scientific packages + environment management
   - Good choice if you plan to do data analysis with the results

#### Required Python Packages
The scripts require these standard packages (usually included with Python):
- `os` - File system operations
- `glob` - File pattern matching  
- `re` - Regular expressions
- `tkinter` - GUI interface (for configuration tool)

If using Metashape console directly, you'll also need:
- `Metashape` - Agisoft Metashape Python API (included with Metashape Professional)

### Option 1: Using the GUI Tool (Recommended)

1. **Configure Python Path**: Edit `start_config_tool_generic.bat` and set your Python executable:
   ```batch
   # Standard Python installation
   set PYTHON_PATH=C:\Python39\python.exe
   
   # Anaconda/Miniconda
   set PYTHON_PATH=C:\Users\YourUsername\anaconda3\python.exe
   
   # Virtual Environment
   set PYTHON_PATH=C:\Your\VirtualEnv\Scripts\python.exe
   
   # System Python (if in PATH)
   set PYTHON_PATH=python
   ```

2. **Launch the GUI**: Double-click `start_config_tool_generic.bat`

3. **Configure in GUI**:
   - **Script Folder**: Browse to the folder containing your automation scripts
   - **DCIM Folder**: Your drone image folders
   - **GCP Folder**: Ground Control Points XML files
   - **Output Folder**: Where results will be saved

4. **Process Data**:
   - Select processing type (RGB, MS, or Combined)
   - Choose single or multiple route mode
   - Scan for available routes
   - Select routes to process
   - Generate Metashape console commands
   - Copy commands one by one to Metashape console

### Option 2: Direct Script Usage

#### Important: Required Imports
Before using any automation script in Metashape console, you must first import the required Python modules:

```python
# Essential imports - run these FIRST in Metashape console
import os
import glob
import re
import Metashape

# Optional but recommended for debugging
import time
import sys
from pathlib import Path

print("All required modules imported successfully!")
```

**⚠️ Critical Note**: These imports must be run in the Metashape console before loading any automation script. If you get import errors, run these imports first.

#### Step 1: Load Script in Metashape Console
```python
# Single Route Processing
exec(open(r'C:\\path\\to\\rgb_single_automation_generic.py',encoding='utf-8').read())
exec(open(r'C:\\path\\to\\ms_single_automation_generic.py',encoding='utf-8').read())
exec(open(r'C:\\path\\to\\rgb_ms_single_automation_generic.py',encoding='utf-8').read())

# Combined Route Processing
exec(open(r'C:\\path\\to\\rgb_combined_automation_generic.py',encoding='utf-8').read())
exec(open(r'C:\\path\\to\\ms_combined_automation_generic.py',encoding='utf-8').read())
exec(open(r'C:\\path\\to\\rgb_ms_combined_automation_generic.py',encoding='utf-8').read())
```

#### Step 2: Configure Paths
```python
# Configure paths for all scripts
configure_paths(
    dcim=r'C:\\path\\to\\DCIM\\folder',        # Contains DJI route folders
    gcp=r'C:\\path\\to\\GCP\\folder',          # Contains XML GCP files
    output=r'C:\\path\\to\\output\\folder'     # Where projects will be saved
)
```

#### Step 3: Configure Routes (for Combined Processing)
```python
# For combined route processing, specify which routes to include
configure_routes(['001', '002', '003'])  # Route numbers to process together
```

#### Complete Workflow Example
Here's a complete example showing all steps including imports:

```python
# Step 1: Import required modules (ALWAYS FIRST)
import os
import glob
import re
import Metashape
import time
from pathlib import Path

# Step 2: Load automation script
exec(open(r'C:\\path\\to\\rgb_single_automation_generic.py',encoding='utf-8').read())

# Step 3: Configure paths
configure_paths(
    dcim=r'D:\\Drone_Data\\Project_Alpha\\DCIM',
    gcp=r'D:\\GCP_Files\\Project_Alpha',
    output=r'D:\\Processed\\Project_Alpha'
)

# Step 4: Process route
process_single_route_by_number('001')
```
#### Step 4: Run Processing
```python
# Single Route Processing
process_single_route_by_number('001')  # Process specific route

# Combined Route Processing
run_combined_rgb_automation()     # Process all configured RGB routes together
run_combined_ms_automation()      # Process all configured MS routes together
run_combined_rgb_ms_automation()  # Process all configured RGB+MS routes together
```

## GUI Configuration Tool Features

The `config_tool_generic.py` provides a user-friendly interface with the following features:

### Visual Interface
- **Path Selection**: Browse buttons for all required folders
- **Processing Options**: Radio buttons for RGB, MS, or Combined processing
- **Route Modes**: Single route or multiple routes combined
- **Route Detection**: Automatic scanning and preview of available routes
- **Command Generation**: Copy-paste ready Metashape console commands

### Workflow Integration
- **Route Preview**: Shows detected routes with image counts
- **Multi-selection**: Select specific routes to process
- **Command Steps**: Generates commands as individual steps for easy copying
- **Error Validation**: Checks all required inputs before generating commands

### Processing Options
- **RGB Processing**: Visible light images for standard photogrammetry
- **MS Processing**: Multispectral images for vegetation analysis
- **Combined Processing**: Both RGB and MS in unified workflow

### Route Modes
- **Single Route**: Process one route at a time (faster, individual projects)
- **Multiple Routes**: Combine multiple routes into one project (comprehensive coverage)

## Advanced Configuration

### Custom Processing Parameters
```python
# Optional: Configure processing quality settings
configure_processing(
    quality='High',           # Photo alignment quality: 'Highest', 'High', 'Medium', 'Low'
    depth_quality='Medium',   # Dense cloud quality: 'UltraHigh', 'High', 'Medium', 'Low'
    mesh_quality='Medium',    # Mesh quality: 'High', 'Medium', 'Low'
    texture_quality='Medium'  # Texture quality: 'High', 'Medium', 'Low'
)
```

### Custom Route Selection
```python
# Check available routes before processing
available_routes = get_available_routes()
print("Available routes:", available_routes)

# Process specific routes only
configure_routes(['001', '003', '005'])

# Or use helper functions for route discovery
show_available_routes()  # Lists all detectable routes with details
```

## Folder Structure Requirements

### DCIM Folder Structure
```
dcim_path/
├── DJI_20240515120000_001_Route1/
│   ├── DJI_20240515120001_0001_D.JPG        # RGB image
│   ├── DJI_20240515120001_0001_MS_G.TIF     # MS Green band
│   ├── DJI_20240515120001_0001_MS_NIR.TIF   # MS NIR band
│   ├── DJI_20240515120001_0001_MS_R.TIF     # MS Red band
│   └── DJI_20240515120001_0001_MS_RE.TIF    # MS Red Edge band
├── DJI_20240515130000_002_Route2/
└── DJI_20240515140000_003_Route3/
```

### GCP Folder Structure
```
gcp_path/
├── gcp_route_001.xml           # RGB GCP file for route 001
├── gcp_route_001_MS.xml        # MS GCP file for route 001 (if different)
├── gcp_route_002.xml           # RGB GCP file for route 002
├── gcp_route_002_MS.xml        # MS GCP file for route 002
└── ...
```

### Creating GCP XML Files

**Important**: The automation scripts require GCP XML files with pixel coordinates. These must be created manually in Metashape before running the automation scripts.

#### Step-by-Step GCP XML Creation Process:

1. **Load Images in Metashape**:
   ```
   - Create new Metashape project
   - Add photos for the specific route
   - Do NOT run any automation yet
   ```

2. **Align Cameras**:
   ```
   - Run: Workflow → Align Photos
   - Use default settings or your preferred alignment parameters
   - Wait for alignment to complete
   ```

3. **Place GCP Markers**:
   ```
   - Place markers on visible ground control points
   - For each GCP marker:
     a) Right-click in model view → "Add Marker"
     b) Label the marker (e.g., "GCP_001", "GCP_002")
     c) Click on the marker in multiple images to set pixel coordinates
     d) Add real-world coordinates in Reference panel
     e) Enable/disable marker for alignment vs check points
   ```

4. **Export GCP XML File**:
   ```
   - Go to: File → Export → Export Markers
   - Choose XML format
   - Save as: gcp_route_XXX.xml (for RGB) or gcp_route_XXX_MS.xml (for MS)
   - Place in your GCP folder
   ```

5. **Verify XML Content**:
   ```xml
   <!-- Example GCP XML structure -->
   <?xml version="1.0" encoding="UTF-8"?>
   <document>
     <markers>
       <marker id="0" label="GCP_001">
         <reference x="485123.456" y="5123456.789" z="12.345" enabled="true"/>
         <projections>
           <projection camera_id="0" x="1234.56" y="2345.67"/>
           <projection camera_id="1" x="1345.67" y="2456.78"/>
           <!-- Multiple image projections... -->
         </projections>
       </marker>
       <!-- More markers... -->
     </markers>
   </document>
   ```

#### Key Requirements for GCP XML Files:

- **Pixel Coordinates**: Each marker must have pixel coordinates (`<projection>`) in multiple images
- **World Coordinates**: Each marker must have real-world coordinates (`<reference>`)
- **Enabled Status**: Set `enabled="true"` for alignment GCPs, `enabled="false"` for check points
- **Consistent Labeling**: Use consistent marker naming across routes
- **File Naming**: Follow naming convention: `gcp_route_001.xml`, `gcp_route_002.xml`, etc.

#### Tips for GCP Placement:

1. **Image Coverage**: Place each GCP marker in 3+ images for reliable positioning
2. **Marker Distribution**: Spread GCPs across the survey area for best accuracy
3. **Check Points**: Reserve 20-30% of GCPs as check points (`enabled="false"`)
4. **Precision**: Click pixel coordinates as precisely as possible in each image
5. **Quality Control**: Review marker placement before exporting XML

**⚠️ Critical**: The automation scripts expect GCP XML files with this specific format. GCP files created through other methods (CSV import, etc.) may not work correctly.

### Output Folder Structure (Created Automatically)
```
output_path/
├── route_001_RGB/              # RGB single route results
│   ├── route_001_RGB.psx       # Metashape project file
│   └── processing_report_RGB.pdf
├── route_001_MS/               # MS single route results
│   ├── route_001_MS.psx        # Metashape project file
│   └── processing_report_MS.pdf
├── route_001_RGB_MS/           # Combined single route results
│   ├── route_001_RGB_MS.psx    # Metashape project file
│   └── processing_report_RGB_MS.pdf
├── combined_RGB/               # Combined multiple RGB routes
│   ├── combined_RGB.psx        # Metashape project file
│   ├── orthomosaic/            # Exported orthomosaic
│   ├── dem/                    # Exported DEM
│   ├── pointcloud/             # Exported point cloud
│   └── report/                 # Processing report
├── combined_MS/                # Combined multiple MS routes
│   ├── combined_MS.psx         # Metashape project file
│   └── processing_report_MS.pdf
└── combined_RGB_MS/            # Combined multiple RGB+MS routes
    ├── combined_RGB_MS.psx     # Metashape project file
    ├── orthomosaic/            # Exported orthomosaic
    ├── dem/                    # Exported DEM
    ├── pointcloud/             # Exported point cloud
    └── report/                 # Processing report
```

## Key Features

### ✅ **GUI Configuration Tool**
- Visual interface for all configuration options
- Automatic route detection and preview
- Copy-paste ready Metashape console commands
- Input validation and error checking
- Support for both single and multiple route workflows

### ✅ **Standardized Naming Convention**
- Consistent script naming: `{type}_{mode}_automation_generic.py`
- Clear distinction between single and combined processing
- Generic suffix for portability identification

### ✅ **Flexible Processing Modes**
- **Single Route**: Process individual routes separately
- **Combined Routes**: Process multiple routes together in one project
- **Mixed Processing**: RGB, MS, or RGB+MS combinations

### ✅ **Enhanced Configuration System**
- `configure_paths()`: Set DCIM, GCP, and output paths
- `configure_routes()`: Specify which routes to include in combined processing
- `configure_processing()`: Customize quality settings
- Global configuration that persists across function calls

### ✅ **Portability**
- No hardcoded paths - works on any system
- Generic versions for any project structure
- All paths configurable via function parameters or GUI

### ✅ **Project Versioning**
- Automatic versioning if project folders already exist
- `route_001_RGB_v2`, `route_001_RGB_v3`, etc.
- Prevents overwriting existing work

### ✅ **Enhanced Save System**
- Explicit chunk specification for reliable project saves
- Product verification after saving
- Fallback save mechanisms
### ✅ **Consistent Processing Parameters**
- Standardized quality settings across all scripts
- Medium quality depth maps (downscale=4)
- 0.1m point spacing for point clouds
- MildFiltering for depth maps

### ✅ **Multi-Camera System Support**
- Proper MS band grouping by timestamp
- Combined RGB+MS processing
- Multi-camera layout configuration

### ✅ **GCP Integration**
- XML marker import with pixel coordinates
- Separate GCP files for RGB and MS processing
- Automatic coordinate system handling (WGS84 → ETRS89)

## Processing Settings

### Camera Alignment
- **Quality**: Full resolution (downscale=1)
- **Preselection**: Generic and Reference enabled
- **Adaptive Fitting**: Disabled (as per workflow requirements)

### Depth Maps
- **Quality**: Medium (downscale=4)
- **Filtering**: MildFiltering
- **Max Neighbors**: 16

### Point Cloud
- **Source**: Depth maps
- **Point Colors**: Enabled
- **Point Spacing**: 0.1 meters
- **Uniform Sampling**: Enabled

### Coordinate Systems
- **Initial**: WGS84 (EPSG:4326) for image GPS data
- **Final**: ETRS89 (EPSG:4258) for output products

## Error Handling

### Automatic Recovery
- Fallback save mechanisms if primary save fails
- Continued processing if non-critical steps fail
- Detailed error reporting with context

### Validation
- Photo count verification after import
- Camera alignment ratio checking
- Product verification after final save
- GCP import validation

## Examples

### Using the GUI Tool (Recommended)

1. **Launch the GUI**:
   ```batch
   # Double-click start_config_tool_generic.bat
   # Or run from command line:
   start_config_tool_generic.bat
   ```

2. **Configure in GUI**:
   - Set script folder to your generic scripts location
   - Set DCIM folder to your drone data
   - Set GCP folder to your ground control points
   - Set output folder for results

3. **Generate Commands**:
   - Select RGB, MS, or Combined processing
   - Choose single or multiple route mode
   - Scan for routes and select the ones to process
   - Click "Generate Commands"
   - Copy each command to Metashape console one by one

### Direct Script Usage Examples

#### Single Route RGB Processing
```python
# Step 1: Import required modules (ALWAYS FIRST)
import os
import glob
import re
import Metashape

# Step 2: Load script
exec(open(r'C:\\scripts\\rgb_single_automation_generic.py',encoding='utf-8').read())

# Step 3: Configure paths
configure_paths(
    dcim=r'D:\\Drone_Data\\Project_Alpha\\DCIM',
    gcp=r'D:\\GCP_Files\\Project_Alpha',
    output=r'D:\\Processed\\Project_Alpha'
)

# Step 4: Process specific route
process_single_route_by_number('001')
```

#### Combined RGB+MS Processing
```python
# Step 1: Import required modules (ALWAYS FIRST)
import os
import glob
import re
import Metashape

# Step 2: Load script
exec(open(r'C:\\scripts\\rgb_ms_combined_automation_generic.py', encoding='utf-8').read())

# Step 3: Configure paths
configure_paths(
    dcim=r'D:\\Drone_Data\\Multispectral_Survey',
    gcp=r'D:\\GCP_Files\\Multispectral_Survey',
    output=r'D:\\Processed\\Multispectral_Survey'
)

# Step 4: Configure which routes to combine
configure_routes(['001', '002', '003'])

# Step 5: Run combined processing
run_combined_rgb_ms_automation()
```

#### Multiple Routes MS Processing
```python
# Step 1: Import required modules (ALWAYS FIRST)
import os
import glob
import re
import Metashape

# Step 2: Load script
exec(open(r'C:\\scripts\\ms_combined_automation_generic.py', encoding='utf-8').read())

# Step 3: Configure paths
configure_paths(
    dcim=r'D:\\Drone_Data\\Agriculture_Survey',
    gcp=r'D:\\GCP_Files\\Agriculture_Survey',
    output=r'D:\\Processed\\Agriculture_Survey'
)

# Step 4: Configure routes to combine
configure_routes(['001', '002', '003', '004'])

# Step 5: Run combined MS processing
run_combined_ms_automation()
```

## Testing Guide

### Pre-Flight Testing Checklist
Before running these scripts on production data, follow this testing protocol to ensure everything works correctly in your environment.

#### Step 1: Prepare Test Data
1. **Create a minimal test dataset**:
   - Select 1-2 routes with 10-20 images each
   - Copy to a dedicated test folder structure
   - Ensure you have corresponding GCP files

2. **Verify file naming conventions**:
   ```
   DJI_20240515120000_001_RouteTest/
   ├── DJI_20240515120001_0001_D.JPG        # RGB images
   ├── DJI_20240515120001_0001_MS_G.TIF     # MS Green
   ├── DJI_20240515120001_0001_MS_NIR.TIF   # MS NIR
   ├── DJI_20240515120001_0001_MS_R.TIF     # MS Red
   └── DJI_20240515120001_0001_MS_RE.TIF    # MS Red Edge
   ```

3. **Prepare test GCP files**:
   ```
   test_gcp/
   ├── gcp_route_001.xml           # For RGB and Combined processing
   └── gcp_route_001_MS.xml        # For MS processing (if different)
   ```

#### Step 2: Test Configuration Tool
```python
# Test 1: Launch GUI tool
# Double-click start_config_tool_generic.bat
# Expected: GUI opens without errors, all browse buttons work

# Test 2: Script folder configuration
# Use browse button to select folder containing automation scripts
# Expected: Script folder path updates correctly

# Test 3: Path configuration
# Set DCIM, GCP, and Output paths using browse buttons
# Expected: All paths update correctly in the interface
```

#### Step 3: Test Route Discovery
```python
# Test route scanning in GUI
# 1. Set DCIM path to test data
# 2. Select processing type (RGB/MS/Combined)
# 3. Click "Scan for Routes"
# Expected: Correctly identifies test routes and image counts

# Test in console (alternative)
# Step 1: Import required modules FIRST
import os
import glob
import re
import Metashape

# Step 2: Load and test script
exec(open(r'C:\\path\\to\\rgb_single_automation_generic.py', encoding='utf-8').read())
configure_paths(dcim=r'C:\\test\\DCIM', gcp=r'C:\\test\\GCP', output=r'C:\\test\\output')
available_routes = get_available_routes()
print("Available routes:", available_routes)
```

#### Step 4: Test Command Generation
```python
# Test GUI command generation
# 1. Configure all paths
# 2. Select processing type and route mode
# 3. Scan for routes and select test routes
# 4. Click "Generate Commands"
# Expected: Shows step-by-step commands ready for copying

# Test generated commands
# Copy each command to Metashape console one by one
# Expected: Each command executes without errors
```

#### Step 5: Test Single Route Processing
Start with the smallest, most controlled test:

```python
# Using GUI-generated commands (recommended):
# Copy these commands one by one to Metashape console:

# Command 1: Import required modules
import os
import glob
import re
import Metashape

# Command 2: Load script
exec(open(r'C:\\path\\to\\rgb_single_automation_generic.py', encoding='utf-8').read())

# Command 3: Configure paths
configure_paths(dcim=r'C:\\test\\DCIM', gcp=r'C:\\test\\GCP', output=r'C:\\test\\output')

# Command 4: Process route
process_single_route_by_number('001')

# Expected outcomes:
# - Project file created: test_output/route_001_RGB/route_001_RGB.psx
# - Processing report: test_output/route_001_RGB/processing_report_RGB.pdf
# - Console shows all processing steps without errors
# - Verification passes for all critical products
```

#### Step 6: Test Error Handling
Intentionally test error conditions:

```python
# Test 1: Invalid route number
process_single_route_by_number('999')
# Expected: Graceful error message, no crash

# Test 2: Missing GCP file (using GUI)
# Remove GCP files and try to generate commands
# Expected: GUI validation catches missing GCP files

# Test 3: Invalid paths (using GUI)
# Set paths to non-existent folders
# Expected: Browse buttons prevent invalid path selection

# Test 4: No routes found
# Point DCIM to empty folder and scan for routes
# Expected: GUI shows "no routes found" message
```

#### Step 7: Test Combined Processing
```python
# Test multiple route processing
# Step 1: Import modules
import os
import glob
import re
import Metashape

# Step 2: Load script
exec(open(r'C:\\path\\to\\rgb_combined_automation_generic.py',encoding='utf-8').read())

# Step 3: Configure
configure_paths(dcim=r'C:\\test\\DCIM',gcp=r'C:\\test\\GCP',output=r'C:\\test\\output')
configure_routes(['001', '002'])  # If you have multiple test routes

# Step 4: Run combined processing
run_combined_rgb_automation()

# Expected: Single project with multiple routes combined
```
#### Step 8: Verify Processing Results
After successful test processing:

1. **Check Project File**:
   ```python
   # Manually verify project file can be opened
   test_doc = Metashape.Document()
   test_doc.open(r'C:\path\to\test\output\route_001_RGB\route_001_RGB.psx')
   print(f"Cameras: {len(test_doc.chunks[0].cameras)}")
   print(f"Markers: {len(test_doc.chunks[0].markers)}")
   print(f"Point cloud: {test_doc.chunks[0].point_cloud.point_count if test_doc.chunks[0].point_cloud else 0}")
   ```

2. **Check Processing Report**:
   - Open the PDF report and verify it contains:
     - Camera alignment statistics
     - GCP accuracy information
     - Processing parameters used
     - Error/warning summaries

3. **Validate GCP Integration**:
   ```python
   # Check GCP import worked correctly
   chunk = test_doc.chunks[0]
   for marker in chunk.markers:
       projections = sum(1 for cam in chunk.cameras if marker.projections[cam])
       print(f"{marker.label}: {projections} projections, enabled: {marker.reference.enabled}")
   ```

#### Step 9: Test GUI Tool Completely
```python
# Test full GUI workflow:
# 1. Launch start_config_tool_generic.bat
# 2. Configure all paths using browse buttons
# 3. Test all processing types (RGB, MS, Combined)
# 4. Test both single and multiple route modes
# 5. Generate commands for each configuration
# 6. Test copy-to-clipboard functionality
# 7. Execute generated commands in Metashape console

# Expected: Complete workflow works without errors
```
#### Step 10: Performance Benchmarking
Record processing times for your test dataset:

```python
import time

start_time = time.time()
process_single_route_by_number('001')
end_time = time.time()

print(f"Processing time: {end_time - start_time:.1f} seconds")
```

### Testing Validation Criteria

#### ✅ **PASS Criteria**
- [ ] Configuration tool launches without errors
- [ ] All browse buttons work and update paths correctly
- [ ] Route scanning correctly identifies test routes with accurate counts
- [ ] Command generation produces valid Metashape console commands
- [ ] Single route processing completes without errors
- [ ] Combined route processing works with multiple routes
- [ ] Project files save correctly and can be reopened
- [ ] GCP import works with correct marker counts and projections
- [ ] Point cloud generation succeeds with reasonable point counts
- [ ] Processing reports generate successfully
- [ ] All processing types work (RGB, MS, Combined)
- [ ] Both single and multiple route modes function correctly
- [ ] Copy-to-clipboard functionality works in GUI
- [ ] Error handling works gracefully for invalid inputs

#### ❌ **FAIL Criteria**
- Configuration tool fails to launch or has interface errors
- Browse buttons don't work or paths don't update
- Route scanning finds no routes or reports wrong counts
- Command generation produces invalid or malformed commands
- Processing stops with unhandled exceptions
- Project files are corrupted or cannot be opened
- GCP import fails or markers have zero projections
- Point cloud generation fails completely
- GUI tool crashes or becomes unresponsive

### Common Issues and Solutions

#### Issue: "Configuration tool won't start"
- **Check**: Python path in `start_config_tool_generic.bat`
- **Solution**: Edit batch file with correct Python executable path

#### Issue: "No routes found" in GUI
- **Check**: DCIM folder structure matches expected DJI naming pattern
- **Solution**: Verify folder names like `DJI_YYYYMMDDHHMMSS_###_*`

#### Issue: "Script folder path invalid"
- **Check**: Script folder contains the automation scripts
- **Solution**: Browse to correct folder containing `*_automation_generic.py` files

#### Issue: "GCP file not found"
- **Check**: GCP XML files exist with correct naming in GCP folder
- **Solution**: Ensure files like `gcp_route_001.xml` exist

#### Issue: "Generated commands don't work in Metashape"
- **Check**: Commands copied completely and executed in correct order
- **Solution**: Copy each step individually, execute in sequence

#### Issue: "No cameras aligned"
- **Check**: Image quality, overlap, and GPS data
- **Solution**: Verify images have GPS data and sufficient overlap

#### Issue: Processing runs out of memory
- **Check**: Available RAM vs. image count and resolution
- **Solution**: Process smaller batches or reduce image resolution

#### Issue: "GUI interface looks broken"
- **Check**: Python tkinter installation
- **Solution**: Install/reinstall Python with tkinter support

### Test Environment Recommendations

1. **Minimum System Requirements**:
   - 16GB RAM for small test datasets
   - 50GB free disk space for test outputs
   - Metashape Professional 2.0+ with Python API
   - Python 3.6+ with tkinter support

2. **Test Data Size**:
   - Start with 10-20 images per route
   - Maximum 2-3 routes for initial testing
   - Use lower resolution images if available

3. **Expected Processing Times**:
   - RGB: ~2-5 minutes per 10 images (CPU dependent)
   - MS: ~5-10 minutes per 10 captures (4x images)
   - Combined: ~10-15 minutes per route

4. **GUI Tool Requirements**:
   - Python with tkinter (usually included)
   - Windows batch file support or equivalent shell
   - File system browse permissions

## Troubleshooting

### Configuration Tool Issues

**Tool won't launch:**
1. Check Python path in batch file
2. Verify Python installation includes tkinter
3. Try running from command line to see error messages

**Python not found error:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. Make sure "Add Python to PATH" was checked during installation
3. Try using full path to Python executable in batch file
4. Test Python installation: open Command Prompt, type `python --version`

**tkinter module not found:**
1. tkinter is usually included with Python - try reinstalling Python
2. On Linux: install python3-tk package (`sudo apt-get install python3-tk`)
3. On macOS: use Python from python.org rather than system Python

**Paths not updating:**
1. Check folder permissions
2. Ensure folders exist before browsing
3. Try typing paths manually instead of browsing

**Commands not generating:**
1. Verify all required fields are filled
2. Check that routes are selected in the list
3. Ensure script folder contains automation scripts

### Processing Issues

**Import errors in Metashape console:**
1. **Always run imports first**: Before loading any script, run the required imports:
   ```python
   import os
   import glob
   import re
   import Metashape
   ```
2. If imports fail, check that you're using Metashape Professional (not Standard)
3. Verify Metashape version supports Python API (1.6+ required)

**Script loading fails:**
1. Check file paths are correct and use forward slashes
2. Verify script files exist in specified location
3. Ensure Metashape Professional is being used

**Route processing fails:**
1. Check DCIM folder structure matches expected format
2. Verify GCP files exist for selected routes
3. Ensure sufficient disk space for outputs

**GCP import problems:**
1. Verify XML files have correct format with pixel coordinates
2. Check marker naming is consistent
3. Ensure coordinate system compatibility

## Tips for Best Results

1. **Use the GUI Tool**: The configuration tool provides the easiest and most reliable way to generate commands
2. **Organize Your Data**: Follow the expected folder structure for best results
3. **Check GCP Files**: Ensure GCP XML files exist for each route before processing
4. **Monitor Progress**: Watch console output for processing status and warnings
5. **Verify Results**: Check that project files open correctly and contain expected data
6. **Start Small**: Test with one route before processing large batches
7. **Keep Backups**: The scripts include versioning, but maintain your own backups of important data
8. **Test First**: Use the testing guide to validate everything works in your environment
9. **Read Reports**: Processing reports contain valuable quality metrics and error information
10. **Update Paths**: Always verify paths are correct before generating commands

## Version Compatibility

### Supported Software Versions
- **Metashape Professional 1.6+** (API compatibility)
- **Python 3.6+** (for script execution and GUI tool)
- **Windows 10+, macOS 10.14+, Linux** (cross-platform support)

### File Format Support
- **RGB Images**: JPG, JPEG (DJI naming convention)
- **Multispectral Images**: TIF, TIFF (DJI MS band naming)
- **GCP Files**: XML format with pixel coordinates
- **Output Formats**: PSX projects, PDF reports, standard export formats

### Integration
- **DJI Drone Compatibility**: Mavic 3 Multispectral, other DJI drones with similar naming
- **Workflow Integration**: Compatible with standard photogrammetry workflows
- **Export Compatibility**: Standard formats for GIS and CAD software