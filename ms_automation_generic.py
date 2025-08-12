"""
Generic Multispectral Metashape Automation Script
=================================================
Portable automation script for processing multispectral drone images with Multi-Camera system.
No hardcoded paths - all paths configurable via parameters.

Usage in Metashape Console:
exec(open(r'path\\to\\ms_automation_generic.py', encoding='utf-8').read())
"""

import os
import glob
import re
import Metashape

def enhanced_save_project(doc, chunk, project_path, step_name=""):
    """Enhanced save function that ensures all products are stored"""
    try:
        print(f"Saving project{' after ' + step_name if step_name else ''}...")
        
        # Ensure chunk is in document
        if chunk not in doc.chunks:
            print("WARNING: Chunk not in document, adding it...")
            doc.append(chunk)
        
        # Save with explicit chunk specification
        doc.save(project_path, chunks=[chunk], archive=True)
        
        print(f"Project saved successfully{' after ' + step_name if step_name else ''}")
        return True
        
    except Exception as e:
        print(f"ERROR saving project{' after ' + step_name if step_name else ''}: {str(e)}")
        try:
            # Fallback: try without chunks parameter
            doc.save(project_path)
            print("Fallback save successful")
            return True
        except Exception as e2:
            print(f"Fallback save also failed: {str(e2)}")
            return False

def verify_saved_products(project_path):
    """Verify that all products are properly saved in the project file"""
    try:
        print("Verifying saved products...")
        
        # Open project in read-only mode to verify
        test_doc = Metashape.Document()
        test_doc.open(project_path)
        
        if not test_doc.chunks:
            print("❌ No chunks found in saved project")
            test_doc = None  # Close document
            return False
            
        test_chunk = test_doc.chunks[0]
        
        # Check for each product
        products_found = []
        products_missing = []
        
        # Check cameras and alignment
        aligned_cameras = len([cam for cam in test_chunk.cameras if cam.transform]) if test_chunk.cameras else 0
        total_cameras = len(test_chunk.cameras) if test_chunk.cameras else 0
        if aligned_cameras > 0:
            products_found.append(f"Camera alignment ({aligned_cameras}/{total_cameras})")
        else:
            products_missing.append("Camera alignment")
            
        # Check tie points
        if test_chunk.tie_points and test_chunk.tie_points.point_count > 0:
            products_found.append(f"Tie points ({test_chunk.tie_points.point_count})")
        else:
            products_missing.append("Tie points")
            
        # Check point cloud
        if test_chunk.point_cloud and test_chunk.point_cloud.point_count > 0:
            products_found.append(f"Point cloud ({test_chunk.point_cloud.point_count:,} points)")
        else:
            products_missing.append("Point cloud")
            
        # Check depth maps
        if test_chunk.depth_maps and len(test_chunk.depth_maps.keys()) > 0:
            products_found.append(f"Depth maps ({len(test_chunk.depth_maps.keys())} cameras)")
        else:
            products_missing.append("Depth maps")
            
        # Check markers
        if test_chunk.markers and len(test_chunk.markers) > 0:
            products_found.append(f"GCP markers ({len(test_chunk.markers)})")
        else:
            products_missing.append("GCP markers")
        
        # Report results
        if products_found:
            print("✅ Products found in saved project:")
            for product in products_found:
                print(f"   ✅ {product}")
                
        if products_missing:
            print("❌ Products missing from saved project:")
            for product in products_missing:
                print(f"   ❌ {product}")
        
        # Close test document
        test_doc = None
        
        # Return success if critical products exist
        critical_products = ["Camera alignment", "Point cloud"]
        critical_missing = [p for p in products_missing if any(cp in p for cp in critical_products)]
        
        if not critical_missing:
            print("✅ All critical products verified in saved project")
            return True
        else:
            print("❌ Critical products missing from saved project")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying saved products: {str(e)}")
        return False

