import pydicom
import matplotlib.pyplot as plt
import numpy as np
import os
from ipywidgets import interact, IntSlider
from scipy.ndimage import zoom 


def load_scan(path):
    """
    Loads all DICOM files from a directory, sorts them by slice location,
    and returns a list of pydicom dataset objects.
    """
    slices = []
    for f in os.listdir(path):
        file_path = os.path.join(path, f)
        if os.path.isfile(file_path) and f.endswith('.dcm'):
            try:
                slices.append(pydicom.dcmread(file_path))
            except pydicom.errors.InvalidDicomError:
                # Skip non-DICOM files
                continue
    
    # Sort the slices based on their 'SliceLocation' tag
    # This is crucial for correct 3D reconstruction
    slices.sort(key=lambda x: float(x.SliceLocation))
    return slices

def apply_window(hu_image, window_level, window_width):
    """
    Applies a windowing transformation to an HU image
    improving contrast between different tissues.
    """
    min_val = window_level - window_width / 2
    max_val = window_level + window_width / 2
    
    # Clip the image to the window range and scale to 0-255 for display
    return np.clip(hu_image, min_val, max_val)   
     
def get_hounsfield_volume(slices):
    """Converts a list of DICOM slices to a 3D HU volume."""
    image = np.stack([s.pixel_array for s in slices])
    image = image.astype(np.float64) # Use float for calculations
    
    # Get conversion parameters from the first slice (usually constant for a series)
    intercept = slices[0].RescaleIntercept
    slope = slices[0].RescaleSlope
    
    if slope != 1:
        image = slope * image
    
    image += intercept
    return image

def interactive_viewer(hu_volume,slice_index, window_level, window_width):
    """
    Starting from a 3D HU volume, creates an interactive viewer
    with a slider for the slice number, window level and width.
    """
    # Select the slice from the 3D HU volume
    hu_slice = hu_volume[slice_index, :, :]
    
    # Apply the windowing
    windowed_slice = apply_window(hu_slice, window_level, window_width)
    
    # Display the result
    plt.figure(figsize=(10, 10))
    plt.imshow(windowed_slice, cmap=plt.cm.gray)
    plt.title(f"Slice: {slice_index+1}/{hu_volume.shape[0]} | Window Level: {window_level} HU, Width: {window_width} HU")
    plt.axis('off')
    plt.show()

