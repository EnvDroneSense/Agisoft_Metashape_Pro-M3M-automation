"""
MS Multi-Dataset Combined Automation Script - GENERIC VERSION
==============================================================
Generic version with configurable paths for any project
Optimized for Metashape console compatibility
MULTISPECTRAL VARIANT - Processes TIF images from DJI Mavic 3 Multispectral

USAGE:
1. Set your paths using configure_paths()
2. Set routes using configure_routes() 
3. Run process_combined_routes()

EXAMPLE LOADING IN METASHAPE CONSOLE:
exec(open(r'YOUR_PATH/ms_combined_console_generic.py', encoding='utf-8').read())
configure_paths(dcim=r'YOUR_DCIM_PATH', gcp=r'YOUR_GCP_PATH', output=r'YOUR_OUTPUT_PATH')
configure_routes(['001', '002'])
run_combined_ms_automation()
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

def scan_dcim_folders_ms(dcim_path):
    route_folders = []
    if not os.path.exists(dcim_path):
        print(f"ERROR: DCIM folder not found: {dcim_path}")
        return route_folders
    print(f"Scanning DCIM directory for MS images: {dcim_path}")
    pattern = r'DJI_\d{12,14}_(\d{3})_.*'
    for folder in os.listdir(dcim_path):
        folder_path = os.path.join(dcim_path, folder)
        if os.path.isdir(folder_path):
            match = re.match(pattern, folder)
            if match:
                route_number = match.group(1)
                ms_patterns = ["*_MS_G.TIF", "*_MS_R.TIF", "*_MS_RE.TIF", "*_MS_NIR.TIF"]
                ms_files = []
                for pattern_ms in ms_patterns:
                    ms_pattern = os.path.join(folder_path, pattern_ms)
                    ms_files.extend(glob.glob(ms_pattern))
                if not ms_files:
                    ms_patterns_lower = ["*_ms_g.tif", "*_ms_r.tif", "*_ms_re.tif", "*_ms_nir.tif"]
                    for pattern_ms in ms_patterns_lower:
                        ms_pattern = os.path.join(folder_path, pattern_ms)
                        ms_files.extend(glob.glob(ms_pattern))
                if not ms_files:
                    all_tif = glob.glob(os.path.join(folder_path, "*MS*.TIF"))
                    all_tif.extend(glob.glob(os.path.join(folder_path, "*ms*.tif")))
                    ms_files = all_tif
                if ms_files:
                    bands = {'G': 0, 'R': 0, 'RE': 0, 'NIR': 0}
                    for img in ms_files:
                        img_name = os.path.basename(img).upper()
                        if '_MS_G.' in img_name:
                            bands['G'] += 1
                        elif '_MS_R.' in img_name:
                            bands['R'] += 1
                        elif '_MS_RE.' in img_name:
                            bands['RE'] += 1
                        elif '_MS_NIR.' in img_name:
                            bands['NIR'] += 1
                    route_folders.append({'folder_name': folder, 'folder_path': folder_path, 'route_number': route_number, 'image_count': len(ms_files), 'image_files': ms_files, 'bands': bands})
                    print(f"  Found Route {route_number}: {len(ms_files)} MS images in {folder} [G:{bands['G']}, R:{bands['R']}, RE:{bands['RE']}, NIR:{bands['NIR']}]")
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
    base_project_folder = f"combined_routes_{route_list}_MS"
    base_project_file = f"combined_routes_{route_list}_MS.psx"
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
                project_file = f"combined_routes_{route_list}_MS_v{version}.psx"
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
    print(f"Looking for MS routes: {', '.join(route_numbers)}")
    all_routes = scan_dcim_folders_ms(dcim_path)
    if not all_routes:
        print("No MS routes found in DCIM folder!")
        return []
    found_routes = []
    for route_num in route_numbers:
        route_found = False
        for route in all_routes:
            if route['route_number'] == route_num:
                found_routes.append(route)
                route_found = True
                bands = route['bands']
                print(f"  Route {route_num}: {route['image_count']} MS images in {route['folder_name']} [G:{bands['G']}, R:{bands['R']}, RE:{bands['RE']}, NIR:{bands['NIR']}]")
                break
        if not route_found:
            print(f"  Route {route_num}: Not found!")
    if len(found_routes) < 2:
        print(f"ERROR: Need at least 2 routes for combination, found {len(found_routes)}")
        return []
    return found_routes

def get_gcp_file_path(route_number, gcp_base_path):
    gcp_filename = f"gcp_route_{route_number}_MS.xml"
    gcp_file_path = os.path.join(gcp_base_path, gcp_filename)
    return gcp_file_path

def validate_routes_and_gcps(routes, gcp_base_path):
    print("Validating MS routes and GCP files...")
    valid_routes = []
    for route in routes:
        route_num = route['route_number']
        gcp_path = get_gcp_file_path(route_num, gcp_base_path)
        print(f"\nValidating Route {route_num}:")
        bands = route['bands']
        print(f"  DCIM: {route['folder_name']} ({route['image_count']} MS images [G:{bands['G']}, R:{bands['R']}, RE:{bands['RE']}, NIR:{bands['NIR']}])")
        print(f"  GCP: {os.path.basename(gcp_path)}")
        if not os.path.exists(gcp_path):
            print(f"  ERROR: GCP file not found: {gcp_path}")
            continue
        else:
            print(f"  GCP file exists")
        route_with_gcp = route.copy()
        route_with_gcp['gcp_path'] = gcp_path
        route_with_gcp['name'] = f"Route_{route_num}_MS"
        valid_routes.append(route_with_gcp)
        print(f"  Route {route_num} validation successful")
    print(f"\nValidation Summary: {len(valid_routes)}/{len(routes)} MS routes valid")
    return valid_routes

def diagnose_datasets(valid_routes):
    print("\nDIAGNOSING MS DATASET COMPATIBILITY:")
    print("=" * 50)
    total_images = sum(route['image_count'] for route in valid_routes)
    print(f"Total MS images across all routes: {total_images}")
    for route in valid_routes:
        print(f"  Route {route['route_number']}: {route['image_count']} MS images")
        sample_files = route['image_files'][:4]
        print(f"    Sample: {[os.path.basename(img) for img in sample_files]}")
        bands = route['bands']
        print(f"    Bands: G={bands['G']}, R={bands['R']}, RE={bands['RE']}, NIR={bands['NIR']}")
    folder_dates = []
    for route in valid_routes:
        folder_name = route['folder_name']
        if folder_name.startswith('DJI_'):
            date_part = folder_name.split('_')[1][:8]
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
    print(f"\nImporting MS Route {route_num}: {route_info['name']}")
    chunk = doc.addChunk()
    chunk.label = route_info['name']
    chunk.crs = Metashape.CoordinateSystem("EPSG::4326")
    print(f"  Set initial coordinate system to WGS84 (EPSG:4326)")
    print(f"  Adding {route_info['image_count']} MS images...")
    chunk.addPhotos(route_info['image_files'])
    if len(chunk.cameras) == 0:
        raise RuntimeError(f"No cameras were added for MS Route {route_num}")
    print(f"  Successfully added {len(chunk.cameras)} cameras")
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
        raise RuntimeError(f"Failed to import markers for MS Route {route_num}: {str(e)}")

def merge_chunks_with_validation(doc, chunks_to_merge):
    print(f"\nMerging {len(chunks_to_merge)} MS chunks...")
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
    coordinate_systems = set()
    for chunk in chunks_to_merge:
        if chunk.crs:
            coordinate_systems.add(str(chunk.crs))
    print(f"  Coordinate systems found: {len(coordinate_systems)}")
    for crs in coordinate_systems:
        print(f"    {crs}")
    try:
        if len(coordinate_systems) > 1:
            print("  Aligning chunks (multiple coordinate systems detected)...")
            doc.alignChunks(chunks_to_merge)
            print("  Chunks aligned successfully")
        else:
            print("  All chunks use same coordinate system - no alignment needed")
        doc.mergeChunks(chunks=chunks_to_merge, merge_markers=True, merge_tiepoints=True, copy_depth_maps=False, copy_point_clouds=False, copy_models=False, copy_elevations=False, copy_orthomosaics=False)
        print("  MS chunks merged successfully")
        chunks_after_merge = len(doc.chunks)
        print(f"  Chunks after merge: {chunks_after_merge} (was {chunks_before_merge})")
        if chunks_after_merge <= chunks_before_merge:
            raise RuntimeError("No new chunk created during merge!")
        merged_chunk = doc.chunks[-1]
        merged_chunk.label = "Merged_MS_Routes"
        print(f"  New merged MS chunk created: {merged_chunk.label}")
        print(f"  Removing {len(chunks_to_merge)} original chunks...")
        chunks_to_remove = []
        for original_chunk in chunks_to_merge:
            if original_chunk in doc.chunks:
                chunks_to_remove.append(original_chunk)
        for chunk_to_remove in reversed(chunks_to_remove):
            try:
                chunk_label = chunk_to_remove.label
                doc.remove(chunk_to_remove)
                print(f"    Removed: {chunk_label}")
            except Exception as e:
                print(f"    Error removing {chunk_to_remove.label}: {e}")
        print(f"  Successfully removed {len(chunks_to_remove)} original chunks")
        final_chunk_count = len(doc.chunks)
        if final_chunk_count != 1:
            print(f"  WARNING: Expected 1 chunk after cleanup, found {final_chunk_count}")
        else:
            print(f"  Cleanup verified: Only merged MS chunk remains")
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
        print(f"  MS merge validation completed successfully")
        return merged_chunk
    except Exception as e:
        raise RuntimeError(f"MS chunk merge failed: {str(e)}")

def match_photos(chunk):
    print(f"\nStep 2: Matching MS photos...")
    print("  Settings: Downscale=2 (half resolution for MS), Generic preselection=True, Reference preselection=True")
    chunk.matchPhotos(downscale=2, generic_preselection=True, reference_preselection=True)
    print(f"MS photo matching completed successfully")
    return True

def align_cameras(chunk):
    print(f"\nStep 3: Aligning MS cameras...")
    chunk.alignCameras(adaptive_fitting=False)
    aligned_cameras = len([cam for cam in chunk.cameras if cam.transform])
    total_cameras = len(chunk.cameras)
    alignment_ratio = aligned_cameras / total_cameras if total_cameras > 0 else 0
    print(f"MS camera alignment completed: {aligned_cameras}/{total_cameras} cameras aligned ({alignment_ratio:.1%})")
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
    report_path = os.path.join(os.path.dirname(project_path), f"processing_report_combined_routes_{route_list}_MS.pdf")
    chunk.exportReport(report_path)
    print(f"Report saved: {report_path}")
    return report_path

def process_combined_routes(route_numbers=None, dcim_path=None, gcp_path=None, output_path=None):
    if route_numbers is None: route_numbers = routes_to_combine
    if dcim_path is None: dcim_path = dcim_base_path
    if gcp_path is None: gcp_path = gcp_base_path
    if output_path is None: output_path = output_base_path
    
    # Validate configuration
    if not dcim_path or not gcp_path or not output_path or not route_numbers:
        print("ERROR: Configuration incomplete!")
        print("Please use configure_paths() and configure_routes() first")
        return False
    
    print("METASHAPE MS MULTI-ROUTE COMBINATION - GENERIC VERSION")
    print("=" * 60)
    print(f"Routes to combine: {', '.join(route_numbers)}")
    print(f"DCIM path: {dcim_path}")
    print(f"GCP path: {gcp_path}")
    print(f"Output path: {output_path}")
    print("=" * 60)
    
    try:
        print(f"\nStep 0: Finding and validating MS routes...")
        found_routes = find_routes_by_numbers(route_numbers, dcim_path)
        if not found_routes:
            print("MS route discovery failed!")
            return False
        valid_routes = validate_routes_and_gcps(found_routes, gcp_path)
        if not valid_routes:
            print("MS route validation failed!")
            return False
        diagnose_datasets(valid_routes)
        project_path, project_full_path = create_combined_project_structure(output_path, route_numbers)
        print(f"\nProject will be saved to: {project_full_path}")
        print(f"\nStep 1: Importing {len(valid_routes)} MS routes as separate chunks...")
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
                print(f"ERROR importing MS Route {route['route_number']}: {str(e)}")
                print("Stopping processing due to route import failure.")
                return False
        print(f"\nSuccessfully imported {len(imported_chunks)} MS routes")
        print(f"   Total markers imported: {total_imported_markers}")
        print(f"   Total enabled markers: {total_enabled_markers}")
        doc.save(project_full_path)
        print(f"Project saved after MS route import")
        print(f"\nStep 1.5: Merging MS chunks into single dataset...")
        try:
            merged_chunk = merge_chunks_with_validation(doc, imported_chunks)
        except Exception as e:
            print(f"ERROR during MS chunk merge: {str(e)}")
            print("Stopping processing due to merge failure.")
            return False
        doc.save(project_full_path)
        print(f"Project saved after MS chunk merge")
        
        print(f"\nStarting standard processing workflow on merged MS dataset...")
        if not match_photos(merged_chunk):
            print("MS photo matching failed!")
            doc.save(project_full_path)
            return False
        doc.save(project_full_path)
        print("Project saved after MS photo matching")
        if not align_cameras(merged_chunk):
            print("MS camera alignment failed!")
            doc.save(project_full_path)
            return False
        doc.save(project_full_path)
        print("Project saved after MS camera alignment")
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
        save_success = enhanced_save_project(doc, merged_chunk, project_full_path, "final MS processing")
        if not save_success:
            print("ERROR: Failed to save final project!")
            return False
        final_cameras = len(merged_chunk.cameras)
        final_markers = len(merged_chunk.markers)
        final_enabled = sum(1 for marker in merged_chunk.markers if marker.reference.enabled)
        final_points = merged_chunk.point_cloud.point_count if merged_chunk.point_cloud else 0
        print(f"\n{'='*60}")
        print(f"SUCCESS: Combined MS route processing completed!")
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
        print(f"\nFATAL ERROR during MS processing: {str(e)}")
        print("Processing failed!")
        return False

def show_available_routes():
    validate_configuration()
    print("\nSCANNING FOR AVAILABLE MS ROUTES")
    print("=" * 50)
    routes = scan_dcim_folders_ms(dcim_base_path)
    if not routes:
        print("No MS routes found!")
        return []
    print(f"Found {len(routes)} MS routes:")
    for route in routes:
        gcp_path = get_gcp_file_path(route['route_number'], gcp_base_path)
        gcp_exists = os.path.exists(gcp_path)
        gcp_status = "OK" if gcp_exists else "MISSING"
        bands = route['bands']
        print(f"  Route {route['route_number']}: {route['image_count']} MS images [G:{bands['G']}, R:{bands['R']}, RE:{bands['RE']}, NIR:{bands['NIR']}], GCP: {gcp_status}")
    print("=" * 50)
    return routes

def show_current_configuration():
    print("\nCURRENT MS CONFIGURATION")
    print("=" * 50)
    print(f"DCIM Base Path: {dcim_base_path}")
    print(f"GCP Base Path: {gcp_base_path}")
    print(f"Output Path: {output_base_path}")
    print(f"Routes to Combine: {', '.join(routes_to_combine) if routes_to_combine else 'Not configured'}")
    print("=" * 50)

def run_combined_ms_automation():
    validate_configuration()
    return process_combined_routes()

def quick_diagnosis():
    validate_configuration()
    print("QUICK DIAGNOSIS OF MS ROUTES TO COMBINE")
    print("=" * 50)
    found_routes = find_routes_by_numbers(routes_to_combine, dcim_base_path)
    if found_routes:
        valid_routes = validate_routes_and_gcps(found_routes, gcp_base_path)
        if valid_routes:
            diagnose_datasets(valid_routes)
            return True
    return False

print("MS MULTI-ROUTE COMBINED AUTOMATION SCRIPT LOADED - GENERIC VERSION")
print("=" * 70)
print("CONFIGURATION REQUIRED:")
print("1. configure_paths(dcim=r'YOUR_DCIM_PATH', gcp=r'YOUR_GCP_PATH', output=r'YOUR_OUTPUT_PATH')")
print("2. configure_routes(['001', '002'])  # or your route numbers")
print("")
print("USAGE:")
print("3. show_available_routes()  # optional: see what's available")
print("4. quick_diagnosis()  # optional: check compatibility before processing")
print("5. run_combined_ms_automation()")
print("")
print("Current configuration:")
show_current_configuration()