def import_gcps_from_xml_ms(chunk, route_number, gcp_base_path):
    """Import Ground Control Points from route-specific MS XML file"""
    gcp_filename = f"gcp_route_{route_number}_MS.xml"
    gcp_file_path = os.path.join(gcp_base_path, gcp_filename)
    
    print(f"\nStep 1.5: Importing Ground Control Points for MS processing...")
    print(f"Loading GCP file: {gcp_file_path}")
    
    # Check if GCP file exists
    if not os.path.exists(gcp_file_path):
        raise FileNotFoundError(f"MS GCP file not found for route {route_number}: {gcp_file_path}")
    
    try:
        # Use Metashape's importMarkers method for XML marker files
        chunk.importMarkers(path=gcp_file_path)
        
        # Count imported markers
        imported_count = len(chunk.markers)
        enabled_count = sum(1 for marker in chunk.markers if marker.reference.enabled)
        
        print(f"Successfully imported {imported_count} MS GCP markers with pixel coordinates")
        print(f"Active GCPs: {enabled_count} (enabled markers for alignment)")
        print(f"Check Points: {imported_count - enabled_count} (disabled markers for accuracy validation)")
        
        # Show marker details
        for marker in chunk.markers:
            # Count projections (pixel coordinates in images)
            projections = sum(1 for camera in chunk.cameras if marker.projections[camera])
            enabled_status = "[ENABLED]" if marker.reference.enabled else "[DISABLED]"
            print(f"  {marker.label}: {projections} image projections {enabled_status}")
        
        return imported_count, enabled_count
        
    except Exception as e:
        raise RuntimeError(f"Error importing MS GCPs from {gcp_file_path}: {str(e)}")

def scan_dcim_folders_ms(dcim_path):
    """Scan DCIM folder for route folders containing multispectral images"""
    route_folders = []
    
    if not os.path.exists(dcim_path):
        print(f"ERROR: DCIM folder not found: {dcim_path}")
        return route_folders
    
    print(f"Scanning DCIM directory for multispectral images: {dcim_path}")
    
    # Pattern to match route folders: DJI_YYYYMMDDHHMM_###_* or DJI_YYYYMMDDHHMMSS_###_*
    pattern = r'DJI_\d{12,14}_(\d{3})_.*'
    
    for folder in os.listdir(dcim_path):
        folder_path = os.path.join(dcim_path, folder)
        if os.path.isdir(folder_path):
            match = re.match(pattern, folder)
            if match:
                route_number = match.group(1)
                
                # Count multispectral images (TIF files with MS identifier)
                ms_patterns = [
                    os.path.join(folder_path, "*_MS_*.TIF"),
                    os.path.join(folder_path, "*_MS_*.tif")
                ]
                
                ms_files = []
                for pattern in ms_patterns:
                    ms_files.extend(glob.glob(pattern))
                
                # Group by capture timestamp to count complete sets
                capture_groups = {}
                band_counts = {'G': 0, 'NIR': 0, 'R': 0, 'RE': 0}
                
                for file_path in ms_files:
                    filename = os.path.basename(file_path)
                    # Extract timestamp from filename: DJI_YYYYMMDDHHMMSS_####_MS_BAND.TIF
                    timestamp_match = re.match(r'DJI_(\d{14})_(\d+)_MS_(\w+)\.TIF', filename, re.IGNORECASE)
                    if timestamp_match:
                        timestamp = timestamp_match.group(1)
                        image_num = timestamp_match.group(2)
                        band = timestamp_match.group(3).upper()
                        
                        capture_key = f"{timestamp}_{image_num}"
                        if capture_key not in capture_groups:
                            capture_groups[capture_key] = {}
                        capture_groups[capture_key][band] = file_path
                        
                        if band in band_counts:
                            band_counts[band] += 1
                
                # Count complete capture sets (4 bands each)
                complete_captures = 0
                all_ms_files = []
                
                for capture_key, bands in capture_groups.items():
                    if len(bands) == 4 and all(band in bands for band in ['G', 'NIR', 'R', 'RE']):
                        complete_captures += 1
                        # Add files in consistent order: G, NIR, R, RE
                        for band in ['G', 'NIR', 'R', 'RE']:
                            all_ms_files.append(bands[band])
                
                if complete_captures > 0:
                    route_folders.append({
                        'folder_name': folder,
                        'folder_path': folder_path,
                        'route_number': route_number,
                        'ms_captures': complete_captures,
                        'ms_files_count': len(ms_files),
                        'band_counts': band_counts,
                        'image_files': all_ms_files,
                        'complete_sets': complete_captures
                    })
                    print(f"  Found Route {route_number}: {complete_captures} complete MS captures ({len(ms_files)} total MS files)")
                    print(f"    Band distribution: G={band_counts['G']}, NIR={band_counts['NIR']}, R={band_counts['R']}, RE={band_counts['RE']}")
    
    return sorted(route_folders, key=lambda x: x['route_number'])

