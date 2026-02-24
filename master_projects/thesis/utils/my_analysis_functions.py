import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import pandas as pd
import os
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit
from scipy.stats import norm
import re
import warnings
import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_stderr():
    """
    A context manager to temporarily suppress stderr, useful for hiding
    output from low-level C/Fortran libraries.
    """
    # Save the original stderr so we can restore it later
    original_stderr = sys.stderr
    # On Windows, os.devnull might not be available. /dev/null is more portable.
    # We open a file handle to the 'null' device.
    devnull = open(os.devnull, 'w')
    try:
        # Redirect stderr to the null device
        sys.stderr = devnull
        # Yield control back to the 'with' block
        yield
    finally:
        # Whatever happens, restore the original stderr
        sys.stderr = original_stderr
        # Clean up the file handle
        devnull.close()
        
def extract_section(header, lines):
    for i, line in enumerate(lines):
        if header in line:
            for j in range(i + 1, len(lines)):
                data_line = lines[j].strip()
                if data_line:
                    return [float(x) for x in data_line.split(';') if x.strip()]
    return []

def bortfeld(z, D0, a, b, R):
    return D0 * np.exp(-a * (z - R)) / ((z - R)**2 + b**2)

def calculate_R80(x_data, y_data, spline_smooth_factor=0):

    x_data=np.array(x_data)
    y_data=np.array(y_data)

    """
    Calculates the distal 80% range (R_80) from Bragg peak data.
    This version uses a stderr suppressor to silence low-level library warnings.
    """
    try:
        # Use our new context manager to silence the noisy spline functions
        with suppress_stderr():
            primary_spline = UnivariateSpline(x_data, y_data, s=spline_smooth_factor)
            
            x_fine = np.linspace(min(x_data), max(x_data), 2000)
            y_fine = primary_spline(x_fine)

            if len(y_fine) == 0:
                return None

            y_max = np.max(y_fine)
            x_peak = x_fine[np.argmax(y_fine)]
            y_80 = 0.80 * y_max

            # The second spline can also produce this warning, so it is also wrapped
            shifted_spline = UnivariateSpline(x_data, y_data - y_80, s=spline_smooth_factor)
        
        # The calculation of roots is not noisy, so it can be outside the block
        all_roots = shifted_spline.roots()

    except Exception as e:
        # This still catches genuine Python errors (e.g., not enough points for a spline)
        return None

    distal_roots = all_roots[all_roots > x_peak]
    
    if len(distal_roots) > 0:
        return distal_roots[0]
    else:
        return None

def numerical_sort_key(filename):
    # Extract the first number from the filename
    numbers = re.findall(r'\d+', filename)
    return int(numbers[0]) if numbers else float('inf')

