#
# program to parse ocr 'csv' polars to create expedition polars
# with Froude scaling support and 180° extrapolation
#
# recommendation is to add the beat/run figures and save this as the 'input' text file
#
# OCR data via https://jieter.github.io/orc-data/site/#extremes
#
import sys
import argparse
import numpy as np

# the extension we add to the generated file
fext = '-polar.txt'

if sys.version_info < (3,6):
    print ("python 3.6 needed for formatting")
    exit(0)

# Set up command line argument parsing
parser = argparse.ArgumentParser(description='Parse OCR CSV polars to create expedition polars with optional Froude scaling and 180° extrapolation')
parser.add_argument('filename', help='The file to process')
parser.add_argument('-s', '--scale', type=float, metavar='PERCENT', 
                   help='Scale BSP figures by percentage using Froude scaling (e.g., 121 for 121%% length)')
parser.add_argument('-a', '--add180', action='store_true',
                   help='Add 180° data points using polynomial extrapolation with bounds checking')

args = parser.parse_args()
fname = args.filename
scale_percent = args.scale
add_180 = args.add180

# Calculate Froude scaling factor
froude_factor = 1.0
if scale_percent is not None:
    # Froude scaling: speed scales with square root of length ratio
    # scale_percent is the percentage scaling (e.g., 121 means 121% = 1.21 ratio)
    length_ratio = scale_percent / 100.0
    froude_factor = length_ratio ** 0.5
    print(f'Applying Froude scaling: {scale_percent}% length scaling = {froude_factor:.4f} speed factor')

if add_180:
    print('Will add 180° extrapolation using polynomial fitting with bounds checking')

fbase = fname.split('.')[0] # remove the extension

try:
    fd = open(fname, "r")
except:
    print(f'Error opening "{fname}"')
    exit(0)

lines = fd.readlines()
fd.close()

# now split based on line and build array
cnt = 1
knots = []
angls = []

for line in lines:
    line = line.strip('\n')
    ents = line.split(';') 
    
    if (cnt == 1): # first line
        idx = 1
        for val in ents:
            if idx != 1:
                knots.append(val)
            idx = idx + 1
        print(f'Winds in the polar for {fbase} are {knots}')
    else:
        angls.append(ents)
        idx = 0
    cnt = cnt + 1

# we need to sort the angles as ocr appends the vmg figures
angls = sorted(angls, key=lambda x: float(x[0]))

def extrapolate_180_speed(angles_speeds, wind_idx):
    """
    Extrapolate speed at 180° using polynomial fitting with bounds checking
    angles_speeds: list of [angle, speed1, speed2, ...] entries
    wind_idx: index of wind speed column to process (1-based)
    """
    # Extract downwind angles and speeds (typically 120° and above)
    downwind_data = []
    max_vmg_speed = 0
    
    for entry in angles_speeds:
        angle = float(entry[0])
        if len(entry) > wind_idx and entry[wind_idx] != '' and float(entry[wind_idx]) > 0:
            speed = float(entry[wind_idx])
            if angle >= 120:  # Consider downwind angles
                downwind_data.append((angle, speed))
            # Track maximum speed for VMG bounds checking
            if angle >= 140 and angle <= 170:  # Typical VMG downwind range
                max_vmg_speed = max(max_vmg_speed, speed)
    
    if len(downwind_data) < 3:  # Need at least 3 points for reasonable fit
        return None
    
    # Sort by angle
    downwind_data.sort()
    angles = [d[0] for d in downwind_data]
    speeds = [d[1] for d in downwind_data]
    
    # Use only the last 4-5 points for extrapolation to avoid influence of reaches
    if len(downwind_data) > 4:
        angles = angles[-4:]
        speeds = speeds[-4:]
    
    try:
        # Fit polynomial (degree 2 or 3 depending on data points)
        degree = min(2, len(angles) - 1)
        coeffs = np.polyfit(angles, speeds, degree)
        poly = np.poly1d(coeffs)
        
        # Extrapolate to 180°
        speed_180 = poly(180.0)
        
        # Bounds checking
        # 1. Speed at 180° should not be higher than the best VMG downwind speed
        if max_vmg_speed > 0:
            speed_180 = min(speed_180, max_vmg_speed * 0.95)  # Cap at 95% of max VMG
        
        # 2. Speed at 180° should not be less than 70% of the last data point
        last_speed = speeds[-1]
        speed_180 = max(speed_180, last_speed * 0.7)
        
        # 3. Ensure positive speed
        speed_180 = max(speed_180, 0.1)
        
        return speed_180
        
    except Exception as e:
        print(f"Warning: Could not extrapolate 180° for wind index {wind_idx}: {e}")
        return None

# Add 180° data if requested and not already present
if add_180:
    # Check if 180° already exists
    has_180 = any(float(entry[0]) == 180.0 for entry in angls if len(entry) > 0)
    
    if not has_180:
        # Create 180° entry
        new_180_entry = ['180.0']
        
        # For each wind speed, extrapolate 180° value
        for wind_idx in range(1, len(knots) + 1):
            speed_180 = extrapolate_180_speed(angls, wind_idx)
            if speed_180 is not None:
                new_180_entry.append(f"{speed_180:.2f}")
            else:
                new_180_entry.append('0.00')  # Fallback
        
        angls.append(new_180_entry)
        angls = sorted(angls, key=lambda x: float(x[0]))  # Re-sort with new 180° entry
        print("Added 180° extrapolated data points")
    else:
        print("180° data already exists in polar")

# Add scaling suffix to filename if scaling is applied
output_suffix = fext
suffix_parts = []

if scale_percent is not None:
    suffix_parts.append(f'scaled{int(scale_percent)}')

if add_180:
    suffix_parts.append('180deg')

if suffix_parts:
    output_suffix = f'-{"-".join(suffix_parts)}{fext}'

try:
    of = open(fbase + output_suffix, "w")
except:
    print(f"Can't open output file {fbase + output_suffix}")
    exit(0)

idx = 1
for spd in knots:
    str_line = spd
    for ent in angls:
        if len(ent) > idx and ent[idx] != '':
            try:
                if (float(ent[0]) == 0): # we allow the first entry to be an angle of '0'
                    # Apply Froude scaling to the speed value
                    scaled_speed = float(ent[idx]) * froude_factor
                    str_line = str_line + "\t" + ent[0] + "\t" + f"{scaled_speed:.2f}"
                elif (float(ent[idx]) > 0.0): # else it has to have velocity
                    # Apply Froude scaling to the speed value
                    scaled_speed = float(ent[idx]) * froude_factor
                    str_line = str_line + "\t" + ent[0] + "\t" + f"{scaled_speed:.2f}"
            except (ValueError, IndexError):
                continue  # Skip invalid entries
    idx = idx + 1
    of.write(str_line + '\n')

of.close()
print(f"Polar written to {fbase + output_suffix}")
if scale_percent is not None:
    print(f"BSP values scaled by Froude factor: {froude_factor:.4f}")

# end of file