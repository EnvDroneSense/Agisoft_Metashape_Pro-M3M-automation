"""
RGB+MS Combined Multi-Dataset Automation Script - GENERIC VERSION
=================================================================
Generic version with configurable paths for any project
Optimized for Metashape console compatibility
COMBINED VARIANT - Processes both RGB (JPG) and MS (TIF) images as Multi-Camera system

USAGE:
1. Set your paths using configure_paths()
2. Set routes using configure_routes() 
3. Run process_combined_routes()

EXAMPLE LOADING IN METASHAPE CONSOLE:
exec(open(r'YOUR_PATH/combined_rgb_ms_console_generic.py', encoding='utf-8').read())
configure_paths(dcim=r'YOUR_DCIM_PATH', gcp=r'YOUR_GCP_PATH', output=r'YOUR_OUTPUT_PATH')
configure_routes(['001', '002'])
run_combined_rgb_ms_automation()
"""

import os
import glob
import re
import Metashape

# Configuration - TO BE SET BY USER
dcim_base_path = None
gcp_base_path = None
output_base_path = None
routes_to_combine = []

def configure_paths(dcim, gcp, output):
    """Configure the base paths for processing"""
    global dcim_base_path, gcp_base_path, output_base_path
    dcim_base_path = dcim
    gcp_base_path = gcp
    output_base_path = output
    print(f"Paths configured:")
    print(f"  DCIM: {dcim_base_path}")
    print(f"  GCP: {gcp_base_path}")
    print(f"  Output: {output_base_path}")

def configure_routes(route_numbers, dcim_path=None, gcp_path=None, output_path=None):
    """Configure routes and optionally update paths"""
    global routes_to_combine, dcim_base_path, gcp_base_path, output_base_path
    routes_to_combine = route_numbers
    if dcim_path: dcim_base_path = dcim_path
    if gcp_path: gcp_base_path = gcp_path
    if output_path: output_base_path = output_path
    print(f"Routes configured: {', '.join(route_numbers)}")
    if dcim_path or gcp_path or output_path:
        print(f"Paths updated:")
        if dcim_path: print(f"  DCIM: {dcim_base_path}")
        if gcp_path: print(f"  GCP: {gcp_base_path}")
        if output_path: print(f"  Output: {output_base_path}")

def validate_configuration():
    """Validate that all required paths are configured"""
    if not dcim_base_path:
        raise ValueError("DCIM path not configured. Use configure_paths() or configure_routes()")
    if not gcp_base_path:
        raise ValueError("GCP path not configured. Use configure_paths() or configure_routes()")
    if not output_base_path:
        raise ValueError("Output path not configured. Use configure_paths() or configure_routes()")
    if not routes_to_combine:
        raise ValueError("Routes not configured. Use configure_routes()")
    return True