def bootstrap(x_data, y_data, n_bootstraps, s, roi_min, roi_max):
    
    x_data=np.array(x_data)
    y_data=np.array(y_data)

    sort_indices = np.argsort(x_data)
    x_data = x_data[sort_indices]
    y_data = y_data[sort_indices]

    # --- Filter the original data to the ROI ---
    roi_indices = (x_data >= roi_min) & (x_data <= roi_max)
    depths_roi = x_data[roi_indices]
    gains_roi = y_data[roi_indices]
    
    if len(depths_roi) < 10: # Sanity check
        print("FATAL ERROR: The Region of Interest is too narrow or doesn't contain enough data points.")
    else:
        print(f"Focusing analysis on ROI: Depth from {roi_min} to {roi_max}.")
        print(f"Using {len(depths_roi)} out of {len(x_data)} total data points for the analysis.")
    
        # --- Calculate R_80 for the original data (using ROI) ---
        #r80_measured = calculate_R80(depths_roi, gains_roi, spline_smooth_factor=s)
        #if r80_measured is None:
        #    print("\nFATAL ERROR: Could not calculate R_80 on the original data within the ROI.")
        #else:
        #    print(f"\nMeasured R_80 from original data (in ROI): {r80_measured:.4f}")
    
        # --- Perform the Bootstrap (on ROI data only) ---
        print(f"Performing bootstrap with {n_bootstraps} samples...")
        bootstrap_r80_values = []
        n_failures = 0
        original_indices_roi = np.arange(len(depths_roi)) # Use indices from the ROI data
    
        for i in range(n_bootstraps):
            # 1. Resample the ROI data
            bootstrap_indices = np.random.choice(original_indices_roi, size=len(original_indices_roi), replace=True)
            x_sample_raw, y_sample_raw = depths_roi[bootstrap_indices], gains_roi[bootstrap_indices]
            
            # 2. Handle duplicate x-values
            df = pd.DataFrame({'depth': x_sample_raw, 'gain': y_sample_raw})
            processed_sample = df.groupby('depth')['gain'].mean().reset_index()
            x_sample, y_sample = processed_sample['depth'].values, processed_sample['gain'].values
            
            # 3. Calculate R_80 for the cleaned-up sample
            # Ensure there are enough unique points to fit a spline
            if len(x_sample) > 3:
                 r80_sample = calculate_R80(x_sample, y_sample, spline_smooth_factor=s)
                 if r80_sample is not None:
                     bootstrap_r80_values.append(r80_sample)
                 else:
                     n_failures += 1
            else:
                n_failures += 1
    
        print(f"Bootstrap complete. {n_failures} of {n_bootstraps} samples failed.")
    
    # --- Analyze and Display Bootstrap Results ---
    bootstrap_r80_values = np.array(bootstrap_r80_values)
    
    if len(bootstrap_r80_values) > 1:
        r80_error = np.std(bootstrap_r80_values, ddof=1)
        r80_mean = np.mean(bootstrap_r80_values)
    
        print("\n--- Bootstrap Results ---")
        print(f"Best estimate for R_80 (bootstrap mean): {r80_mean:.4f}")
        print(f"Error on R_80 (bootstrap std dev):     {r80_error:.4f}")
        
        print("\n==================================================")
        print(f"  Final Result: R_80 = {r80_mean:.3f} ± {r80_error:.3f}")
        print("==================================================")

        return r80_error
    
    else:
        print("\nCould not perform bootstrap analysis. Not enough valid R_80 values were found.")
        print("TIP: Try increasing SPLINE_S_FACTOR or uncomment the diagnostic plot to investigate.")

def compute_distal_ranges(folder_path):
    # Usage
    filenames = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    filenames.sort(key=numerical_sort_key)
    
    distal_ranges = []
    
    for filename in filenames:
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                lines = f.readlines()
            
            depths = extract_section("Curve depth: [mm]", lines)
            gains = extract_section("Curve gains: [counts]", lines)
    
            if depths and gains and len(depths) == len(gains):
                distal_range = calculate_R80(depths, gains)
                distal_ranges.append((filename, distal_range))
            else:
                distal_ranges.append((filename, np.nan))  # Handle corrupted or incomplete files
    
    # Output results
    #print("File\t\t\tDistal 80% Range [mm]")
    #for fname, dr in distal_ranges:
    #    print(f"{fname:25s} {dr:.2f}" if not np.isnan(dr) else f"{fname:25s} NaN")
    
    distal_ranges = pd.DataFrame(distal_ranges,columns=['File','Distal 80% Range [mm]'])

    return distal_ranges

def compute_R80_errors(folder_path, n_bootstraps, s):
    # Usage
    filenames = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    filenames.sort(key=numerical_sort_key)
    
    distal_ranges = []
    
    for filename in filenames:
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                lines = f.readlines()
            
            depths = extract_section("Curve depth: [mm]", lines)
            gains = extract_section("Curve gains: [counts]", lines)
    
            if depths and gains and len(depths) == len(gains):
                distal_range = calculate_R80(depths, gains)
                if distal_range < 30:
                    roi_min=0
                else:
                    roi_min = distal_range-30
                roi_max = distal_range+20
                distal_range_error = bootstrap(depths,gains,n_bootstraps, s, roi_min, roi_max)
                percentage_error = (distal_range_error/distal_range)*100
                distal_ranges.append((filename, distal_range, distal_range_error,percentage_error))
            else:
                distal_ranges.append((filename, np.nan))  # Handle corrupted or incomplete files
    
    # Output results
    #print("File\t\t\tDistal 80% Range [mm]")
    #for fname, dr in distal_ranges:
    #    print(f"{fname:25s} {dr:.2f}" if not np.isnan(dr) else f"{fname:25s} NaN")
    
    distal_ranges = pd.DataFrame(distal_ranges,columns=['File','Distal 80% Range [mm]','Error [mm]','Error [%]'])

    return distal_ranges