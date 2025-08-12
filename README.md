# Generic Metashape Automation Scripts

This folder contains portable, generic versions of the Metashape automation scripts with no hardcoded file paths. These scripts can be used in any project by simply configuring the required paths.

**Originally developed for DJI Mavic 3 Multispectral (M3M) drone data processing**, these scripts support both RGB and multispectral workflows for professional photogrammetry projects.

## Scripts Overview

### 1. `rgb_automation_generic.py`
- **Purpose**: Process RGB-only drone images
- **Input**: JPG files with 'D' identifier (e.g., DJI_20240515120000_0001_D.JPG)
- **Output**: Camera alignment, depth maps, point cloud, processing report
- **GCP Files**: `gcp_route_001.xml`, `gcp_route_002.xml`, etc.
- **M3M Support**: Optimized for DJI Mavic 3 Multispectral RGB sensor

### 2. `ms_automation_generic.py`
- **Purpose**: Process multispectral drone images as Multi-Camera system
- **Input**: TIF files with MS band identifiers (G, NIR, R, RE)
- **Output**: Multispectral point cloud with band values for vegetation analysis
- **GCP Files**: `gcp_route_001_MS.xml`, `gcp_route_002_MS.xml`, etc.
- **M3M Support**: Native support for M3M's 4-band multispectral sensor array

### 3. `combined_automation_generic.py`
- **Purpose**: Process RGB and MS images together in combined Multi-Camera system
- **Input**: Both RGB (JPG) and MS (TIF) files
- **Output**: Full pipeline including mesh, texture, DEM, orthomosaic exports
- **GCP Files**: `gcp_route_001.xml`, `gcp_route_002.xml`, etc.
- **M3M Support**: Leverages M3M's synchronized RGB and multispectral capture capabilities

## Usage Instructions

### Step 1: Load Script in Metashape
```python
# In Metashape Console
exec(open(r'C:\\path\\to\\script\\rgb_automation_generic.py', encoding='utf-8').read())
```

### Step 2: Configure Paths
```python
# Set your project paths
dcim_path = r'C:\\path\\to\\DCIM\\folder'        # Contains DJI route folders
output_path = r'C:\\path\\to\\output\\folder'    # Where projects will be saved
gcp_path = r'C:\\path\\to\\GCP\\folder'          # Contains XML GCP files
```

### Step 3: Run Processing
```python
# Process all routes
process_all_routes(dcim_path, output_path, gcp_path)              # RGB
process_all_routes_ms(dcim_path, output_path, gcp_path)           # MS
process_combined_routes(dcim_path, output_path, gcp_path)         # Combined

# Process selected routes only
process_selected_routes(['001', '003'], dcim_path, output_path, gcp_path)
process_selected_routes_ms(['001', '003'], dcim_path, output_path, gcp_path)

# Show available routes first
show_available_routes(dcim_path)                                  # RGB
show_available_routes_ms(dcim_path)                              # MS
show_available_combined_routes(dcim_path)                        # Combined
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
├── route_001_RGB/              # RGB processing results
│   ├── route_001_RGB.psx       # Metashape project file
│   └── processing_report_RGB.pdf
├── route_001_MS/               # MS processing results
│   ├── route_001_MS.psx        # Metashape project file
│   └── processing_report_MS.pdf
└── route_001_Combined/         # Combined processing results
    ├── route_001_combined.psx  # Metashape project file
    ├── orthomosaic/            # Exported orthomosaic
    ├── dem/                    # Exported DEM
    ├── pointcloud/             # Exported point cloud
    └── report/                 # Processing report
```

## Key Features

### ✅ **Portability**
- No hardcoded paths
- Works on any system with proper path configuration
- All paths configurable via function parameters

### ✅ **Project Versioning**
- Automatic versioning if project folders already exist
- `route_001_RGB_v2`, `route_001_RGB_v3`, etc.
- Prevents overwriting existing work

### ✅ **Enhanced Save System**
- Explicit chunk specification for reliable project saves
- Product verification after saving
- Fallback save mechanisms

### ✅ **Flexible Route Selection**
- Process all routes: `process_all_routes()`
- Process selected routes: `process_selected_routes(['001', '003'])`
- Process single route: `process_single_route_by_number('001')`
- Show available routes: `show_available_routes()`

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

### Basic RGB Processing
```python
# Load script
exec(open(r'C:\\scripts\\rgb_automation_generic.py', encoding='utf-8').read())

# Configure paths
dcim_path = r'D:\\Drone_Data\\Project_Alpha\\DCIM'
output_path = r'D:\\Processed\\Project_Alpha'
gcp_path = r'D:\\GCP_Files\\Project_Alpha'

# See what's available
show_available_routes(dcim_path)

# Process specific routes
process_selected_routes(['001', '003', '005'], dcim_path, output_path, gcp_path)
```

### Combined RGB+MS Processing
```python
# Load script
exec(open(r'C:\\scripts\\combined_automation_generic.py', encoding='utf-8').read())

# Configure paths
dcim_path = r'D:\\Drone_Data\\Multispectral_Survey'
output_path = r'D:\\Processed\\Multispectral_Survey'
gcp_path = r'D:\\GCP_Files\\Multispectral_Survey'

# Full processing with exports
process_combined_routes(dcim_path, output_path, gcp_path)
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

#### Step 2: Test Script Loading
```python
# Test 1: Load RGB script
exec(open(r'C:\\path\\to\\rgb_automation_generic.py', encoding='utf-8').read())
# Expected: Script loads without errors, shows usage instructions