def scan_dcim_folders_combined(dcim_path):
    route_folders = []
    if not os.path.exists(dcim_path):
        print(f"ERROR: DCIM folder not found: {dcim_path}")
        return route_folders
    print(f"Scanning DCIM directory for RGB+MS images: {dcim_path}")
    pattern = r'DJI_\d{12,14}_(\d{3})_.*'
    for folder in os.listdir(dcim_path):
        folder_path = os.path.join(dcim_path, folder)
        if os.path.isdir(folder_path):
            match = re.match(pattern, folder)
            if match:
                route_number = match.group(1)
                
                # Look for RGB images
                rgb_pattern = os.path.join(folder_path, "*_D.JPG")
                rgb_files = glob.glob(rgb_pattern)
                if not rgb_files:
                    rgb_pattern_alt = os.path.join(folder_path, "*D.JPG")
                    rgb_files = glob.glob(rgb_pattern_alt)
                if not rgb_files:
                    all_jpg = glob.glob(os.path.join(folder_path, "*.JPG"))
                    all_jpg.extend(glob.glob(os.path.join(folder_path, "*.jpg")))
                    rgb_files = all_jpg
                
                # Look for MS images
                ms_patterns = ["*_MS_G.TIF", "*_MS_R.TIF", "*_MS_RE.TIF", "*_MS_NIR.TIF"]
                ms_files = []
                for pattern_ms in ms_patterns:
                    ms_pattern = os.path.join(folder_path, pattern_ms)
                    ms_files.extend(glob.glob(ms_pattern))
                
                # Also check lowercase variants
                if not ms_files:
                    ms_patterns_lower = ["*_ms_g.tif", "*_ms_r.tif", "*_ms_re.tif", "*_ms_nir.tif"]
                    for pattern_ms in ms_patterns_lower:
                        ms_pattern = os.path.join(folder_path, pattern_ms)
                        ms_files.extend(glob.glob(ms_pattern))
                
                # Fallback: any TIF with MS in name
                if not ms_files:
                    all_tif = glob.glob(os.path.join(folder_path, "*MS*.TIF"))
                    all_tif.extend(glob.glob(os.path.join(folder_path, "*ms*.tif")))
                    ms_files = all_tif
                
                # Only include routes that have both RGB and MS images
                if rgb_files and ms_files:
                    all_images = rgb_files + ms_files
                    route_folders.append({
                        'folder_name': folder, 
                        'folder_path': folder_path, 
                        'route_number': route_number, 
                        'rgb_count': len(rgb_files),
                        'ms_count': len(ms_files),
                        'total_count': len(all_images),
                        'image_files': all_images,
                        'rgb_files': rgb_files,
                        'ms_files': ms_files
                    })
                    print(f"  Found Route {route_number}: {len(rgb_files)} RGB + {len(ms_files)} MS = {len(all_images)} total images")
                elif rgb_files:
                    print(f"  Route {route_number}: {len(rgb_files)} RGB images (no MS images found)")
                elif ms_files:
                    print(f"  Route {route_number}: {len(ms_files)} MS images (no RGB images found)")
    return sorted(route_folders, key=lambda x: x['route_number'])

def enhanced_save_project(doc, chunk, project_path, step_name=""):
    try:
        print(f"Saving project{' after ' + step_name if step_name else ''}...")
        doc.save(project_path)
        print(f"Project saved successfully{' after ' + step_name if step_name else ''}")
        return True
    except Exception as e:
        print(f"ERROR saving project{' after ' + step_name if step_name else ''}: {str(e)}")
        return False

def create_combined_project_structure(output_base, route_numbers):
    route_list = "_".join(route_numbers)
    base_project_folder = f"combined_routes_{route_list}_RGB_MS"
    base_project_file = f"combined_routes_{route_list}_RGB_MS.psx"
    project_folder = base_project_folder
    project_file = base_project_file
    version = 1
    while True:
        project_path = os.path.join(output_base, project_folder)
        project_full_path = os.path.join(project_path, project_file)
        if os.path.exists(project_path):
            if os.listdir(project_path):
                version += 1
                project_folder = f"{base_project_folder}_v{version}"
                project_file = f"combined_routes_{route_list}_RGB_MS_v{version}.psx"
                print(f"Folder {base_project_folder} exists, trying {project_folder}")
                continue
            else:
                break
        else:
            break
    os.makedirs(project_path, exist_ok=True)
    project_full_path = os.path.join(project_path, project_file)
    if version > 1:
        print(f"Created versioned project folder: {project_folder}")
    return project_path, project_full_path

def find_routes_by_numbers(route_numbers, dcim_path):
    print(f"Looking for RGB+MS routes: {', '.join(route_numbers)}")
    all_routes = scan_dcim_folders_combined(dcim_path)
    if not all_routes:
        print("No combined RGB+MS routes found in DCIM folder!")
        return []
    found_routes = []
    for route_num in route_numbers:
        route_found = False
        for route in all_routes:
            if route['route_number'] == route_num:
                found_routes.append(route)
                route_found = True
                print(f"  Route {route_num}: {route['rgb_count']} RGB + {route['ms_count']} MS = {route['total_count']} total images in {route['folder_name']}")
                break
        if not route_found:
            print(f"  Route {route_num}: Not found!")
    if len(found_routes) < 2:
        print(f"ERROR: Need at least 2 routes for combination, found {len(found_routes)}")
        return []
    return found_routes