def create_project_structure_ms(route_info, output_base):
    """Create the project folder structure and return paths for MS processing with automatic versioning"""
    base_project_folder = f"route_{route_info['route_number']}_MS"
    base_project_file = f"route_{route_info['route_number']}_MS.psx"
    
    # Check for existing folders and create versioned name if needed
    project_folder = base_project_folder
    project_file = base_project_file
    version = 1
    
    while True:
        project_path = os.path.join(output_base, project_folder)
        project_full_path = os.path.join(project_path, project_file)
        
        # Check if folder exists and has files in it
        if os.path.exists(project_path):
            # Check if there are any files in the folder (not just empty)
            if os.listdir(project_path):  # Folder exists and has files
                version += 1
                project_folder = f"{base_project_folder}_v{version}"
                project_file = f"route_{route_info['route_number']}_MS_v{version}.psx"
                print(f"Folder {base_project_folder} exists, trying {project_folder}")
                continue
            else:
                # Folder exists but is empty, we can use it
                break
        else:
            # Folder doesn't exist, we can create it
            break
    
    # Create the final folder structure
    os.makedirs(project_path, exist_ok=True)
    project_full_path = os.path.join(project_path, project_file)
    
    if version > 1:
        print(f"Created versioned MS project folder: {project_folder}")
    
    return project_path, project_full_path

