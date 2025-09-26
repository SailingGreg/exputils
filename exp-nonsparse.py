#!/usr/bin/env python3
"""
Final Clean Converter - Creates perfect wide format with just header + data
Enhanced with daylight saving time conversion support
"""

import pandas as pd
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone
import pytz

def create_parameter_mapping():
    """Create mapping based on the actual CSV headers."""
    return {
        0: 'Utc', 1: 'BSP', 2: 'AWA', 3: 'AWS', 4: 'TWA', 5: 'TWS', 6: 'TWD',
        7: 'RudderFwd', 10: 'Leeway', 11: 'Set', 12: 'Drift', 13: 'HDG',
        14: 'AirTemp', 15: 'SeaTemp', 16: 'Baro', 17: 'Depth', 18: 'Heel',
        19: 'Trim', 20: 'Rudder', 21: 'Tab', 22: 'Forestay', 23: 'Downhaul',
        24: 'MastAng', 25: 'FStayLen', 26: 'MastButt', 27: 'Load_S', 28: 'Load_P',
        29: 'Rake', 30: 'Volts', 32: 'ROT', 39: 'GpQual', 41: 'PDOP',
        43: 'GpsNum', 44: 'GpsAge', 45: 'Altitude', 46: 'GeoSep', 47: 'GpsMode',
        48: 'Lat', 49: 'Lon', 50: 'COG', 51: 'SOG', 52: 'DiffStn', 60: 'Error',
        61: 'RunnerS', 62: 'RunnerP', 67: 'Vang', 68: 'Trav', 69: 'Main',
        71: 'KeelAng', 72: 'KeelHt', 73: 'Board', 74: 'EngOilPres', 75: 'RPM_1',
        76: 'RPM_2', 77: 'Board_P', 78: 'Board_S', 84: 'DistToLn', 85: 'RchTmToLn',
        86: 'RchDtToLn', 146: 'GPS_time', 147: 'TWD_Plus90', 148: 'TWD_Minus90',
        151: 'Downhaul2', 161: 'Mk_Lat', 162: 'Mk_Lon', 163: 'Port_lat',
        164: 'Port_lon', 165: 'Stbd_lat', 166: 'Stbd_lon', 167: 'HPE', 168: 'RH',
        169: 'Lead_P', 170: 'Lead_S', 171: 'BackStay', 256: 'GPS_tOffset',
        257: 'Heave', 258: 'MWA', 259: 'MWS', 260: 'Boom', 268: 'Twist',
        272: 'TWDTwisted', 273: 'TackLossT', 274: 'TackLossD', 277: 'TrimRate',
        278: 'HeelRate', 351: 'DepthAft', 373: 'TWSGradient', 382: 'CANLoad_Percent',
        383: 'FastPkErr'
    }

def excel_serial_to_datetime(serial_date):
    """Convert Excel serial date number to datetime object."""
    # Excel's epoch starts at 1900-01-01, but there's a leap year bug
    # Excel incorrectly treats 1900 as a leap year
    excel_epoch = datetime(1899, 12, 30, tzinfo=timezone.utc)
    return excel_epoch + pd.Timedelta(days=serial_date)

def get_system_timezone():
    """Detect the system timezone."""
    try:
        # Try to get system timezone name
        local_tz_name = time.tzname[time.daylight]  # Gets DST name if available
        if not local_tz_name:
            local_tz_name = time.tzname[0]  # Fallback to standard time
        
        # Map common timezone abbreviations to full names
        tz_mapping = {
            'GMT': 'Europe/London',
            'BST': 'Europe/London', 
            'EST': 'US/Eastern',
            'EDT': 'US/Eastern',
            'CST': 'US/Central',
            'CDT': 'US/Central',
            'MST': 'US/Mountain',
            'MDT': 'US/Mountain',
            'PST': 'US/Pacific',
            'PDT': 'US/Pacific'
        }
        
        if local_tz_name in tz_mapping:
            return tz_mapping[local_tz_name]
        
        # Fallback to Europe/London for GMT-like systems
        return 'Europe/London'
    except:
        return 'Europe/London'