def get_gcp_file_path(route_number, gcp_base_path):
    gcp_filename = f"gcp_route_{route_number}.xml"
    gcp_file_path = os.path.join(gcp_base_path, gcp_filename)
    return gcp_file_path

def validate_routes_and_gcps(routes, gcp_base_path):
    print("Validating RGB+MS routes and GCP files...")
    valid_routes = []
    for route in routes:
        route_num = route['route_number']
        gcp_path = get_gcp_file_path(route_num, gcp_base_path)
        print(f"\nValidating Route {route_num}:")
        print(f"  DCIM: {route['folder_name']} ({route['rgb_count']} RGB + {route['ms_count']} MS = {route['total_count']} total images)")
        print(f"  GCP: {os.path.basename(gcp_path)}")
        if not os.path.exists(gcp_path):
            print(f"  ERROR: GCP file not found: {gcp_path}")
            continue
        else:
            print(f"  GCP file exists")
        route_with_gcp = route.copy()
        route_with_gcp['gcp_path'] = gcp_path
        route_with_gcp['name'] = f"Route_{route_num}_RGB_MS"
        valid_routes.append(route_with_gcp)
        print(f"  Route {route_num} validation successful")
    print(f"\nValidation Summary: {len(valid_routes)}/{len(routes)} RGB+MS routes valid")
    return valid_routes

def diagnose_datasets(valid_routes):
    print("\nDIAGNOSING RGB+MS DATASET COMPATIBILITY:")
    print("=" * 50)
    
    # Check image counts
    total_rgb = sum(route['rgb_count'] for route in valid_routes)
    total_ms = sum(route['ms_count'] for route in valid_routes)
    total_images = sum(route['total_count'] for route in valid_routes)
    print(f"Total images across all routes: {total_rgb} RGB + {total_ms} MS = {total_images} total")
    
    for route in valid_routes:
        print(f"  Route {route['route_number']}: {route['rgb_count']} RGB + {route['ms_count']} MS = {route['total_count']} total")
        
        # Sample RGB images
        sample_rgb = route['rgb_files'][:3]
        print(f"    Sample RGB: {[os.path.basename(img) for img in sample_rgb]}")
        
        # Sample MS images and check bands
        sample_ms = route['ms_files'][:4]
        print(f"    Sample MS: {[os.path.basename(img) for img in sample_ms]}")
        
        # Check MS band distribution
        bands = {'G': 0, 'R': 0, 'RE': 0, 'NIR': 0}
        for img in route['ms_files']:
            img_name = os.path.basename(img).upper()
            if '_MS_G.' in img_name:
                bands['G'] += 1
            elif '_MS_R.' in img_name:
                bands['R'] += 1
            elif '_MS_RE.' in img_name:
                bands['RE'] += 1
            elif '_MS_NIR.' in img_name:
                bands['NIR'] += 1
        
        print(f"    MS band distribution: G={bands['G']}, R={bands['R']}, RE={bands['RE']}, NIR={bands['NIR']}")
    
    # Check if routes are from same date/session
    folder_dates = []
    for route in valid_routes:
        folder_name = route['folder_name']
        if folder_name.startswith('DJI_'):
            date_part = folder_name.split('_')[1][:8]  # YYYYMMDD
            folder_dates.append(date_part)
            print(f"  Route {route['route_number']} date: {date_part}")
    
    if len(set(folder_dates)) > 1:
        print("  WARNING: Routes are from different dates - this may cause matching issues!")
    else:
        print("  OK: All routes from same date")
    
    print("=" * 50)
    return True