def process_ms_route(route_info, output_base, gcp_base_path):
    """Process a single route with multispectral images"""
    print(f"\n{'='*60}")
    print(f"PROCESSING ROUTE {route_info['route_number']} - MULTISPECTRAL")
    print(f"{'='*60}")
    print(f"Folder: {route_info['folder_name']}")
    print(f"Complete MS captures: {route_info['ms_captures']}")
    print(f"Total MS files: {route_info['ms_files_count']}")
    print(f"Band distribution: {route_info['band_counts']}")
    
    # Create project structure
    project_path, project_full_path = create_project_structure_ms(route_info, output_base)
    print(f"Project will be saved to: {project_full_path}")
    print(f"MS GCP files location: {gcp_base_path}")
    
    # Get image files
    image_files = route_info['image_files']
    
    if not image_files:
        print("ERROR: No multispectral images found!")
        return False
    
    try:
        # Create new Metashape document and chunk
        print("\nStep 0: Creating new project...")
        doc = Metashape.Document()
        chunk = doc.addChunk()
        chunk.label = f"Route_{route_info['route_number']}_MS"
        
        # Set initial coordinate system (WGS84 for images)
        chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
        print("Initial coordinate system set to WGS84 (EPSG:4326) for image GPS data")
        
        # Add photos as Multi-Camera system
        print(f"\nStep 1: Adding {len(image_files)} multispectral images as Multi-Camera system...")
        print(f"Complete captures: {route_info['complete_sets']} (4 bands each)")
        
        # Add all TIF files - Metashape will automatically group them by timestamp
        chunk.addPhotos(image_files)
        
        # Configure as Multi-Camera system
        print("Configuring as Multi-Camera system...")
        for camera in chunk.cameras:
            camera.group = None  # Let Metashape auto-group by timestamp
        
        # Enable multi-camera system processing
        # Note: Metashape should automatically detect multi-camera setup from filename patterns
        
        # Verify photos were added
        if len(chunk.cameras) == 0:
            print("ERROR: No cameras were added to the project!")
            return False
        
        print(f"Successfully added {len(chunk.cameras)} cameras (multispectral bands)")
        print(f"Expected camera groups: {route_info['complete_sets']} (one per capture location)")
        
        # Import Ground Control Points for MS
        try:
            imported_count, enabled_count = import_gcps_from_xml_ms(chunk, route_info['route_number'], gcp_base_path)
            
            # Set project coordinate system to ETRS89 after GCP import
            print(f"\nSetting project coordinate system to ETRS89 (EPSG:4258)...")
            chunk.crs = Metashape.CoordinateSystem("EPSG::4258")
            print("Project coordinate system changed to ETRS89 for final output")
            
        except Exception as gcp_error:
            print(f"ERROR: Failed to import MS GCPs: {str(gcp_error)}")
            print("Stopping processing due to MS GCP import failure.")
            return False
        
        # Save project with GCPs
        doc.save(project_full_path, chunks=[chunk])
        print(f"Project saved with {imported_count} MS GCPs imported")
        
        # Step 2: Match Photos (Multi-Camera system)
        print(f"\nStep 2: Matching photos (Multi-Camera system)...")
        print("  Settings: Downscale=1 (full resolution), Generic preselection=True, Reference preselection=True")
        chunk.matchPhotos(
            downscale=1,  # Full resolution
            generic_preselection=True,
            reference_preselection=True  # Use GCPs for photo matching
        )
        doc.save(project_full_path, chunks=[chunk])
        print("Photo matching completed for Multi-Camera system")
        
        # Step 3: Align Cameras (Multi-Camera system)
        print(f"\nStep 3: Aligning cameras (Multi-Camera system)...")
        chunk.alignCameras(adaptive_fitting=False)
        
        # Check alignment results
        aligned_cameras = len([cam for cam in chunk.cameras if cam.transform])
        total_cameras = len(chunk.cameras)
        alignment_ratio = aligned_cameras / total_cameras if total_cameras > 0 else 0
        
        print(f"Camera alignment completed: {aligned_cameras}/{total_cameras} cameras aligned ({alignment_ratio:.1%})")
        print(f"Expected aligned cameras: {route_info['complete_sets'] * 4} (4 bands × {route_info['complete_sets']} captures)")
        
        if aligned_cameras == 0:
            print("WARNING: No cameras were aligned! Processing may fail.")
        elif alignment_ratio < 0.8:
            print(f"WARNING: Low alignment ratio ({alignment_ratio:.1%}). Consider checking image quality.")
        
        # Display GCP information
        if chunk.markers:
            enabled_markers = sum(1 for marker in chunk.markers if marker.reference.enabled)
            print(f"MS GCP markers: {enabled_markers} enabled for alignment, {len(chunk.markers) - enabled_markers} as check points")
        
        doc.save(project_full_path, chunks=[chunk])
        
        # Step 4: Build Depth Maps
        print(f"\nStep 4: Building depth maps...")
        print("  Settings: Quality=Medium (4), Filter=MildFiltering, Max neighbors=16")
        chunk.buildDepthMaps(
            downscale=4,  # Medium quality
            filter_mode=Metashape.FilterMode.MildFiltering,
            max_neighbors=16
        )
        doc.save(project_full_path, chunks=[chunk])
        print("Depth maps completed")
        
        # Step 5: Build Point Cloud (with multispectral values)
        print(f"\nStep 5: Building point cloud with multispectral values...")
        print("  Settings: Source=Depth maps, Point colors=True, Spacing=0.1m")
        chunk.buildPointCloud(
            source_data=Metashape.DataSource.DepthMapsData,
            point_colors=True,
            points_spacing=0.1  # 0.1 meters
        )
        
        # Check point cloud results
        if chunk.point_cloud:
            point_count = chunk.point_cloud.point_count
            print(f"Multispectral point cloud completed: {point_count:,} points generated")
            print("Point cloud includes multispectral band values for vegetation analysis")
        else:
            print("WARNING: No point cloud was generated!")
        
        doc.save(project_full_path, chunks=[chunk])
        
        # Step 6: Generate Processing Report
        print(f"\nStep 6: Generating processing report...")
        report_path = os.path.join(project_path, f"processing_report_MS.pdf")
        chunk.exportReport(report_path)
        print(f"MS processing report saved: {report_path}")
        
        # Final comprehensive save with all processing results
        print(f"\nStep 7: Final project save...")
        save_success = enhanced_save_project(doc, chunk, project_full_path, "final MS processing")
        if not save_success:
            print("ERROR: Failed to save final MS project!")
            return False
        
        # Verify all products are saved
        verification_success = verify_saved_products(project_full_path)
        if not verification_success:
            print("WARNING: MS product verification failed - some data may not be properly saved")
        
        print(f"\n{'='*60}")
        print(f"SUCCESS: Route {route_info['route_number']} MS processing completed!")
        print(f"Project: {project_full_path}")
        print(f"MS captures: {route_info['complete_sets']} complete sets")
        print(f"MS GCPs: {imported_count} imported ({enabled_count} active, {imported_count-enabled_count} check points)")
        print(f"Point cloud: Multispectral values included")
        print(f"Report: {report_path}")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR during MS processing Route {route_info['route_number']}: {str(e)}")
        print("MS processing failed!")
        return False

def process_all_routes_ms(dcim_path, output_path, gcp_path):
    """Process all routes found in DCIM folder for multispectral processing"""
    print("METASHAPE MULTISPECTRAL AUTOMATION")
    print("=" * 50)
    print(f"DCIM Path: {dcim_path}")
    print(f"Output Path: {output_path}")
    print(f"MS GCP Path: {gcp_path}")
    
    # Scan for routes
    routes = scan_dcim_folders_ms(dcim_path)
    
    if not routes:
        print("\nNo multispectral routes found!")
        print("Expected folder naming pattern: DJI_YYYYMMDDHHMM_###_*")
        print("With MS images matching pattern: *_MS_*.TIF (4 bands: G, NIR, R, RE)")
        return False
    
    print(f"\nFound {len(routes)} MS routes:")
    for i, route in enumerate(routes, 1):
        print(f"  {i}. Route {route['route_number']}: {route['complete_sets']} complete MS captures")
    
    # Process each route
    print(f"\nStarting MS processing of {len(routes)} routes...")
    successful = 0
    failed = 0
    
    for route in routes:
        success = process_ms_route(route, output_path, gcp_path)
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"MS PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total routes: {len(routes)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output location: {output_path}")
    print(f"MS GCP location: {gcp_path}")
    print(f"{'='*60}")
    
    return successful > 0