def get_timezone_display_name(timezone_name, sample_datetime=None):
    """Get display name that shows actual timezone (e.g., 'GMT Daylight')."""
    try:
        tz = pytz.timezone(timezone_name)
        
        # Use sample datetime to determine if DST is active
        if sample_datetime:
            dt_utc = excel_serial_to_datetime(sample_datetime)
            dt_local = dt_utc.astimezone(tz)
            tz_name = dt_local.strftime('%Z')  # Gets actual timezone abbreviation (BST, GMT, etc.)
        else:
            # Fallback - check if timezone typically observes DST
            now_utc = datetime.now(timezone.utc)
            now_local = now_utc.astimezone(tz)
            tz_name = now_local.strftime('%Z')
        
        # Create readable names
        if tz_name in ['BST']:
            return 'GMT_Daylight'
        elif tz_name in ['GMT']:
            return 'GMT_Standard'
        elif tz_name in ['EDT']:
            return 'Eastern_Daylight'
        elif tz_name in ['EST']:
            return 'Eastern_Standard'
        elif tz_name in ['PDT']:
            return 'Pacific_Daylight'
        elif tz_name in ['PST']:
            return 'Pacific_Standard'
        else:
            return f'{tz_name}'
            
    except:
        return 'Local_Time'

def get_timezone_abbreviation(timezone_name, sample_datetime=None):
    """Get a clean abbreviation for timezone names."""
    timezone_abbrevs = {
        'Europe/London': 'BST_GMT',
        'US/Eastern': 'EST_EDT', 
        'US/Central': 'CST_CDT',
        'US/Mountain': 'MST_MDT',
        'US/Pacific': 'PST_PDT',
        'Australia/Sydney': 'AEST_AEDT',
        'Europe/Paris': 'CET_CEST',
        'Europe/Berlin': 'CET_CEST',
        'Asia/Tokyo': 'JST',
        'Asia/Shanghai': 'CST'
    }
    
    if timezone_name in timezone_abbrevs:
        return timezone_abbrevs[timezone_name]
    else:
        # Fallback: clean up the timezone name
        return timezone_name.replace('/', '_').replace('-', '_')

def get_dst_offset_hours(timezone_name, sample_timestamp):
    """Get the DST offset in hours for a given timezone and timestamp."""
    try:
        tz = pytz.timezone(timezone_name)
        # Convert sample timestamp to datetime to check DST
        dt_utc = excel_serial_to_datetime(sample_timestamp)
        dt_local = dt_utc.astimezone(tz)
        
        # Get UTC offset in seconds, convert to hours
        offset_seconds = dt_local.utcoffset().total_seconds()
        offset_hours = offset_seconds / 3600
        
        return offset_hours
    except:
        # Default for Europe/London
        return 1.0  # BST is UTC+1