def import_route_as_chunk(doc, route_info):
    route_num = route_info['route_number']
    print(f"\nImporting RGB+MS Route {route_num}: {route_info['name']}")
    chunk = doc.addChunk()
    chunk.label = route_info['name']
    chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
    print(f"  Set initial coordinate system to WGS84 (EPSG:4326)")
    print(f"  Adding {route_info['total_count']} images ({route_info['rgb_count']} RGB + {route_info['ms_count']} MS) as Multi-Camera system...")
    
    # Add all images as Multi-Camera system for RGB+MS combination
    chunk.addPhotos(route_info['image_files'])
    if len(chunk.cameras) == 0:
        raise RuntimeError(f"No cameras were added for RGB+MS Route {route_num}")
    print(f"  Successfully added {len(chunk.cameras)} cameras (MultiCamera layout for RGB+MS)")
    
    gcp_filename = os.path.basename(route_info['gcp_path'])
    print(f"  Importing markers from: {gcp_filename}")
    try:
        chunk.importMarkers(path=route_info['gcp_path'])
        imported_count = len(chunk.markers)
        enabled_count = sum(1 for marker in chunk.markers if marker.reference.enabled)
        print(f"  Imported {imported_count} GCP markers ({enabled_count} enabled, {imported_count-enabled_count} check points)")
        for marker in chunk.markers:
            projections = len(marker.projections)
            enabled_status = "[ENABLED]" if marker.reference.enabled else "[DISABLED]"
            print(f"    {marker.label}: {projections} projections {enabled_status}")
        chunk.crs = Metashape.CoordinateSystem("EPSG::4258")
        print(f"  Set coordinate system to ETRS89 (EPSG:4258)")
        return chunk, imported_count, enabled_count
    except Exception as e:
        raise RuntimeError(f"Failed to import markers for RGB+MS Route {route_num}: {str(e)}")

def merge_chunks_with_validation(doc, chunks_to_merge):
    print(f"\nMerging {len(chunks_to_merge)} RGB+MS chunks...")
    total_markers_before = 0
    total_projections_before = 0
    total_cameras_before = 0
    chunks_before_merge = len(doc.chunks)
    
    for chunk in chunks_to_merge:
        total_markers_before += len(chunk.markers)
        total_cameras_before += len(chunk.cameras)
        for marker in chunk.markers:
            total_projections_before += len(marker.projections)
    print(f"  Before merge: {len(chunks_to_merge)} chunks, {total_cameras_before} cameras, {total_markers_before} markers, {total_projections_before} total projections")
    
    # Check coordinate systems
    coordinate_systems = set()
    for chunk in chunks_to_merge:
        if chunk.crs:
            coordinate_systems.add(str(chunk.crs))
    
    print(f"  Coordinate systems found: {len(coordinate_systems)}")
    for crs in coordinate_systems:
        print(f"    {crs}")
    
    try:
        # Align chunks before merging if needed
        if len(coordinate_systems) > 1:
            print("  Aligning chunks (multiple coordinate systems detected)...")
            doc.alignChunks(chunks_to_merge)
            print("  Chunks aligned successfully")
        else:
            print("  All chunks use same coordinate system - no alignment needed")
        
        # Merge chunks - this creates a NEW chunk
        doc.mergeChunks(chunks=chunks_to_merge, merge_markers=True, merge_tiepoints=True, copy_depth_maps=False, copy_point_clouds=False, copy_models=False, copy_elevations=False, copy_orthomosaics=False)
        print("  RGB+MS chunks merged successfully")
        
        # Find the NEW merged chunk
        chunks_after_merge = len(doc.chunks)
        print(f"  Chunks after merge: {chunks_after_merge} (was {chunks_before_merge})")
        
        if chunks_after_merge <= chunks_before_merge:
            raise RuntimeError("No new chunk created during merge!")
        
        # The new merged chunk is typically the last one
        merged_chunk = doc.chunks[-1]
        merged_chunk.label = "Merged_RGB_MS_Routes"
        print(f"  New merged RGB+MS chunk created: {merged_chunk.label}")
        
        # Remove the original unmerged chunks
        print(f"  Removing {len(chunks_to_merge)} original chunks...")
        chunks_to_remove = []
        for original_chunk in chunks_to_merge:
            if original_chunk in doc.chunks:
                chunks_to_remove.append(original_chunk)
        
        # Remove chunks in reverse order to avoid index issues
        for chunk_to_remove in reversed(chunks_to_remove):
            try:
                chunk_label = chunk_to_remove.label
                doc.remove(chunk_to_remove)
                print(f"    Removed: {chunk_label}")
            except Exception as e:
                print(f"    Error removing {chunk_to_remove.label}: {e}")
        
        print(f"  Successfully removed {len(chunks_to_remove)} original chunks")
        
        # Verify cleanup
        final_chunk_count = len(doc.chunks)
        if final_chunk_count != 1:
            print(f"  WARNING: Expected 1 chunk after cleanup, found {final_chunk_count}")
            print(f"  Remaining chunks:")
            for i, chunk in enumerate(doc.chunks):
                print(f"    {i+1}. {chunk.label}")
        else:
            print(f"  Cleanup verified: Only merged RGB+MS chunk remains")
        
        # Verify the merge worked
        merged_markers = len(merged_chunk.markers)
        merged_cameras = len(merged_chunk.cameras)
        merged_projections = sum(len(marker.projections) for marker in merged_chunk.markers)
        
        print(f"  Final result: {len(doc.chunks)} chunk, {merged_cameras} cameras, {merged_markers} markers, {merged_projections} total projections")
        
        if merged_cameras != total_cameras_before:
            print(f"  WARNING: Camera count mismatch! Expected {total_cameras_before}, got {merged_cameras}")
        else:
            print(f"  Camera count validated: {merged_cameras}")
        
        print(f"  Marker consolidation: {total_markers_before} -> {merged_markers} (duplicates merged)")
        
        if merged_projections == 0:
            raise RuntimeError("No marker projections found after merge!")
        
        print(f"  RGB+MS merge validation completed successfully")
        return merged_chunk
        
    except Exception as e:
        raise RuntimeError(f"RGB+MS chunk merge failed: {str(e)}")

