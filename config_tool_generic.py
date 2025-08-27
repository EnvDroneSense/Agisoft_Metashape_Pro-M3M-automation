"""
Metashape Automation Configuration Tool - GENERIC VERSION
=========================================================
GUI tool for generating Metashape console commands for automation scripts.
Generic version with configurable script paths.

Features:
- Visual folder selection for DCIM, GCP, and Output paths
- Auto-detection of routes with preview
- Support for RGB, MS, and RGB+MS processing
- Single and Multiple route processing
- Generated console commands for copy-paste
- Configurable script locations

Usage:
1. Configure script paths using configure_script_paths()
2. Run this script to open the GUI configuration tool.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import glob
import re
import json
from pathlib import Path
from datetime import datetime

class MetashapeConfigTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Metashape Automation Configuration Tool - Generic")
        self.root.geometry("1100x900")  # Wider window for better command display
        self.root.resizable(True, True)
        
        # Configuration file settings
        self.config_file_path = os.path.join(os.path.dirname(__file__), "metashape_config_generic.json")
        
        # Variables
        self.dcim_path = tk.StringVar()
        self.gcp_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.script_base_path = tk.StringVar()
        self.processing_type = tk.StringVar(value="RGB")
        self.route_mode = tk.StringVar(value="Single")
        self.detected_routes = []
        self.selected_routes = []
        
        # Default script paths (can be configured)
        self.script_paths = {
            'rgb_single': 'rgb_single_automation_generic.py',
            'ms_single': 'ms_single_automation_generic.py',
            'rgb_ms_single': 'rgb_ms_single_automation_generic.py',
            'rgb_combined': 'rgb_combined_automation_generic.py',
            'ms_combined': 'ms_combined_automation_generic.py',
            'rgb_ms_combined': 'rgb_ms_combined_automation_generic.py'
        }
        
        self.setup_gui()
        self.load_config()  # Load previous configuration on startup
        self.update_preview()
    
    def setup_gui(self):
        """Create the main GUI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="Metashape Automation Configuration Tool - Generic", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # Configuration Save/Load Section
        config_manage_frame = ttk.LabelFrame(main_frame, text="Configuration Management", padding="10")
        config_manage_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_manage_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Config file path display
        ttk.Label(config_manage_frame, text="Config File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.config_path_label = ttk.Label(config_manage_frame, text=self.config_file_path, 
                                          font=("Consolas", 8), foreground="blue")
        self.config_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Config management buttons
        config_btn_frame = ttk.Frame(config_manage_frame)
        config_btn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(config_btn_frame, text="💾 Save Config", 
                  command=self.save_config).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(config_btn_frame, text="📁 Load Config", 
                  command=self.load_config_file).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(config_btn_frame, text="📤 Export Config As...", 
                  command=self.export_config).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(config_btn_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_config).grid(row=0, column=3)
        
        # Script Configuration Section
        script_frame = ttk.LabelFrame(main_frame, text="Script Configuration", padding="10")
        script_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        script_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Script Base Path
        ttk.Label(script_frame, text="Script Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(script_frame, textvariable=self.script_base_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(script_frame, text="Browse", command=self.browse_script_path).grid(row=0, column=2)
        
        # Processing Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Processing Configuration", padding="10")
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Processing Type
        ttk.Label(config_frame, text="Processing Type:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        type_frame = ttk.Frame(config_frame)
        type_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Radiobutton(type_frame, text="RGB", variable=self.processing_type, 
                       value="RGB", command=self.on_config_change).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(type_frame, text="Multispectral", variable=self.processing_type, 
                       value="MS", command=self.on_config_change).grid(row=0, column=1, padx=(0, 20))
        ttk.Radiobutton(type_frame, text="RGB+MS", variable=self.processing_type, 
                       value="Combined", command=self.on_config_change).grid(row=0, column=2)
        
        # Route Mode
        ttk.Label(config_frame, text="Route Mode:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        mode_frame = ttk.Frame(config_frame)
        mode_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Radiobutton(mode_frame, text="Single Route", variable=self.route_mode, 
                       value="Single", command=self.on_config_change).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(mode_frame, text="Multiple Routes (Combined)", variable=self.route_mode, 
                       value="Multiple", command=self.on_config_change).grid(row=0, column=1)
        
        # Path Selection Section
        path_frame = ttk.LabelFrame(main_frame, text="Path Selection", padding="10")
        path_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        row += 1
        
        # DCIM Path
        ttk.Label(path_frame, text="DCIM Folder:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(path_frame, textvariable=self.dcim_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(path_frame, text="Browse", command=self.browse_dcim).grid(row=0, column=2)
        
        # GCP Path
        ttk.Label(path_frame, text="GCP Folder:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Entry(path_frame, textvariable=self.gcp_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        ttk.Button(path_frame, text="Browse", command=self.browse_gcp).grid(row=1, column=2, pady=(5, 0))
        
        # Output Path
        ttk.Label(path_frame, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Entry(path_frame, textvariable=self.output_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        ttk.Button(path_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=(5, 0))
        
        # Route Detection Section
        route_frame = ttk.LabelFrame(main_frame, text="Route Detection", padding="10")
        route_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        route_frame.columnconfigure(0, weight=1)
        row += 1
        
        # Scan button and preview
        scan_button = ttk.Button(route_frame, text="Scan for Routes", command=self.scan_routes)
        scan_button.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Route preview
        self.route_preview = tk.Listbox(route_frame, height=6, selectmode=tk.MULTIPLE)
        self.route_preview.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.route_preview.bind('<<ListboxSelect>>', self.on_route_select)
        
        # Command Generation Section
        command_frame = ttk.LabelFrame(main_frame, text="Generated Commands", padding="10")
        command_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        command_frame.columnconfigure(0, weight=1)
        command_frame.rowconfigure(1, weight=1)
        
        # Generate button
        generate_button = ttk.Button(command_frame, text="Generate Commands", command=self.generate_commands)
        generate_button.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Commands display area with scrollbar
        commands_container = ttk.Frame(command_frame)
        commands_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        commands_container.columnconfigure(0, weight=1)
        commands_container.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar for commands
        self.commands_canvas = tk.Canvas(commands_container)
        scrollbar = ttk.Scrollbar(commands_container, orient="vertical", command=self.commands_canvas.yview)
        self.scrollable_commands_frame = ttk.Frame(self.commands_canvas)
        
        self.scrollable_commands_frame.bind(
            "<Configure>",
            lambda e: self.commands_canvas.configure(scrollregion=self.commands_canvas.bbox("all"))
        )
        
        # Bind canvas width changes to update the scrollable frame width
        self.commands_canvas.bind(
            "<Configure>",
            lambda e: self.commands_canvas.itemconfig(
                self.commands_canvas.create_window((0, 0), window=self.scrollable_commands_frame, anchor="nw"),
                width=e.width
            ) if hasattr(e, 'width') else None
        )
        
        self.commands_canvas.create_window((0, 0), window=self.scrollable_commands_frame, anchor="nw")
        self.commands_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.commands_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store reference to command widgets for clearing
        self.command_widgets = []
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready. Load config or configure script paths and select folders.")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def configure_script_paths(self, script_folder, custom_paths=None):
        """Configure script paths programmatically"""
        self.script_base_path.set(script_folder)
        if custom_paths:
            self.script_paths.update(custom_paths)
        print(f"Script paths configured for folder: {script_folder}")
    
    def browse_script_path(self):
        """Browse for script folder"""
        folder = filedialog.askdirectory(title="Select Script Folder")
        if folder:
            self.script_base_path.set(folder)
    
    def browse_dcim(self):
        """Browse for DCIM folder"""
        folder = filedialog.askdirectory(title="Select DCIM Folder")
        if folder:
            self.dcim_path.set(folder)
            self.update_preview()
    
    def browse_gcp(self):
        """Browse for GCP folder"""
        folder = filedialog.askdirectory(title="Select GCP Folder")
        if folder:
            self.gcp_path.set(folder)
    
    def browse_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
    
    def on_config_change(self):
        """Handle configuration changes"""
        self.update_preview()
    
    def update_preview(self):
        """Update the route preview based on current settings"""
        if not self.dcim_path.get():
            return
        
        self.scan_routes()
    
    def scan_routes(self):
        """Scan DCIM folder for available routes"""
        dcim_folder = self.dcim_path.get()
        if not dcim_folder or not os.path.exists(dcim_folder):
            messagebox.showwarning("Warning", "Please select a valid DCIM folder")
            return
        
        processing_type = self.processing_type.get()
        routes = self.scan_dcim_folders(dcim_folder, processing_type)
        
        self.detected_routes = routes
        self.update_route_list()
    
    def scan_dcim_folders(self, dcim_path, processing_type):
        """Scan DCIM folder for route folders based on processing type"""
        route_folders = []
        
        if not os.path.exists(dcim_path):
            return route_folders
        
        # Pattern to match route folders: DJI_YYYYMMDDHHMM_###_* or DJI_YYYYMMDDHHMMSS_###_*
        pattern = r'DJI_\d{12,14}_(\d{3})_.*'
        
        for folder in os.listdir(dcim_path):
            folder_path = os.path.join(dcim_path, folder)
            if os.path.isdir(folder_path):
                match = re.match(pattern, folder)
                if match:
                    route_number = match.group(1)
                    
                    if processing_type == "RGB":
                        # Look for RGB images
                        rgb_files = self.find_rgb_files(folder_path)
                        if rgb_files:
                            route_folders.append({
                                'folder_name': folder,
                                'route_number': route_number,
                                'image_count': len(rgb_files),
                                'type': 'RGB'
                            })
                    
                    elif processing_type == "MS":
                        # Look for MS images
                        ms_files = self.find_ms_files(folder_path)
                        if ms_files:
                            route_folders.append({
                                'folder_name': folder,
                                'route_number': route_number,
                                'image_count': len(ms_files),
                                'type': 'MS'
                            })
                    
                    elif processing_type == "Combined":
                        # Look for both RGB and MS images
                        rgb_files = self.find_rgb_files(folder_path)
                        ms_files = self.find_ms_files(folder_path)
                        if rgb_files and ms_files:
                            route_folders.append({
                                'folder_name': folder,
                                'route_number': route_number,
                                'image_count': len(rgb_files) + len(ms_files),
                                'type': 'RGB+MS',
                                'rgb_count': len(rgb_files),
                                'ms_count': len(ms_files)
                            })
        
        return sorted(route_folders, key=lambda x: x['route_number'])
    
    def find_rgb_files(self, folder_path):
        """Find RGB files in folder"""
        rgb_files = glob.glob(os.path.join(folder_path, "*_D.JPG"))
        if not rgb_files:
            rgb_files = glob.glob(os.path.join(folder_path, "*D.JPG"))
        if not rgb_files:
            rgb_files = glob.glob(os.path.join(folder_path, "*.JPG"))
            rgb_files.extend(glob.glob(os.path.join(folder_path, "*.jpg")))
        return rgb_files
    
    def find_ms_files(self, folder_path):
        """Find MS files in folder"""
        ms_patterns = ["*_MS_G.TIF", "*_MS_R.TIF", "*_MS_RE.TIF", "*_MS_NIR.TIF"]
        ms_files = []
        for pattern in ms_patterns:
            ms_files.extend(glob.glob(os.path.join(folder_path, pattern)))
        
        if not ms_files:
            ms_patterns_lower = ["*_ms_g.tif", "*_ms_r.tif", "*_ms_re.tif", "*_ms_nir.tif"]
            for pattern in ms_patterns_lower:
                ms_files.extend(glob.glob(os.path.join(folder_path, pattern)))
        
        if not ms_files:
            ms_files = glob.glob(os.path.join(folder_path, "*MS*.TIF"))
            ms_files.extend(glob.glob(os.path.join(folder_path, "*ms*.tif")))
        
        return ms_files
    
    def update_route_list(self):
        """Update the route list display"""
        self.route_preview.delete(0, tk.END)
        
        for route in self.detected_routes:
            if route['type'] == 'RGB+MS':
                display_text = f"Route {route['route_number']}: {route['rgb_count']} RGB + {route['ms_count']} MS = {route['image_count']} total images"
            else:
                display_text = f"Route {route['route_number']}: {route['image_count']} {route['type']} images"
            
            self.route_preview.insert(tk.END, display_text)
    
    def on_route_select(self, event):
        """Handle route selection"""
        selection = self.route_preview.curselection()
        self.selected_routes = [self.detected_routes[i] for i in selection]
    
    def generate_commands(self):
        """Generate Metashape console commands"""
        if not self.validate_inputs():
            return
        
        command_lines = self.build_command_lines()
        self.display_command_lines(command_lines)
    
    def validate_inputs(self):
        """Validate all required inputs"""
        if not self.script_base_path.get():
            messagebox.showerror("Error", "Please select script folder")
            return False
        
        if not self.dcim_path.get():
            messagebox.showerror("Error", "Please select DCIM folder")
            return False
        
        if not self.gcp_path.get():
            messagebox.showerror("Error", "Please select GCP folder")
            return False
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select output folder")
            return False
        
        if not self.selected_routes:
            messagebox.showerror("Error", "Please select at least one route")
            return False
        
        route_mode = self.route_mode.get()
        if route_mode == "Multiple" and len(self.selected_routes) < 2:
            messagebox.showerror("Error", "Multiple route mode requires at least 2 routes")
            return False
        
        return True
    
    def build_command_lines(self):
        """Build the command lines for Metashape console"""
        processing_type = self.processing_type.get()
        route_mode = self.route_mode.get()
        
        # Determine script filename and path
        script_folder = self.script_base_path.get()
        if route_mode == "Single":
            if processing_type == "RGB":
                script_name = self.script_paths['rgb_single']
            elif processing_type == "MS":
                script_name = self.script_paths['ms_single']
            elif processing_type == "Combined":
                script_name = self.script_paths['rgb_ms_single']
        else:
            if processing_type == "RGB":
                script_name = self.script_paths['rgb_combined']
            elif processing_type == "MS":
                script_name = self.script_paths['ms_combined']
            elif processing_type == "Combined":
                script_name = self.script_paths['rgb_ms_combined']
        
        script_path = os.path.join(script_folder, script_name).replace('\\', '/')
        
        # Build paths (escape backslashes for Python strings)
        dcim_path = self.dcim_path.get().replace('\\', '\\\\')
        gcp_path = self.gcp_path.get().replace('\\', '\\\\')
        output_path = self.output_path.get().replace('\\', '\\\\')
        
        # Get selected route numbers
        route_numbers = [route['route_number'] for route in self.selected_routes]
        
        # Build command lines as separate items
        if route_mode == "Single":
            # Single route commands
            route_num = route_numbers[0]
            command_lines = [
                f"exec(open(r'{script_path}',encoding='utf-8').read())",
                f"configure_paths(dcim=r'{dcim_path}', gcp=r'{gcp_path}', output=r'{output_path}')",
                f"process_single_route_by_number('{route_num}')"
            ]
        else:
            # Multiple route commands  
            routes_str = "', '".join(route_numbers)
            command_lines = [
                f"exec(open(r'{script_path}',encoding='utf-8').read())",
                f"configure_paths(dcim=r'{dcim_path}', gcp=r'{gcp_path}', output=r'{output_path}')",
                f"configure_routes(['{routes_str}'])",
                f"run_combined_{processing_type.lower()}_automation()"
            ]
        
        return command_lines
    
    def display_command_lines(self, command_lines):
        """Display command lines with individual copy buttons"""
        # Clear previous commands
        for widget in self.command_widgets:
            widget.destroy()
        self.command_widgets.clear()
        
        # Create command line widgets
        for i, command_line in enumerate(command_lines, 1):
            # Create frame for this command line
            line_frame = ttk.Frame(self.scrollable_commands_frame)
            line_frame.grid(row=i-1, column=0, sticky=(tk.W, tk.E), pady=2, padx=5)
            line_frame.columnconfigure(1, weight=1)
            
            # Step label
            step_label = ttk.Label(line_frame, text=f"Step {i}:", font=("Arial", 9, "bold"))
            step_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            
            # Command text (read-only entry for easy selection) - wider
            command_entry = tk.Entry(line_frame, font=("Consolas", 8), state="readonly", width=90)
            command_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
            command_entry.config(state="normal")
            command_entry.delete(0, tk.END)
            command_entry.insert(0, command_line)
            command_entry.config(state="readonly")
            
            # Copy button
            copy_button = ttk.Button(
                line_frame, 
                text="📋 Copy", 
                command=lambda cmd=command_line: self.copy_to_clipboard(cmd)
            )
            copy_button.grid(row=0, column=2, sticky=tk.E)
            
            # Store references
            self.command_widgets.extend([line_frame, step_label, command_entry, copy_button])
        
        # Make sure the scrollable frame expands properly
        self.scrollable_commands_frame.columnconfigure(0, weight=1)
        
        # Update canvas scroll region
        self.scrollable_commands_frame.update_idletasks()
        self.commands_canvas.configure(scrollregion=self.commands_canvas.bbox("all"))
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "paths": {
                    "dcim": self.dcim_path.get(),
                    "gcp": self.gcp_path.get(),
                    "output": self.output_path.get(),
                    "script_base": self.script_base_path.get()
                },
                "processing": {
                    "type": self.processing_type.get(),
                    "mode": self.route_mode.get()
                },
                "script_paths": self.script_paths,
                "routes": {
                    "detected_count": len(self.detected_routes),
                    "selected_routes": [route['route_number'] for route in self.selected_routes]
                }
            }
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.status_label.config(text=f"Configuration saved to {os.path.basename(self.config_file_path)}")
            
        except Exception as e:
            error_msg = f"Failed to save configuration: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("Save Error", error_msg)
    
    def load_config(self):
        """Load configuration from default file"""
        try:
            if not os.path.exists(self.config_file_path):
                self.status_label.config(text="No saved configuration found. Configure paths manually.")
                return
            
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load paths
            paths = config_data.get("paths", {})
            self.dcim_path.set(paths.get("dcim", ""))
            self.gcp_path.set(paths.get("gcp", ""))
            self.output_path.set(paths.get("output", ""))
            self.script_base_path.set(paths.get("script_base", ""))
            
            # Load processing settings
            processing = config_data.get("processing", {})
            self.processing_type.set(processing.get("type", "RGB"))
            self.route_mode.set(processing.get("mode", "Single"))
            
            # Load script paths if available
            saved_script_paths = config_data.get("script_paths", {})
            if saved_script_paths:
                self.script_paths.update(saved_script_paths)
            
            # Update display
            self.update_preview()
            
            # Auto-refresh routes if DCIM path exists
            if self.dcim_path.get() and os.path.exists(self.dcim_path.get()):
                self.refresh_routes()
            
            self.status_label.config(text=f"Configuration loaded from {os.path.basename(self.config_file_path)}")
            
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            self.status_label.config(text=error_msg)
            # Don't show error popup on startup, just log it
    
    def load_config_file(self):
        """Load configuration from a selected file"""
        config_file = filedialog.askopenfilename(
            title="Load Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.config_file_path)
        )
        
        if not config_file:
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load paths
            paths = config_data.get("paths", {})
            self.dcim_path.set(paths.get("dcim", ""))
            self.gcp_path.set(paths.get("gcp", ""))
            self.output_path.set(paths.get("output", ""))
            self.script_base_path.set(paths.get("script_base", ""))
            
            # Load processing settings
            processing = config_data.get("processing", {})
            self.processing_type.set(processing.get("type", "RGB"))
            self.route_mode.set(processing.get("mode", "Single"))
            
            # Load script paths if available
            saved_script_paths = config_data.get("script_paths", {})
            if saved_script_paths:
                self.script_paths.update(saved_script_paths)
            
            # Update display
            self.update_preview()
            
            # Auto-refresh routes if DCIM path exists
            if self.dcim_path.get() and os.path.exists(self.dcim_path.get()):
                self.refresh_routes()
            
            self.status_label.config(text=f"Configuration loaded from {os.path.basename(config_file)}")
            messagebox.showinfo("Config Loaded", f"Configuration successfully loaded from:\n{config_file}")
            
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("Load Error", error_msg)
    
    def export_config(self):
        """Export configuration to a selected file"""
        config_file = filedialog.asksaveasfilename(
            title="Export Configuration As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.config_file_path),
            initialfilename=f"metashape_config_generic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if not config_file:
            return
        
        try:
            config_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "exported_from": self.config_file_path,
                "paths": {
                    "dcim": self.dcim_path.get(),
                    "gcp": self.gcp_path.get(),
                    "output": self.output_path.get(),
                    "script_base": self.script_base_path.get()
                },
                "processing": {
                    "type": self.processing_type.get(),
                    "mode": self.route_mode.get()
                },
                "script_paths": self.script_paths,
                "routes": {
                    "detected_count": len(self.detected_routes),
                    "selected_routes": [route['route_number'] for route in self.selected_routes],
                    "route_details": [
                        {
                            "route_number": route['route_number'],
                            "image_count": route['image_count'],
                            "folder_name": route['folder_name']
                        } for route in self.detected_routes
                    ]
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.status_label.config(text=f"Configuration exported to {os.path.basename(config_file)}")
            messagebox.showinfo("Config Exported", f"Configuration successfully exported to:\n{config_file}")
            
        except Exception as e:
            error_msg = f"Failed to export configuration: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("Export Error", error_msg)
    
    def reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Reset Configuration", 
                              "Are you sure you want to reset all settings to defaults?\n"
                              "This will clear all current paths and settings."):
            self.dcim_path.set("")
            self.gcp_path.set("")
            self.output_path.set("")
            self.script_base_path.set("")
            self.processing_type.set("RGB")
            self.route_mode.set("Single")
            self.detected_routes = []
            self.selected_routes = []
            
            # Reset script paths to defaults
            self.script_paths = {
                'rgb_single': 'rgb_single_automation_generic.py',
                'ms_single': 'ms_single_automation_generic.py',
                'rgb_ms_single': 'rgb_ms_single_automation_generic.py',
                'rgb_combined': 'rgb_combined_automation_generic.py',
                'ms_combined': 'ms_combined_automation_generic.py',
                'rgb_ms_combined': 'rgb_ms_combined_automation_generic.py'
            }
            
            # Clear commands
            for widget in self.command_widgets:
                widget.destroy()
            self.command_widgets.clear()
            
            self.status_label.config(text="Configuration reset to defaults.")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()  # Required for clipboard to work
            # Show brief status instead of popup
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Command copied: {text[:50]}...")
        except Exception as e:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Copy failed: {str(e)}")

def configure_script_paths(script_folder, custom_paths=None):
    """Configure script paths globally"""
    global default_script_folder, default_script_paths
    default_script_folder = script_folder
    if custom_paths:
        default_script_paths.update(custom_paths)
    print(f"Default script paths configured for folder: {script_folder}")

# Global defaults
default_script_folder = None
default_script_paths = {
    'rgb_single': 'rgb_single_automation_generic.py',
    'ms_single': 'ms_single_automation_generic.py',
    'rgb_ms_single': 'rgb_ms_single_automation_generic.py',
    'rgb_combined': 'rgb_combined_automation_generic.py',
    'ms_combined': 'ms_combined_automation_generic.py',
    'rgb_ms_combined': 'rgb_ms_combined_automation_generic.py'
}

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = MetashapeConfigTool(root)
    
    # Set default script folder if configured globally
    if default_script_folder:
        app.configure_script_paths(default_script_folder, default_script_paths)
    
    root.mainloop()

if __name__ == "__main__":
    print("Metashape Automation Configuration Tool - Generic Version")
    print("=" * 60)
    print("USAGE:")
    print("1. Run this script to open the GUI")
    print("2. Configure script folder (where your automation scripts are located)")
    print("3. Configure DCIM, GCP, and Output paths")
    print("4. Select processing type and route mode")
    print("5. Scan for routes and select the ones to process")
    print("6. Generate commands and copy them to Metashape console")
    print("")
    print("CONFIGURATION (optional):")
    print("configure_script_paths(r'C:\\Your\\Scripts\\Folder')")
    print("")
    main()