def convert_to_clean_wide_format(input_file, output_file=None, apply_dst=False, timezone_name=None):
    """
    Convert to clean wide format with proper header verification.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (optional)
        apply_dst: Whether to apply daylight saving time conversion
        timezone_name: Target timezone for DST conversion (auto-detected if None)
    """
    
    # Auto-detect timezone if not specified and DST is requested
    if apply_dst and timezone_name is None:
        timezone_name = get_system_timezone()
        print(f"Auto-detected timezone: {timezone_name}")
    elif timezone_name is None:
        timezone_name = 'Europe/London'  # Default fallback
    print(f"Reading: {input_file}")
    
    # Read CSV with dtype specification to avoid warnings
    df = pd.read_csv(input_file, dtype=str, low_memory=False)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Find the start of actual data (skip all metadata rows)
    # Look for rows where UTC column has actual timestamp values (> 40000)
    data_start = None
    for i in range(len(df)):
        utc_val = df.iloc[i, 1]  # UTC column
        try:
            if pd.notna(utc_val) and float(utc_val) > 40000:  # Real timestamp
                data_start = i
                break
        except:
            continue
    
    if data_start is None:
        print("Could not find start of actual data!")
        return None
    
    print(f"Found actual data starting at row {data_start + 1}")
    
    # Extract data rows only
    data_df = df.iloc[data_start:].copy()
    data_df.reset_index(drop=True, inplace=True)
    
    print(f"Processing {len(data_df)} actual data rows")
    
    # Collect all parameter-value data
    all_data = []
    
    for row_idx, row in data_df.iterrows():
        utc_time = row.iloc[1]  # UTC from column 1
        
        if pd.isna(utc_time):
            continue

        if (utc_time == "Utc" or float(utc_time) < 40000):
            continue
        
        # Process alternating columns starting from column 2
        for col_idx in range(2, len(row) - 1, 2):  # Step by 2
            param_id = row.iloc[col_idx]
            value = row.iloc[col_idx + 1]
            
            if pd.notna(param_id) and pd.notna(value):
                try:
                    param_id_num = int(float(param_id))
                    value_num = float(value)
                    
                    all_data.append({
                        'UTC': float(utc_time),
                        'Parameter': param_id_num,
                        'Value': value_num
                    })
                except:
                    continue
        
        # Progress indicator
        if row_idx % 1000 == 0:
            print(f"  Processed {row_idx:,} rows...")
    
    print(f"Collected {len(all_data):,} parameter-value data points")
    
    if not all_data:
        print("No valid data found!")
        return None
    
    # Create dataframe and pivot
    work_df = pd.DataFrame(all_data)
    
    print("Pivoting to wide format...")
    wide_df = work_df.pivot_table(
        index='UTC',
        columns='Parameter',
        values='Value',
        aggfunc='first'
    )
    
    # Rename columns first
    param_mapping = create_parameter_mapping()
    new_columns = {}
    for param_id in wide_df.columns:
        if param_id in param_mapping:
            new_columns[param_id] = param_mapping[param_id]
        else:
            new_columns[param_id] = f'Param_{int(param_id)}'
    
    wide_df.rename(columns=new_columns, inplace=True)
    
    # Reset index to convert the index (UTC timestamps) to a column
    wide_df.reset_index(inplace=True)
    
    # Sort by UTC timestamps first (ensures consistent ordering)
    wide_df.sort_values('UTC', inplace=True)
    
    # Apply daylight saving time conversion AFTER sorting
    time_column_name = 'UTC'
    if apply_dst:
        print(f"Converting UTC to local time ({timezone_name})...")
        try:
            # Simple approach: just add the timezone offset to UTC timestamps
            sample_utc = wide_df['UTC'].iloc[0]
            offset_hours = get_dst_offset_hours(timezone_name, sample_utc)
            offset_days = offset_hours / 24.0  # Convert hours to Excel day fraction
            
            print(f"Applying timezone offset: +{offset_hours} hours (+{offset_days:.6f} days)")
            
            # Simple addition - no complex conversions
            #_df['UTC'] = wide_df['UTC'] + offset_days.round(12)
            wide_df['UTC'] = (wide_df['UTC'] + offset_days).round(5)
            
            print(f"✓ Successfully converted timestamps to {timezone_name}")
            
            # Show sample conversion for verification
            if len(wide_df) > 0:
                sample_local = wide_df['UTC'].iloc[0]
                local_dt = excel_serial_to_datetime(sample_local)
                
                print(f"Sample conversion:")
                print(f"  UTC: {sample_utc:.6f} -> Local: {sample_local:.6f}")
                print(f"  Local time: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Difference: {(sample_local - sample_utc) * 24:.1f} hours")
                
            # Use proper display name for the column
            display_name = get_timezone_display_name(timezone_name, sample_local)
            wide_df.rename(columns={'UTC': display_name}, inplace=True)
            time_column_name = display_name
                
        except Exception as e:
            print(f"Warning: Daylight saving conversion failed: {e}")
            print("Continuing with UTC timestamps")
    
    # Add ONLY the parameter ID verification row at the top
    print("Adding parameter ID verification row...")
    
    # Use the complete parameter mapping
    param_mapping = create_parameter_mapping()
    
    # Create reverse mapping (column name -> parameter ID)
    reverse_mapping = {v: k for k, v in param_mapping.items()}
    
    # Create verification row using the complete mapping
    verification_row = {}
    '''
    for col in wide_df.columns:
        if 'Time' in col or col == 'UTC':  # Handles GMT_Daylight_Time, GMT_Standard_Time, etc.
            verification_row[col] = 0  # UTC parameter ID
    '''
    for col in wide_df.columns:
        if col == time_column_name or 'GMT' in col or 'Daylight' in col or col == 'UTC':
            verification_row[col] = '0.0'  # Use string '0' not integer 0
            print(f"  {col} -> parameter 0.0 (UTC/Time column)")
        elif col in reverse_mapping:
            verification_row[col] = reverse_mapping[col]
            print(f"  {col} -> parameter {reverse_mapping[col]}")
        elif col.startswith('Param_'):
            # Extract parameter ID from Param_XXX format
            param_id = int(col.replace('Param_', ''))
            verification_row[col] = param_id
            print(f"  {col} -> parameter {param_id}")
        else:
            verification_row[col] = ''
            print(f"  {col} -> NO PARAMETER ID FOUND")
    
    # Insert verification row at the top
    verification_df = pd.DataFrame([verification_row])
    final_df = pd.concat([verification_df, wide_df], ignore_index=True)

    #final_df = wide_df.copy()
    
    # Generate output filename
    if output_file is None:
        input_path = Path(input_file)
        suffix = "_dst" if apply_dst else "_clean"
        output_file = input_path.parent / f"{input_path.stem}{suffix}.csv"
    
    # Save with error handling for Windows permission issues
    print(f"Saving to: {output_file}")
    try:
        # Use standard pandas CSV writing - should be fast and clean now
        final_df.to_csv(output_file, index=False)
        print(f"✓ Successfully saved to: {output_file}")
    except PermissionError:
        # Try alternative filename if permission denied
        input_path = Path(input_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if apply_dst:
            alt_output = input_path.parent / f"{input_path.stem}_dst_{timestamp}.csv"
        else:
            alt_output = input_path.parent / f"{input_path.stem}_clean_{timestamp}.csv"
        
        print(f"⚠️  Permission denied for {output_file}")
        print(f"🔄 Trying alternative filename: {alt_output}")
        
        try:
            final_df.to_csv(alt_output, index=False)
            print(f"✓ Successfully saved to: {alt_output}")
            output_file = alt_output
        except Exception as e2:
            print(f"✗ Failed to save alternative file: {e2}")
            print("💡 Suggestions:")
            print("   - Close Excel if the file is open")
            print("   - Check if the file is read-only")
            print("   - Try running as administrator")
            print("   - Specify a different output path with -o")
            raise e2
    except Exception as e:
        print(f"✗ Unexpected error saving file: {e}")
        raise e
    
    print(f"\n✓ Perfect! Clean conversion completed!")
    print(f"Structure:")
    time_col_name = f'LocalTime_{timezone_name.replace("/", "_")}' if apply_dst else 'UTC'
    print(f"  Column names: {time_col_name}, BSP, AWA, Depth, Heel, etc.")
    print(f"  Row 1: Parameter IDs for verification (0, 1, 2, 17, 18, etc.)")
    print(f"  Row 2+: {len(wide_df):,} rows of actual sailing data")
    print(f"  Total columns: {len(final_df.columns)}")
    
    if apply_dst:
        print(f"  Time zone: {timezone_name} (with daylight saving adjustments)")
        if timezone_name == 'Europe/London':
            print(f"  Note: Times will be in BST (summer) or GMT (winter) as appropriate")
    
    # Verify key mappings using reverse mapping
    bsp_param = reverse_mapping.get('BSP', 'NOT FOUND')
    depth_param = reverse_mapping.get('Depth', 'NOT FOUND') 
    heel_param = reverse_mapping.get('Heel', 'NOT FOUND')
    
    print(f"\nVerification:")
    print(f"  BSP -> Parameter {bsp_param}")
    print(f"  Depth -> Parameter {depth_param}")
    print(f"  Heel -> Parameter {heel_param}")
    
    return final_df

def main():
    parser = argparse.ArgumentParser(description='Convert sailing data to clean wide format with optional daylight saving time conversion')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('output_file', nargs='?', help='Output CSV file path (optional)')
    parser.add_argument('-d', '--dst', action='store_true', 
                       help='Apply daylight saving time conversion to UTC timestamps')
    parser.add_argument('-t', '--timezone', default=None,
                       help='Target timezone for DST conversion (auto-detected if not specified). Examples: US/Eastern, US/Pacific, Australia/Sydney')
    parser.add_argument('-o', '--output', help='Alternative way to specify output file')
    
    args = parser.parse_args()
    
    # Handle output file specification
    if args.output:
        args.output_file = args.output
    
    # Validate timezone if DST is requested
    if args.dst:
        if args.timezone:
            try:
                pytz.timezone(args.timezone)
                print(f"Using specified timezone: {args.timezone}")
            except pytz.exceptions.UnknownTimeZoneError:
                print(f"Error: Unknown timezone '{args.timezone}'")
                print("Common timezones: US/Eastern, US/Central, US/Mountain, US/Pacific, Europe/London, Europe/Paris, Australia/Sydney")
                return 1
        else:
            detected_tz = get_system_timezone()
            print(f"Auto-detected system timezone: {detected_tz}")
            args.timezone = detected_tz
    
    # Check if output file already exists and is potentially locked
    if args.output_file and Path(args.output_file).exists():
        print(f"⚠️  Output file {args.output_file} already exists")
        print("💡 If you get permission errors, the file might be open in Excel")
    
    try:
        result = convert_to_clean_wide_format(
            args.input_file, 
            args.output_file, 
            apply_dst=args.dst,
            timezone_name=args.timezone
        )
        if result is not None:
            print("✓ Final clean conversion completed!")
            return 0
        else:
            print("✗ Conversion failed!")
            return 1
    except PermissionError as e:
        print(f"✗ Permission Error: {e}")
        print("💡 Common solutions:")
        print("   - Close the output file if it's open in Excel")
        print("   - Use a different output filename with -o filename.csv")
        print("   - Run the command prompt as administrator")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("v55")
    exit(main())