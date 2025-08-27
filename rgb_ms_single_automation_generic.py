"""
Generic Combined RGB+MS Metashape Automation Script
===================================================
Portable automation script for processing RGB and Multispectral drone images together as Multi-Camera system.
No hardcoded paths - all paths configurable via parameters.

Usage in Metashape Console:
exec(open(r'path\\to\\combined_automation_generic.py', encoding='utf-8').read())
"""

import os
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

def create_project_structure(base_path, route_name):
    """Create project folder structure with automatic versioning"""
    base_project_name = f"route_{route_name}_Combined"
    version = 1
    
    # Check for existing versions and increment
    while True:
        if version == 1:
            project_folder_name = base_project_name
        else:
            project_folder_name = f"{base_project_name}_v{version}"
        
        project_folder = os.path.join(base_path, project_folder_name)
        
        if not os.path.exists(project_folder):
            break
        version += 1
    
    # Create the project folder and subfolders
    os.makedirs(project_folder, exist_ok=True)
    
    subfolders = ['orthomosaic', 'dem', 'pointcloud', 'report']
    for subfolder in subfolders:
        os.makedirs(os.path.join(project_folder, subfolder), exist_ok=True)
    
    return project_folder, project_folder_name

def scan_dcim_folders_combined(base_path):
    """Scan for both RGB (JPG) and MS (TIF) images in DCIM folders"""
    dcim_folders = {}
    
    for root, dirs, files in os.walk(base_path):
        if 'DCIM' in root or any('DJI_' in d for d in dirs):
            # Extract route identifier from path or folder names
            path_parts = root.replace('\\', '/').split('/')
            route_match = None
            
            # Look for route pattern in folder names
            for part in path_parts:
                if re.match(r'^DJI_\d{12,14}_(\d{3})_.*', part):
                    route_match = re.search(r'DJI_\d{12,14}_(\d{3})_.*', part)
                    break
                elif re.match(r'^route_\d+', part):
                    route_match = re.search(r'route_(\d+)', part)
                    break
            
            if route_match:
                route_number = route_match.group(1)
                
                if route_number not in dcim_folders:
                    dcim_folders[route_number] = {'rgb_images': [], 'ms_images': [], 'dcim_path': root}
                
                # Collect RGB images (JPG with 'D' identifier)
                rgb_images = [f for f in files if f.lower().endswith('.jpg') and ('D' in f.upper() or 'RGB' in f.upper())]
                dcim_folders[route_number]['rgb_images'].extend([os.path.join(root, f) for f in rgb_images])
                
                # Collect MS images (TIF files)
                ms_images = [f for f in files if (f.lower().endswith('.tif') or f.lower().endswith('.tiff')) and 'MS' in f.upper()]
                dcim_folders[route_number]['ms_images'].extend([os.path.join(root, f) for f in ms_images])
    
    return dcim_folders

def import_gcps_from_xml(chunk, gcp_file_path):
    """Import GCPs from XML file using Metashape's built-in function"""
    if not os.path.exists(gcp_file_path):
        print(f"Warning: GCP file not found: {gcp_file_path}")
        return False
    
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
        
        return True
    except Exception as e:
        print(f"Error importing GCPs: {e}")
        return False