def multi_planar_reformation(dicom_folder_path):
    """
    Function that takes as input the folder path containing the
    CT scan, converts it to the HU volume, performs slincing and 
    windowing along each axis and plots them in an interactive viewer.
    """
    try:

        patient_scan_slices = load_scan(dicom_folder_path)
        hu_volume = get_hounsfield_volume(patient_scan_slices)
        
        # Get voxel spacing information
        first_slice = patient_scan_slices[0]
        last_slice = patient_scan_slices[-1]
        pixel_spacing = first_slice.PixelSpacing # [row_spacing, col_spacing] -> [dy, dx]
        slice_thickness = first_slice.SliceThickness # dz
        
        dx, dy, dz = float(pixel_spacing[1]), float(pixel_spacing[0]), float(slice_thickness)
        
        # Determine z-axis orientation
        z_pos_first = first_slice.ImagePositionPatient[2]
        z_pos_last = last_slice.ImagePositionPatient[2]
        
        # If the first slice has a smaller z-coordinate, it's a feet-first scan.
        flip_z_axis = z_pos_first < z_pos_last
        if flip_z_axis:
            print("Feet-first scan detected. Z-axis will be flipped for display.")
        else:
            print("Head-first scan detected. Z-axis is standard.")

        print(f"Voxel Dimensions: dx={dx:.4f} mm, dy={dy:.4f} mm, dz={dz:.4f} mm")
        print(f"Original Volume Shape (z, y, x): {hu_volume.shape}")
    
        # Define an interactive plotting function
        def plot_planes(slice_z, slice_y, slice_x, window_level, window_width):

            # Create a figure with 3 subplots
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))

            # --- AXIAL VIEW (original z-slices) ---
            axial_slice = hu_volume[slice_z, :, :]
            axes[0].imshow(apply_window(axial_slice, window_level, window_width), cmap=plt.cm.gray, aspect=dy/dx)
            axes[0].set_title(f"Axial Plane (z = {slice_z})")
            axes[0].set_xlabel("X-axis")
            axes[0].set_ylabel("Y-axis")
    
            # --- CORONAL VIEW (y-slices) ---
            # View (z, x) planes by slicing along y.
            coronal_slice = hu_volume[:, slice_y, :]
            if flip_z_axis:
                coronal_slice = np.flipud(coronal_slice) # Flip vertically
            axes[1].imshow(apply_window(coronal_slice, window_level, window_width), cmap=plt.cm.gray, aspect=dz/dx)
            axes[1].set_title(f"Coronal Plane (y = {slice_y})")
            axes[1].set_xlabel("X-axis")
            axes[1].set_ylabel("Z-axis")
            
            # --- SAGITTAL VIEW (x-slices) ---
            # View (z, y) planes by slicing along x.
            sagittal_slice = hu_volume[:, :, slice_x]
            if flip_z_axis:
                sagittal_slice = np.flipud(sagittal_slice) # Flip vertically
            axes[2].imshow(apply_window(sagittal_slice, window_level, window_width), cmap=plt.cm.gray, aspect=dz/dy)
            axes[2].set_title(f"Sagittal Plane (x = {slice_x})")
            axes[2].set_xlabel("Y-axis")
            axes[2].set_ylabel("Z-axis")
            
            plt.tight_layout()
            plt.show()
    
        # Create interactive sliders for all axes and windowing
        interact(
            plot_planes,
            slice_z=IntSlider(value=hu_volume.shape[0] // 2, min=0, max=hu_volume.shape[0] - 1, description='Axial Slice (Z):', continuous_update=False),
            slice_y=IntSlider(value=hu_volume.shape[1] // 2, min=0, max=hu_volume.shape[1] - 1, description='Coronal Slice (Y):', continuous_update=False),
            slice_x=IntSlider(value=hu_volume.shape[2] // 2, min=0, max=hu_volume.shape[2] - 1, description='Sagittal Slice (X):', continuous_update=False),
            window_level=IntSlider(value=40, min=-1000, max=2000, step=10, description='Level (HU):', continuous_update=False),
            window_width=IntSlider(value=400, min=1, max=5000, step=10, description='Width (HU):', continuous_update=False)
        );

    except Exception as e:
        print(f"An error occurred: {e}")

def scaled_images(dicom_folder_path):
    try:
        patient_scan_slices = load_scan(dicom_folder_path)
        hu_volume = get_hounsfield_volume(patient_scan_slices)
        
        # 1. Get original voxel spacing
        first_slice = patient_scan_slices[0]
        pixel_spacing = first_slice.PixelSpacing
        slice_thickness = first_slice.SliceThickness
        
        original_spacing = np.array([slice_thickness, pixel_spacing[0], pixel_spacing[1]], dtype=np.float32)
        print(f"Original Voxel Spacing (dz, dy, dx): {original_spacing}")
    
        # 2. Define desired new isotropic spacing (e.g., 1mm x 1mm x 1mm)
        new_spacing = [1.0, 1.0, 1.0]
    
        # 3. Calculate the zoom factor
        zoom_factor = original_spacing / new_spacing
        print(f"Calculated Zoom Factor: {zoom_factor}")
    
        # 4. Perform the resampling using scipy.ndimage.zoom
        # The 'order' parameter controls the interpolation type. 1 = bilinear, 3 = cubic.
        resampled_volume = zoom(hu_volume, zoom_factor, order=1)
        
        print(f"Original volume shape: {hu_volume.shape}")
        print(f"Resampled volume shape: {resampled_volume.shape}")
    
        # --- UPDATED PLOTTING FUNCTION (using the resampled volume) ---
        def plot_planes(slice_z, slice_y, slice_x, window_level, window_width):
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            def apply_window(image):
                min_val = window_level - window_width / 2
                max_val = window_level + window_width / 2
                return np.clip(image, min_val, max_val)
    
            # The key change: aspect=1 for all plots because the data is now isotropic!
            axes[0].imshow(apply_window(resampled_volume[slice_z, :, :]), cmap=plt.cm.gray, aspect=1)
            axes[0].set_title(f"Axial Plane (z = {slice_z})")
    
            axes[1].imshow(apply_window(np.flipud(resampled_volume[:, slice_y, :])), cmap=plt.cm.gray, aspect=1)
            axes[1].set_title(f"Coronal Plane (y = {slice_y})")
            
            axes[2].imshow(apply_window(np.flipud(resampled_volume[:, :, slice_x])), cmap=plt.cm.gray, aspect=1)
            axes[2].set_title(f"Sagittal Plane (x = {slice_x})")
            
            plt.tight_layout()
            plt.show()
    
        # Create sliders, making sure the max values match the NEW resampled shape
        interact(
            plot_planes,
            slice_z=IntSlider(value=resampled_volume.shape[0] // 2, min=0, max=resampled_volume.shape[0] - 1, description='Axial Slice (Z):'),
            slice_y=IntSlider(value=resampled_volume.shape[1] // 2, min=0, max=resampled_volume.shape[1] - 1, description='Coronal Slice (Y):'),
            slice_x=IntSlider(value=resampled_volume.shape[2] // 2, min=0, max=resampled_volume.shape[2] - 1, description='Sagittal Slice (X):'),
            window_level=IntSlider(value=40, min=-1000, max=2000, step=10, description='Level (HU):'),
            window_width=IntSlider(value=400, min=1, max=5000, step=10, description='Width (HU):')
        );

    except Exception as e:
        print(f"An error occurred: {e}")

def square_display(dicom_folder_path):
    try:
        patient_scan_slices = load_scan(dicom_folder_path)
        hu_volume = get_hounsfield_volume(patient_scan_slices)
        
        original_spacing = np.array([patient_scan_slices[0].SliceThickness] + list(patient_scan_slices[0].PixelSpacing), dtype=np.float32)
        new_spacing = [1.0, 1.0, 1.0]
        zoom_factor = original_spacing / new_spacing
        resampled_volume = zoom(hu_volume, zoom_factor, order=1)
        
        print(f"Resampled volume shape: {resampled_volume.shape}")
    
        # --- FINAL, PROPORTIONAL PLOTTING FUNCTION ---
        def plot_planes(slice_z, slice_y, slice_x, window_level, window_width):
            
            # 1. Get the dimensions of each plane from the resampled volume shape
            # shape is (z, y, x)
            shape = resampled_volume.shape
            axial_h, axial_w = shape[1], shape[2]
            coronal_h, coronal_w = shape[0], shape[2]
            sagittal_h, sagittal_w = shape[0], shape[1]
    
            # 2. Define the width ratios for the subplots
            # The width of each subplot box will be proportional to the image width
            width_ratios = [axial_w, coronal_w, sagittal_w]
    
            # 3. Calculate a proportional figure size
            # We'll use the max height and total width
            total_width = sum(width_ratios)
            max_height = max(axial_h, coronal_h, sagittal_h)
            
            # Use a scaling factor to convert pixel dimensions to inches for figsize
            # Adjust the 'dpi_scale' if the figure is too large or too small
            dpi_scale = 100 
            figsize = (total_width / dpi_scale, max_height / dpi_scale)
    
            # 4. Create the subplots with the calculated ratios and size
            fig, axes = plt.subplots(
                1, 3, 
                figsize=figsize, 
                gridspec_kw={'width_ratios': width_ratios}
            )
            
            def apply_window(image):
                min_val = window_level - window_width / 2
                max_val = window_level + window_width / 2
                return np.clip(image, min_val, max_val)
    
            # Display each plane. The aspect ratio is 1 because of our resampling.
            axes[0].imshow(apply_window(resampled_volume[slice_z, :, :]), cmap=plt.cm.gray, aspect=1)
            axes[0].set_title(f"Axial Plane (z = {slice_z})")
    
            axes[1].imshow(apply_window(np.flipud(resampled_volume[:, slice_y, :])), cmap=plt.cm.gray, aspect=1)
            axes[1].set_title(f"Coronal Plane (y = {slice_y})")
            
            axes[2].imshow(apply_window(np.flipud(resampled_volume[:, :, slice_x])), cmap=plt.cm.gray, aspect=1)
            axes[2].set_title(f"Sagittal Plane (x = {slice_x})")
            
            # Remove axis ticks for a cleaner look
            for ax in axes:
                ax.set_xticks([])
                ax.set_yticks([])
    
            plt.tight_layout(pad=0) # Use tight_layout to minimize padding
            plt.show()
    
        # The interact call remains the same
        interact(
            plot_planes,
            slice_z=IntSlider(value=resampled_volume.shape[0] // 2, min=0, max=resampled_volume.shape[0] - 1, description='Axial Slice (Z):'),
            slice_y=IntSlider(value=resampled_volume.shape[1] // 2, min=0, max=resampled_volume.shape[1] - 1, description='Coronal Slice (Y):'),
            slice_x=IntSlider(value=resampled_volume.shape[2] // 2, min=0, max=resampled_volume.shape[2] - 1, description='Sagittal Slice (X):'),
            window_level=IntSlider(value=40, min=-1000, max=2000, step=10, description='Level (HU):'),
            window_width=IntSlider(value=400, min=1, max=5000, step=10, description='Width (HU):')
        );

    except Exception as e:
        print(f"An error occurred: {e}")
        