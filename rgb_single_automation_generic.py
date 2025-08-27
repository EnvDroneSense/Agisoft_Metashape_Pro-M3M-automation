"""
Generic RGB-Only Metashape Automation Script
============================================
Portable automation script for processing RGB drone images only.
No hardcoded paths - all paths configurable via parameters.

Usage in Metashape Console:
exec(open(r'path\\to\\rgb_automation_generic.py', encoding='utf-8').read())
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

def import_gcps_from_xml(chunk, route_number, gcp_base_path):
    """Import Ground Control Points from route-specific XML file"""
    gcp_filename = f"gcp_route_{route_number}.xml"
    gcp_file_path = os.path.join(gcp_base_path, gcp_filename)
    
    print(f"\nStep 1.5: Importing Ground Control Points...")
    print(f"Loading GCP file: {gcp_file_path}")
    
    # Check if GCP file exists
    if not os.path.exists(gcp_file_path):
        raise FileNotFoundError(f"GCP file not found for route {route_number}: {gcp_file_path}")
    
    try:
        # Use Metashape's importMarkers method for XML marker files
        chunk.importMarkers(path=gcp_file_path)
        
        # Count imported markers
        imported_count = len(chunk.markers)
        enabled_count = sum(1 for marker in chunk.markers if marker.reference.enabled)
        
        print(f"Successfully imported {imported_count} GCP markers with pixel coordinates")
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
        raise RuntimeError(f"Error importing GCPs from {gcp_file_path}: {str(e)}")

def scan_dcim_folders(dcim_path):
    """Scan DCIM folder for route folders containing RGB images"""
    route_folders = []
    
    if not os.path.exists(dcim_path):
        print(f"ERROR: DCIM folder not found: {dcim_path}")
        return route_folders
    
    print(f"Scanning DCIM directory: {dcim_path}")
    
    # Pattern to match route folders: DJI_YYYYMMDDHHMM_###_* or DJI_YYYYMMDDHHMMSS_###_*
    pattern = r'DJI_\d{12,14}_(\d{3})_.*'
    
    for folder in os.listdir(dcim_path):
        folder_path = os.path.join(dcim_path, folder)
        if os.path.isdir(folder_path):
            match = re.match(pattern, folder)
            if match:
                route_number = match.group(1)
                
                # Count RGB images (JPG files with 'D' identifier)
                rgb_pattern = os.path.join(folder_path, "*_D.JPG")
                rgb_files = glob.glob(rgb_pattern)
                
                # Also try without underscore before D (in case naming varies)
                if not rgb_files:
                    rgb_pattern_alt = os.path.join(folder_path, "*D.JPG")
                    rgb_files = glob.glob(rgb_pattern_alt)
                
                # Count all JPG files as backup
                if not rgb_files:
                    all_jpg = glob.glob(os.path.join(folder_path, "*.JPG"))
                    all_jpg.extend(glob.glob(os.path.join(folder_path, "*.jpg")))
                    rgb_files = all_jpg
                
                if rgb_files:
                    route_folders.append({
                        'folder_name': folder,
                        'folder_path': folder_path,
                        'route_number': route_number,
                        'rgb_count': len(rgb_files),
                        'image_files': rgb_files
                    })
                    print(f"  Found Route {route_number}: {len(rgb_files)} RGB images")
    
    return sorted(route_folders, key=lambda x: x['route_number'])

def create_project_structure(route_info, output_base):
    """Create the project folder structure and return paths with automatic versioning"""
    base_project_folder = f"route_{route_info['route_number']}_RGB"
    base_project_file = f"route_{route_info['route_number']}_RGB.psx"
    
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
                project_file = f"route_{route_info['route_number']}_RGB_v{version}.psx"
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
        print(f"Created versioned project folder: {project_folder}")
    
    return project_path, project_full_path

def process_rgb_route(route_info, output_base, gcp_base_path):
    """Process a single route with RGB images only"""
    print(f"\n{'='*60}")
    print(f"PROCESSING ROUTE {route_info['route_number']} - RGB ONLY")
    print(f"{'='*60}")
    print(f"Folder: {route_info['folder_name']}")
    print(f"Images: {route_info['rgb_count']} RGB files")
    
    # Create project structure
    project_path, project_full_path = create_project_structure(route_info, output_base)
    print(f"Project will be saved to: {project_full_path}")
    print(f"GCP files location: {gcp_base_path}")
    
    # Get image files
    image_files = route_info['image_files']
    
    if not image_files:
        print("ERROR: No RGB images found!")
        return False
    
    try:
        # Create new Metashape document and chunk
        print("\nStep 0: Creating new project...")
        doc = Metashape.Document()
        chunk = doc.addChunk()
        chunk.label = f"Route_{route_info['route_number']}_RGB"
        
        # Set initial coordinate system (WGS84 for images)
        chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
        print("Initial coordinate system set to WGS84 (EPSG:4326) for image GPS data")
        
        # Add photos
        print(f"\nStep 1: Adding {len(image_files)} RGB images...")
        chunk.addPhotos(image_files)
        
        # Verify photos were added
        if len(chunk.cameras) == 0:
            print("ERROR: No cameras were added to the project!")
            return False
        
        print(f"Successfully added {len(chunk.cameras)} cameras")
        
        # Import Ground Control Points
        try:
            imported_count, enabled_count = import_gcps_from_xml(chunk, route_info['route_number'], gcp_base_path)
            
            # Set project coordinate system to ETRS89 after GCP import
            print(f"\nSetting project coordinate system to ETRS89 (EPSG:4258)...")
            chunk.crs = Metashape.CoordinateSystem("EPSG::4258")
            print("Project coordinate system changed to ETRS89 for final output")
            
        except Exception as gcp_error:
            print(f"ERROR: Failed to import GCPs: {str(gcp_error)}")
            print("Stopping processing due to GCP import failure.")
            return False
        
        # Save project with GCPs
        doc.save(project_full_path, chunks=[chunk])
        print(f"Project saved with {imported_count} GCPs imported")
        
        # Step 2: Match Photos
        print(f"\nStep 2: Matching photos...")
        print("  Settings: Downscale=1 (full resolution), Generic preselection=True, Reference preselection=True")
        
        chunk.matchPhotos(
            downscale=1,  # Full resolution
            generic_preselection=True,
            reference_preselection=True  # Use GCPs for photo matching
        )
        
        # Verify photo matching results before saving
        tie_points = chunk.point_cloud.point_count if chunk.point_cloud else 0
        print(f"Photo matching completed: {tie_points} tie points found")
        
        if tie_points == 0:
            print("WARNING: No tie points found! Photo matching may have failed.")
        
        # Force save after photo matching
        print("Saving project after photo matching...")
        doc.save(project_full_path, chunks=[chunk])
        print("Photo matching results saved successfully")
        
        # Step 3: Align Cameras
        print(f"\nStep 3: Aligning cameras...")
        chunk.alignCameras(adaptive_fitting=False)
        
        # Check alignment results
        aligned_cameras = len([cam for cam in chunk.cameras if cam.transform])
        total_cameras = len(chunk.cameras)
        alignment_ratio = aligned_cameras / total_cameras if total_cameras > 0 else 0
        
        print(f"Camera alignment completed: {aligned_cameras}/{total_cameras} cameras aligned ({alignment_ratio:.1%})")
        
        if aligned_cameras == 0:
            print("ERROR: No cameras aligned! Cannot proceed with processing.")
            doc.save(project_full_path, chunks=[chunk])  # Save the failed state for debugging
            return False
        
        # Save after successful camera alignment
        print("Saving project after camera alignment...")
        doc.save(project_full_path, chunks=[chunk])
        print("Camera alignment results saved successfully")
        
        # Display GCP information
        if chunk.markers:
            enabled_markers = sum(1 for marker in chunk.markers if marker.reference.enabled)
            print(f"GCP markers: {enabled_markers} enabled for alignment, {len(chunk.markers) - enabled_markers} as check points")
        
        # Step 4: Build Depth Maps
        print(f"\nStep 4: Building depth maps...")
        print("  Settings: Quality=Medium (4), Filter=MildFiltering, Max neighbors=16")
        chunk.buildDepthMaps(
            downscale=4,  # Medium quality
            filter_mode=Metashape.FilterMode.MildFiltering,
            max_neighbors=16
        )
        
        # Force save after depth maps
        print("Saving project after depth maps...")
        doc.save(project_full_path, chunks=[chunk])
        print("Depth maps completed and saved successfully")
        
        # Step 5: Build Point Cloud
        print(f"\nStep 5: Building point cloud...")
        print("  Settings: Source=Depth maps, Point colors=True, Spacing=0.1m")
        chunk.buildPointCloud(
            source_data=Metashape.DataSource.DepthMapsData,
            point_colors=True,
            points_spacing=0.1  # 0.1 meters
        )
        
        # Check point cloud results and force save
        if chunk.point_cloud:
            point_count = chunk.point_cloud.point_count
            print(f"Point cloud completed: {point_count:,} points generated")
            print("Saving project after point cloud generation...")
            doc.save(project_full_path, chunks=[chunk])
            print("Point cloud saved successfully")
        else:
            print("WARNING: No point cloud was generated!")
            doc.save(project_full_path, chunks=[chunk])  # Save even if point cloud failed
        
        # Step 6: Generate Processing Report
        print(f"\nStep 6: Generating processing report...")
        report_path = os.path.join(project_path, f"processing_report_RGB.pdf")
        chunk.exportReport(report_path)
        print(f"Report saved: {report_path}")
        
        # Final comprehensive save with all processing results
        print(f"\nStep 7: Final project save...")
        save_success = enhanced_save_project(doc, chunk, project_full_path, "final processing")
        if not save_success:
            print("ERROR: Failed to save final project!")
            return False
        
        # Verify all products are saved
        verification_success = verify_saved_products(project_full_path)
        if not verification_success:
            print("WARNING: Product verification failed - some data may not be properly saved")
        
        print(f"\n{'='*60}")
        print(f"SUCCESS: Route {route_info['route_number']} RGB processing completed!")
        print(f"Project: {project_full_path}")
        print(f"GCPs: {imported_count} imported ({enabled_count} active, {imported_count-enabled_count} check points)")
        print(f"Report: {report_path}")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR during processing Route {route_info['route_number']}: {str(e)}")
        print("Processing failed!")
        return False

def process_all_routes(dcim_path, output_path, gcp_path):
    """Process all routes found in DCIM folder"""
    print("METASHAPE RGB AUTOMATION")
    print("=" * 50)
    print(f"DCIM Path: {dcim_path}")
    print(f"Output Path: {output_path}")
    print(f"GCP Path: {gcp_path}")
    
    # Scan for routes
    routes = scan_dcim_folders(dcim_path)
    
    if not routes:
        print("\nNo routes found!")
        print("Expected folder naming pattern: DJI_YYYYMMDDHHMM_###_*")
        print("With RGB images matching pattern: *_D.JPG or *.JPG")
        return False
    
    print(f"\nFound {len(routes)} routes:")
    for i, route in enumerate(routes, 1):
        print(f"  {i}. Route {route['route_number']}: {route['rgb_count']} RGB images")
    
    # Process each route
    print(f"\nStarting processing of {len(routes)} routes...")
    successful = 0
    failed = 0
    
    for route in routes:
        success = process_rgb_route(route, output_path, gcp_path)
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total routes: {len(routes)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output location: {output_path}")
    print(f"GCP location: {gcp_path}")
    print(f"{'='*60}")
    
    return successful > 0

def process_single_route_by_number(route_number, dcim_path, output_path, gcp_path):
    """Process a specific route by route number"""
    routes = scan_dcim_folders(dcim_path)
    target_route = None
    
    for route in routes:
        if route['route_number'] == route_number:
            target_route = route
            break
    
    if not target_route:
        print(f"Route {route_number} not found!")
        print(f"Available routes: {[r['route_number'] for r in routes]}")
        return False
    
    return process_rgb_route(target_route, output_path, gcp_path)

def process_selected_routes(route_numbers, dcim_path, output_path, gcp_path):
    """Process specific routes by route numbers (e.g., ['001', '003', '005'])"""
    print("METASHAPE RGB AUTOMATION - SELECTED ROUTES")
    print("=" * 50)
    print(f"DCIM Path: {dcim_path}")
    print(f"Output Path: {output_path}")
    print(f"GCP Path: {gcp_path}")
    print(f"Processing routes: {', '.join(route_numbers)}")
    
    # Scan for routes
    routes = scan_dcim_folders(dcim_path)
    
    if not routes:
        print("No routes found!")
        return False
    
    # Filter selected routes
    selected_routes = []
    for route_num in route_numbers:
        for route in routes:
            if route['route_number'] == route_num:
                selected_routes.append(route)
                break
        else:
            print(f"WARNING: Route {route_num} not found!")
    
    if not selected_routes:
        print("No valid routes selected!")
        return False
    
    print(f"\nFound {len(selected_routes)} selected routes:")
    for route in selected_routes:
        print(f"  Route {route['route_number']}: {route['rgb_count']} RGB images")
    
    # Process each selected route
    successful = 0
    failed = 0
    
    for route in selected_routes:
        success = process_rgb_route(route, output_path, gcp_path)
        if success:
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"PROCESSING SUMMARY - {len(selected_routes)} SELECTED ROUTES")
    print(f"{'='*60}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"{'='*60}")
    
    return successful > 0

def show_available_routes(dcim_path):
    """Display all available routes with details"""
    routes = scan_dcim_folders(dcim_path)
    
    if not routes:
        print("No routes found!")
        return []
    
    print(f"\nAvailable routes in: {dcim_path}")
    print("-" * 60)
    total_images = 0
    for i, route in enumerate(routes):
        size_category = "Small" if route['rgb_count'] < 200 else "Medium" if route['rgb_count'] < 400 else "Large"
        print(f"{i}: Route {route['route_number']} - {route['rgb_count']} RGB images ({size_category})")
        total_images += route['rgb_count']
    
    print("-" * 60)
    print(f"Total: {len(routes)} routes with {total_images} images")
    
    return routes

# Display usage instructions
print("GENERIC RGB METASHAPE AUTOMATION SCRIPT LOADED")
print("=" * 60)
print("This script requires manual path configuration!")
print("")
print("Required paths:")
print("- dcim_path: Path to DCIM folder containing DJI route folders")
print("- output_path: Path where processed projects will be saved")
print("- gcp_path: Path to folder containing GCP XML files")
print("")
print("Usage examples:")
print("1. process_all_routes(dcim_path, output_path, gcp_path)")
print("2. show_available_routes(dcim_path)")
print("3. process_selected_routes(['001', '003'], dcim_path, output_path, gcp_path)")
print("4. process_single_route_by_number('001', dcim_path, output_path, gcp_path)")
print("")
print("GCP Files Expected:")
print("- gcp_route_001.xml, gcp_route_002.xml, etc. in gcp_path folder")
print("")
print("Example setup:")
print("dcim_path = r'C:\\path\\to\\DCIM'")
print("output_path = r'C:\\path\\to\\output'")
print("gcp_path = r'C:\\path\\to\\GCP'")
print("process_all_routes(dcim_path, output_path, gcp_path)")