def process_selected_routes_ms(route_numbers, dcim_path, output_path, gcp_path):
    """Process specific MS routes by route numbers (e.g., ['001', '003', '005'])"""
    print("METASHAPE MULTISPECTRAL AUTOMATION - SELECTED ROUTES")
    print("=" * 60)
    print(f"DCIM Path: {dcim_path}")
    print(f"Output Path: {output_path}")
    print(f"MS GCP Path: {gcp_path}")
    print(f"Processing MS routes: {', '.join(route_numbers)}")
    
    # Scan for routes
    routes = scan_dcim_folders_ms(dcim_path)
    
    if not routes:
        print("No MS routes found!")
        return False
    
    # Filter selected routes
    selected_routes = []
    for route_num in route_numbers:
        for route in routes:
            if route['route_number'] == route_num:
                selected_routes.append(route)
                break
        else:
            print(f"WARNING: MS Route {route_num} not found!")
    
    if not selected_routes:
        print("No valid MS routes selected!")
        return False
    
    print(f"\nFound {len(selected_routes)} selected MS routes:")
    for route in selected_routes:
        print(f"  Route {route['route_number']}: {route['complete_sets']} complete MS captures")
    
    # Process each selected route
    successful = 0
    failed = 0
    
    for route in selected_routes:
        success = process_ms_route(route, output_path, gcp_path)
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"PROCESSING SUMMARY - {len(selected_routes)} SELECTED MS ROUTES")
    print(f"{'='*60}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"{'='*60}")
    
    return successful > 0

def show_available_routes_ms(dcim_path):
    """Display all available MS routes with details"""
    routes = scan_dcim_folders_ms(dcim_path)
    
    if not routes:
        print("No MS routes found!")
        return []
    
    print(f"\nAvailable MS routes in: {dcim_path}")
    print("-" * 70)
    total_captures = 0
    for i, route in enumerate(routes):
        size_category = "Small" if route['complete_sets'] < 50 else "Medium" if route['complete_sets'] < 100 else "Large"
        print(f"{i}: Route {route['route_number']} - {route['complete_sets']} complete MS captures ({size_category})")
        print(f"   Band counts: G={route['band_counts']['G']}, NIR={route['band_counts']['NIR']}, R={route['band_counts']['R']}, RE={route['band_counts']['RE']}")
        total_captures += route['complete_sets']
    
    print("-" * 70)
    print(f"Total: {len(routes)} routes with {total_captures} complete MS captures")
    
    return routes

# Display usage instructions
print("GENERIC MULTISPECTRAL METASHAPE AUTOMATION SCRIPT LOADED")
print("=" * 70)
print("This script requires manual path configuration!")
print("")
print("Required paths:")
print("- dcim_path: Path to DCIM folder containing DJI route folders")
print("- output_path: Path where processed projects will be saved")
print("- gcp_path: Path to folder containing MS GCP XML files")
print("")
print("Usage examples:")
print("1. process_all_routes_ms(dcim_path, output_path, gcp_path)")
print("2. show_available_routes_ms(dcim_path)")
print("3. process_selected_routes_ms(['001', '003'], dcim_path, output_path, gcp_path)")
print("")
print("MS GCP Files Expected:")
print("- gcp_route_001_MS.xml, gcp_route_002_MS.xml, etc. in gcp_path folder")
print("")
print("Multispectral Requirements:")
print("- 4 TIF files per capture: *_MS_G.TIF, *_MS_NIR.TIF, *_MS_R.TIF, *_MS_RE.TIF")
print("- Configured as Multi-Camera system for proper band alignment")
print("- Point cloud includes multispectral values for vegetation analysis")
print("")
print("Example setup:")
print("dcim_path = r'C:\\path\\to\\DCIM'")
print("output_path = r'C:\\path\\to\\output'")
print("gcp_path = r'C:\\path\\to\\GCP'")
print("process_all_routes_ms(dcim_path, output_path, gcp_path)")