def process_combined_route(route_number, rgb_images, ms_images, project_folder, gcp_file_path):
    """Process both RGB and MS images together in Multi-Camera system"""
    
    # Create new document and chunk
    doc = Metashape.Document()
    chunk = doc.addChunk()
    chunk.label = f"Route_{route_number}_Combined"
    
    print(f"Processing Route {route_number} - Combined RGB+MS")
    print(f"RGB images: {len(rgb_images)}")
    print(f"MS images: {len(ms_images)}")
    
    # Combine all images for Multi-Camera system
    all_images = rgb_images + ms_images
    
    try:
        # Add all photos as Multi-Camera system
        chunk.addPhotos(all_images, layout=Metashape.MulticameraLayout)
        print(f"Added {len(all_images)} photos as Multi-Camera system")
        
        # Save project after adding photos
        project_file = os.path.join(project_folder, f"route_{route_number}_combined.psx")
        doc.save(project_file, chunks=[chunk])
        print(f"Project saved: {project_file}")
        
        # Import GCPs (will apply to RGB and propagate to MS)
        if import_gcps_from_xml(chunk, gcp_file_path):
            print("GCPs imported and applied to Multi-Camera system")
        
        # Set coordinate systems
        chunk.crs = Metashape.CoordinateSystem("EPSG::4326")  # WGS84 for images
        print("Coordinate system set to WGS84 (EPSG:4326)")
        doc.save(project_file, chunks=[chunk])  # Save after setup
        
        # Align photos
        print("Starting photo alignment...")
        print("  Settings: Downscale=1 (full resolution), Generic preselection=True, Reference preselection=True")
        chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection=True)
        chunk.alignCameras(adaptive_fitting=False)
        doc.save(project_file, chunks=[chunk])  # Save after alignment
        print("Photo alignment completed")
        
        # Check alignment results
        aligned_cameras = sum(1 for camera in chunk.cameras if camera.transform)
        total_cameras = len(chunk.cameras)
        alignment_ratio = aligned_cameras / total_cameras if total_cameras > 0 else 0
        
        print(f"Camera alignment completed: {aligned_cameras}/{total_cameras} cameras aligned ({alignment_ratio:.1%})")
        
        if aligned_cameras == 0:
            print("ERROR: No cameras aligned successfully!")
            return False
        
        # Build depth maps and point cloud
        print("Building depth maps and point cloud...")
        print("  Settings: Quality=Medium (4), Filter=MildFiltering, Point spacing=0.1m")
        chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.MildFiltering, max_neighbors=16)
        chunk.buildPointCloud(source_data=Metashape.DataSource.DepthMapsData, point_colors=True, points_spacing=0.1)
        doc.save(project_file, chunks=[chunk])  # Save after dense cloud
        print("Point cloud completed")
        
        # Build mesh
        print("Building mesh...")
        chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation)
        doc.save(project_file, chunks=[chunk])  # Save after mesh
        print("Mesh completed")
        
        # Build texture
        print("Building texture...")
        chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=4096)
        doc.save(project_file, chunks=[chunk])  # Save after texture
        print("Texture completed")
        
        # Build DEM
        print("Building DEM...")
        chunk.buildDem(source_data=Metashape.DenseCloudData)
        doc.save(project_file, chunks=[chunk])  # Save after DEM
        print("DEM completed")
        
        # Build Orthomosaic
        print("Building orthomosaic...")
        chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)
        doc.save(project_file, chunks=[chunk])  # Save after orthomosaic
        print("Orthomosaic completed")
        
        # Export products
        print("Exporting products...")
        
        # Export orthomosaic
        ortho_path = os.path.join(project_folder, "orthomosaic", f"route_{route_number}_combined_orthomosaic.tif")
        chunk.exportRaster(ortho_path, image_format=Metashape.ImageFormatTIFF)
        print(f"Orthomosaic exported: {ortho_path}")
        
        # Export DEM
        dem_path = os.path.join(project_folder, "dem", f"route_{route_number}_combined_dem.tif")
        chunk.exportRaster(dem_path, source_data=Metashape.ElevationData, image_format=Metashape.ImageFormatTIFF)
        print(f"DEM exported: {dem_path}")
        
        # Export point cloud
        pc_path = os.path.join(project_folder, "pointcloud", f"route_{route_number}_combined_pointcloud.las")
        chunk.exportPoints(pc_path, source_data=Metashape.DenseCloudData, format=Metashape.PointsFormatLAS)
        print(f"Point cloud exported: {pc_path}")
        
        # Export processing report
        report_path = os.path.join(project_folder, "report", f"route_{route_number}_combined_report.pdf")
        chunk.exportReport(report_path)
        print(f"Processing report exported: {report_path}")
        
        # Final save with verification
        save_success = enhanced_save_project(doc, chunk, project_file, "final combined processing")
        if not save_success:
            print("ERROR: Failed to save final combined project!")
            return False
        
        # Verify all products are saved
        verification_success = verify_saved_products(project_file)
        if not verification_success:
            print("WARNING: Combined product verification failed - some data may not be properly saved")
        
        print(f"Route {route_number} combined processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error processing route {route_number}: {e}")
        return False