def match_photos(chunk):
    print(f"\nStep 2: Matching RGB+MS photos...")
    print("  Settings: Downscale=1 (full resolution for RGB+MS combination), Generic preselection=True, Reference preselection=True")
    
    chunk.matchPhotos(
        downscale=1,  # Full resolution for RGB+MS combination
        generic_preselection=True,
        reference_preselection=True
    )
    
    print(f"RGB+MS photo matching completed successfully")
    print(f"  (Check console output for tie point statistics)")
    return True

def align_cameras(chunk):
    print(f"\nStep 3: Aligning RGB+MS cameras...")
    chunk.alignCameras(adaptive_fitting=False)
    aligned_cameras = len([cam for cam in chunk.cameras if cam.transform])
    total_cameras = len(chunk.cameras)
    alignment_ratio = aligned_cameras / total_cameras if total_cameras > 0 else 0
    print(f"RGB+MS camera alignment completed: {aligned_cameras}/{total_cameras} cameras aligned ({alignment_ratio:.1%})")
    if aligned_cameras == 0:
        print("ERROR: No cameras aligned! Cannot proceed with processing.")
        return False
    if chunk.markers:
        enabled_markers = sum(1 for marker in chunk.markers if marker.reference.enabled)
        print(f"GCP markers: {enabled_markers} enabled for alignment, {len(chunk.markers) - enabled_markers} as check points")
    return True

def build_depth_maps(chunk):
    print(f"\nStep 4: Building depth maps...")
    print("  Settings: Quality=Medium (4), Filter=MildFiltering, Max neighbors=16")
    chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.FilterMode.MildFiltering, max_neighbors=16)
    print("Depth maps completed successfully")
    return True

def generate_point_cloud(chunk):
    print(f"\nStep 5: Building point cloud...")
    print("  Settings: Source=Depth maps, Point colors=True, Spacing=0.1m")
    chunk.buildPointCloud(source_data=Metashape.DataSource.DepthMapsData, point_colors=True, points_spacing=0.1)
    if chunk.point_cloud:
        point_count = chunk.point_cloud.point_count
        print(f"Point cloud completed: {point_count:,} points generated")
        return True
    else:
        print("WARNING: No point cloud was generated!")
        return False

def generate_processing_report(chunk, project_path, route_numbers):
    print(f"\nStep 6: Generating processing report...")
    route_list = "_".join(route_numbers)
    report_path = os.path.join(os.path.dirname(project_path), f"processing_report_combined_routes_{route_list}_RGB_MS.pdf")
    chunk.exportReport(report_path)
    print(f"Report saved: {report_path}")
    return report_path