# Test 2: Load MS script  
exec(open(r'C:\\path\\to\\ms_automation_generic.py', encoding='utf-8').read())
# Expected: Script loads without errors, shows MS-specific instructions

# Test 3: Load Combined script
exec(open(r'C:\\path\\to\\combined_automation_generic.py', encoding='utf-8').read())
# Expected: Script loads without errors, shows combined processing instructions
```

#### Step 3: Test Route Discovery
```python
# Configure test paths
test_dcim = r'C:\\path\\to\\test\\DCIM'
test_output = r'C:\\path\\to\\test\\output'
test_gcp = r'C:\\path\\to\\test\\GCP'

# Test route scanning
show_available_routes(test_dcim)                    # RGB routes
show_available_routes_ms(test_dcim)                 # MS routes  
show_available_combined_routes(test_dcim)           # Combined routes

# Expected: Correctly identifies test routes and image counts
```

#### Step 4: Test Single Route Processing
Start with the smallest, most controlled test:

```python
# Test RGB processing on one route
success = process_single_route_by_number('001', test_dcim, test_output, test_gcp)
print(f"RGB Test Result: {'PASSED' if success else 'FAILED'}")

# Expected outcomes:
# - Project file created: test_output/route_001_RGB/route_001_RGB.psx
# - Processing report: test_output/route_001_RGB/processing_report_RGB.pdf
# - Console shows all processing steps without errors
# - Verification passes for all critical products
```

#### Step 5: Test Error Handling
Intentionally test error conditions:

```python
# Test 1: Missing GCP file
process_single_route_by_number('999', test_dcim, test_output, test_gcp)
# Expected: Graceful error message, no crash

# Test 2: Invalid DCIM path
show_available_routes(r'C:\\nonexistent\\path')
# Expected: Error message about folder not found

# Test 3: Invalid output path (read-only)
# Try processing with output path set to read-only folder
# Expected: Graceful error handling with fallback options
```

#### Step 6: Verify Processing Results
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

#### Step 7: Performance Benchmarking
Record processing times for your test dataset:

```python
import time

start_time = time.time()
process_single_route_by_number('001', test_dcim, test_output, test_gcp)
end_time = time.time()

print(f"Processing time: {end_time - start_time:.1f} seconds")
print(f"Images processed: {image_count}")
print(f"Time per image: {(end_time - start_time) / image_count:.2f} seconds")
```

#### Step 8: Test Batch Processing
Once single route processing works:

```python
# Test selected routes processing
process_selected_routes(['001'], test_dcim, test_output, test_gcp)

# Test full batch processing (if you have multiple test routes)
process_all_routes(test_dcim, test_output, test_gcp)
```

### Testing Validation Criteria

#### ✅ **PASS Criteria**
- [ ] All scripts load without import errors
- [ ] Route discovery correctly identifies test routes
- [ ] Single route processing completes without errors
- [ ] Project files save correctly and can be reopened
- [ ] GCP import works with correct marker counts
- [ ] Point cloud generation succeeds with reasonable point counts
- [ ] Processing reports generate successfully
- [ ] Verification functions pass for all critical products
- [ ] Error handling works gracefully for invalid inputs

#### ❌ **FAIL Criteria**
- Script loading fails with import errors
- Route discovery finds no routes or wrong counts
- Processing stops with unhandled exceptions
- Project files are corrupted or cannot be opened
- GCP import fails or markers have zero projections
- Point cloud generation fails completely
- Verification functions report missing critical products

### Common Issues and Solutions

#### Issue: "No routes found"
- **Check**: DCIM folder structure matches expected DJI naming pattern
- **Solution**: Verify folder names like `DJI_YYYYMMDDHHMMSS_###_*`

#### Issue: "GCP file not found"
- **Check**: GCP XML files exist with correct naming
- **Solution**: Ensure files like `gcp_route_001.xml` exist in GCP folder

#### Issue: "No cameras aligned"
- **Check**: Image quality and overlap
- **Solution**: Verify images have GPS data and sufficient overlap

#### Issue: Processing runs out of memory
- **Check**: Available RAM vs. image count and resolution
- **Solution**: Process smaller batches or reduce image resolution

#### Issue: Verification fails
- **Check**: Metashape API version compatibility
- **Solution**: Update Metashape or check API documentation

### Test Environment Recommendations

1. **Minimum System Requirements**:
   - 16GB RAM for small test datasets
   - 50GB free disk space for test outputs
   - Metashape Professional 2.0+ with Python API

2. **Test Data Size**:
   - Start with 10-20 images per route
   - Maximum 2-3 routes for initial testing
   - Use lower resolution images if available

3. **Expected Processing Times**:
   - RGB: ~2-5 minutes per 10 images (CPU dependent)
   - MS: ~5-10 minutes per 10 captures (4x images)
   - Combined: ~10-15 minutes per route

## Tips for Best Results

1. **Organize Your Data**: Follow the expected folder structure for best results
2. **Check GCP Files**: Ensure GCP XML files exist for each route before processing
3. **Monitor Progress**: Watch console output for processing status and warnings
4. **Verify Results**: Use the built-in verification functions to check saved products
5. **Start Small**: Test with one route before processing large batches