def process_combined_routes(dcim_path, output_path, gcp_path):
    """Process all combined routes found in the specified paths"""
    print("METASHAPE COMBINED RGB+MS AUTOMATION")
    print("=" * 50)
    print(f"DCIM Path: {dcim_path}")
    print(f"Output Path: {output_path}")
    print(f"GCP Path: {gcp_path}")
    
    # Scan for DCIM folders with both RGB and MS images
    dcim_folders = scan_dcim_folders_combined(dcim_path)
    
    if not dcim_folders:
        print("No DCIM folders with images found!")
        return False
    
    print(f"Found {len(dcim_folders)} routes with images:")
    for route_number, data in dcim_folders.items():
        print(f"  Route {route_number}: {len(data['rgb_images'])} RGB, {len(data['ms_images'])} MS images")
    
    successful = 0
    failed = 0
    
    # Process each route
    for route_number, data in dcim_folders.items():
        rgb_images = data['rgb_images']
        ms_images = data['ms_images']
        
        if not rgb_images and not ms_images:
            print(f"Skipping route {route_number}: No images found")
            continue
        
        # Create project structure with versioning
        project_folder, project_name = create_project_structure(output_path, route_number)
        print(f"Created project folder: {project_folder}")
        
        # Look for GCP file
        gcp_file_path = os.path.join(gcp_path, f"gcp_route_{route_number}.xml")
        
        # Process the route
        success = process_combined_route(route_number, rgb_images, ms_images, project_folder, gcp_file_path)
        
        if success:
            print(f"✓ Route {route_number} processed successfully")
            successful += 1
        else:
            print(f"✗ Route {route_number} processing failed")
            failed += 1
        
        print("-" * 50)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"COMBINED PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total routes: {len(dcim_folders)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output location: {output_path}")
    print(f"GCP location: {gcp_path}")
    print(f"{'='*60}")
    
    return successful > 0

def show_available_combined_routes(dcim_path):
    """Display all available combined routes with details"""
    dcim_folders = scan_dcim_folders_combined(dcim_path)
    
    if not dcim_folders:
        print("No combined routes found!")
        return []
    
    print(f"\nAvailable combined routes in: {dcim_path}")
    print("-" * 70)
    total_rgb = 0
    total_ms = 0
    
    for route_number, data in dcim_folders.items():
        rgb_count = len(data['rgb_images'])
        ms_count = len(data['ms_images'])
        total_rgb += rgb_count
        total_ms += ms_count
        
        print(f"Route {route_number}: {rgb_count} RGB + {ms_count} MS = {rgb_count + ms_count} total images")
    
    print("-" * 70)
    print(f"Total: {len(dcim_folders)} routes with {total_rgb} RGB + {total_ms} MS images")
    
    return dcim_folders

# Display usage instructions
print("GENERIC COMBINED RGB+MS METASHAPE AUTOMATION SCRIPT LOADED")
print("=" * 70)
print("This script requires manual path configuration!")
print("")
print("Required paths:")
print("- dcim_path: Path to folder containing DJI route folders with RGB and MS images")
print("- output_path: Path where processed projects will be saved")
print("- gcp_path: Path to folder containing GCP XML files")
print("")
print("Usage examples:")
print("1. process_combined_routes(dcim_path, output_path, gcp_path)")
print("2. show_available_combined_routes(dcim_path)")
print("")
print("GCP Files Expected:")
print("- gcp_route_001.xml, gcp_route_002.xml, etc. in gcp_path folder")
print("")
print("Requirements:")
print("- Both RGB (JPG with 'D' or 'RGB' identifier) and MS (TIF with 'MS') images")
print("- Multi-Camera system configuration for combined processing")
print("- Full pipeline: Alignment → Dense Cloud → Mesh → Texture → DEM → Orthomosaic")
print("- Automatic product export (orthomosaic, DEM, point cloud, report)")
print("")
print("Example setup:")
print("dcim_path = r'C:\\path\\to\\project\\with\\DCIM\\folders'")
print("output_path = r'C:\\path\\to\\output'")
print("gcp_path = r'C:\\path\\to\\GCP'")
print("process_combined_routes(dcim_path, output_path, gcp_path)")