def process_combined_routes(route_numbers=None, dcim_path=None, gcp_path=None, output_path=None):
    if route_numbers is None: route_numbers = routes_to_combine
    if dcim_path is None: dcim_path = dcim_base_path
    if gcp_path is None: gcp_path = output_path
    if output_path is None: output_path = output_base_path
    
    # Validate configuration
    if not dcim_path or not gcp_path or not output_path or not route_numbers:
        print("ERROR: Configuration incomplete!")
        print("Please use configure_paths() and configure_routes() first")
        return False
    
    print("METASHAPE RGB+MS MULTI-ROUTE COMBINATION - GENERIC VERSION")
    print("=" * 60)
    print(f"Routes to combine: {', '.join(route_numbers)}")
    print(f"DCIM path: {dcim_path}")
    print(f"GCP path: {gcp_path}")
    print(f"Output path: {output_path}")
    print("=" * 60)
    try:
        print(f"\nStep 0: Finding and validating RGB+MS routes...")
        found_routes = find_routes_by_numbers(route_numbers, dcim_path)
        if not found_routes:
            print("RGB+MS route discovery failed!")
            return False
        valid_routes = validate_routes_and_gcps(found_routes, gcp_path)
        if not valid_routes:
            print("RGB+MS route validation failed!")
            return False
        
        # Diagnose dataset compatibility
        diagnose_datasets(valid_routes)
        project_path, project_full_path = create_combined_project_structure(output_path, route_numbers)
        print(f"\nProject will be saved to: {project_full_path}")
        print(f"\nStep 1: Importing {len(valid_routes)} RGB+MS routes as separate chunks...")
        doc = Metashape.Document()
        imported_chunks = []
        total_imported_markers = 0
        total_enabled_markers = 0
        for route in valid_routes:
            try:
                chunk, imported_count, enabled_count = import_route_as_chunk(doc, route)
                imported_chunks.append(chunk)
                total_imported_markers += imported_count
                total_enabled_markers += enabled_count
            except Exception as e:
                print(f"ERROR importing RGB+MS Route {route['route_number']}: {str(e)}")
                print("Stopping processing due to route import failure.")
                return False
        print(f"\nSuccessfully imported {len(imported_chunks)} RGB+MS routes")
        print(f"   Total markers imported: {total_imported_markers}")
        print(f"   Total enabled markers: {total_enabled_markers}")
        doc.save(project_full_path)
        print(f"Project saved after RGB+MS route import")
        print(f"\nStep 1.5: Merging RGB+MS chunks into single dataset...")
        try:
            merged_chunk = merge_chunks_with_validation(doc, imported_chunks)
        except Exception as e:
            print(f"ERROR during RGB+MS chunk merge: {str(e)}")
            print("Stopping processing due to merge failure.")
            return False
        doc.save(project_full_path)
        print(f"Project saved after RGB+MS chunk merge")
        
        # Debug: Check merged chunk state
        print(f"\nDEBUG: Merged RGB+MS chunk analysis:")
        print(f"  Total cameras: {len(merged_chunk.cameras)}")
        print(f"  Total markers: {len(merged_chunk.markers)}")
        print(f"  Enabled markers: {sum(1 for m in merged_chunk.markers if m.reference.enabled)}")
        print(f"  Coordinate system: {merged_chunk.crs}")
        cameras_with_gps = sum(1 for cam in merged_chunk.cameras if cam.reference and cam.reference.location)
        print(f"  Cameras with GPS: {cameras_with_gps}/{len(merged_chunk.cameras)}")
        
        print(f"\nStarting standard processing workflow on merged RGB+MS dataset...")
        if not match_photos(merged_chunk):
            print("RGB+MS photo matching failed!")
            doc.save(project_full_path)
            return False
        doc.save(project_full_path)
        print("Project saved after RGB+MS photo matching")
        if not align_cameras(merged_chunk):
            print("RGB+MS camera alignment failed!")
            doc.save(project_full_path)
            return False
        doc.save(project_full_path)
        print("Project saved after RGB+MS camera alignment")
        if not build_depth_maps(merged_chunk):
            print("Depth map generation failed!")
            doc.save(project_full_path)
            return False
        doc.save(project_full_path)
        print("Project saved after depth map generation")
        if not generate_point_cloud(merged_chunk):
            print("Point cloud generation failed!")
            doc.save(project_full_path)
            return False
        doc.save(project_full_path)
        print("Project saved after point cloud generation")
        report_path = generate_processing_report(merged_chunk, project_full_path, route_numbers)
        print(f"\nStep 7: Final project save...")
        save_success = enhanced_save_project(doc, merged_chunk, project_full_path, "final RGB+MS processing")
        if not save_success:
            print("ERROR: Failed to save final project!")
            return False
        final_cameras = len(merged_chunk.cameras)
        final_markers = len(merged_chunk.markers)
        final_enabled = sum(1 for marker in merged_chunk.markers if marker.reference.enabled)
        final_points = merged_chunk.point_cloud.point_count if merged_chunk.point_cloud else 0
        print(f"\n{'='*60}")
        print(f"SUCCESS: Combined RGB+MS route processing completed!")
        print(f"{'='*60}")
        print(f"Input routes: {', '.join(route_numbers)}")
        print(f"Final cameras: {final_cameras}")
        print(f"Final markers: {final_markers} ({final_enabled} enabled, {final_markers-final_enabled} check points)")
        print(f"Point cloud: {final_points:,} points")
        print(f"Project: {project_full_path}")
        print(f"Report: {report_path}")
        print(f"{'='*60}")
        return True
    except Exception as e:
        print(f"\nFATAL ERROR during RGB+MS processing: {str(e)}")
        print("Processing failed!")
        return False

def show_available_routes():
    validate_configuration()
    print("\nSCANNING FOR AVAILABLE RGB+MS ROUTES")
    print("=" * 50)
    routes = scan_dcim_folders_combined(dcim_base_path)
    if not routes:
        print("No RGB+MS routes found!")
        return []
    print(f"Found {len(routes)} RGB+MS routes:")
    for route in routes:
        gcp_path = get_gcp_file_path(route['route_number'], gcp_base_path)
        gcp_exists = os.path.exists(gcp_path)
        gcp_status = "OK" if gcp_exists else "MISSING"
        print(f"  Route {route['route_number']}: {route['rgb_count']} RGB + {route['ms_count']} MS = {route['total_count']} total, GCP: {gcp_status}")
    print("=" * 50)
    return routes

def show_current_configuration():
    print("\nCURRENT RGB+MS CONFIGURATION")
    print("=" * 50)
    print(f"DCIM Base Path: {dcim_base_path}")
    print(f"GCP Base Path: {gcp_base_path}")
    print(f"Output Path: {output_base_path}")
    print(f"Routes to Combine: {', '.join(routes_to_combine) if routes_to_combine else 'Not configured'}")
    print("=" * 50)

def run_combined_rgb_ms_automation():
    validate_configuration()
    return process_combined_routes()

def quick_diagnosis():
    validate_configuration()
    print("QUICK DIAGNOSIS OF RGB+MS ROUTES TO COMBINE")
    print("=" * 50)
    found_routes = find_routes_by_numbers(routes_to_combine, dcim_base_path)
    if found_routes:
        valid_routes = validate_routes_and_gcps(found_routes, gcp_base_path)
        if valid_routes:
            diagnose_datasets(valid_routes)
            return True
    return False

print("RGB+MS MULTI-ROUTE COMBINED AUTOMATION SCRIPT LOADED - GENERIC VERSION")
print("=" * 70)
print("CONFIGURATION REQUIRED:")
print("1. configure_paths(dcim=r'YOUR_DCIM_PATH', gcp=r'YOUR_GCP_PATH', output=r'YOUR_OUTPUT_PATH')")
print("2. configure_routes(['001', '002'])  # or your route numbers")
print("")
print("USAGE:")
print("3. show_available_routes()  # optional: see what's available")
print("4. quick_diagnosis()  # optional: check RGB+MS compatibility before processing")
print("5. run_combined_rgb_ms_automation()")
print("")
print("Current configuration:")
show_current_configuration()
