#!/usr/bin/env python3
"""
GPX Track Trimmer - Extract track segments within a specified time range
Works with Navionics and Garmin GPX files
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import argparse
import sys
import math


def parse_time(time_str):
    """Parse ISO 8601 datetime string from GPX file"""
    try:
        # Handle timezone format (Z or +00:00)
        if time_str.endswith('Z'):
            time_str = time_str[:-1] + '+00:00'
        return datetime.fromisoformat(time_str)
    except ValueError:
        # Try alternative format without microseconds
        try:
            return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return None


def format_duration(seconds):
    """Format duration in seconds to human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def calculate_speed(lat1, lon1, lat2, lon2, time_diff):
    """Calculate speed between two points in m/s"""
    if time_diff <= 0:
        return 0.0
    
    # Haversine formula to calculate distance
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance / time_diff


def trim_gpx_by_time(input_file, output_file, start_time, end_time):
    """
    Trim GPX track to include only points within the specified time range
    
    Args:
        input_file: Path to input GPX file
        output_file: Path to output GPX file
        start_time: Start time as datetime object or ISO string
        end_time: End time as datetime object or ISO string
    """
    
    # Parse start and end times if they're strings
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    # Register the namespace to preserve prefixes
    ET.register_namespace('', 'http://www.topografix.com/GPX/1/1')
    
    # Parse the GPX file
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing GPX file: {e}")
        return False
    
    # Get namespace
    namespace = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    if root.tag.startswith('{'):
        ns = root.tag[1:root.tag.index('}')]
        namespace = {'gpx': ns}
        ET.register_namespace('', ns)
    
    points_kept = 0
    points_removed = 0
    max_speed = 0.0
    first_time = None
    last_time = None
    prev_point = None
    has_navionics_speed = False
    
    # Interval tracking
    intervals = []
    prev_kept_time = None
    
    # Process all track segments
    for trk in root.findall('.//gpx:trk', namespace):
        for trkseg in trk.findall('gpx:trkseg', namespace):
            # Get all track points
            trkpts = list(trkseg.findall('gpx:trkpt', namespace))
            
            # Check each point
            for trkpt in trkpts:
                time_elem = trkpt.find('gpx:time', namespace)
                
                if time_elem is not None and time_elem.text:
                    point_time = parse_time(time_elem.text)
                    
                    if point_time:
                        # Remove points outside the time range
                        if point_time < start_time or point_time > end_time:
                            trkseg.remove(trkpt)
                            points_removed += 1
                        else:
                            points_kept += 1
                            
                            # Track intervals between kept points
                            if prev_kept_time is not None:
                                interval = (point_time - prev_kept_time).total_seconds()
                                intervals.append(interval)
                            prev_kept_time = point_time
                            
                            # Track first and last times
                            if first_time is None or point_time < first_time:
                                first_time = point_time
                            if last_time is None or point_time > last_time:
                                last_time = point_time
                            
                            # Check for Navionics speed extension
                            extensions = trkpt.find('gpx:extensions', namespace)
                            if extensions is not None:
                                for child in extensions:
                                    if child.tag == 'navionics_speed' or child.tag.endswith('}navionics_speed'):
                                        if child.text:
                                            try:
                                                speed_knots = float(child.text)
                                                max_speed = max(max_speed, speed_knots)
                                                has_navionics_speed = True
                                            except ValueError:
                                                pass
                                            break
                            
                            # For Garmin (or if no speed data), calculate from position
                            if not has_navionics_speed and prev_point is not None:
                                try:
                                    lat1 = float(prev_point['lat'])
                                    lon1 = float(prev_point['lon'])
                                    lat2 = float(trkpt.get('lat'))
                                    lon2 = float(trkpt.get('lon'))
                                    time_diff = (point_time - prev_point['time']).total_seconds()
                                    
                                    speed_ms = calculate_speed(lat1, lon1, lat2, lon2, time_diff)
                                    speed_knots = speed_ms * 1.94384  # m/s to knots
                                    max_speed = max(max_speed, speed_knots)
                                except (ValueError, TypeError):
                                    pass
                            
                            # Store current point for next iteration
                            prev_point = {
                                'lat': trkpt.get('lat'),
                                'lon': trkpt.get('lon'),
                                'time': point_time
                            }
                    else:
                        # Remove points with invalid time
                        trkseg.remove(trkpt)
                        points_removed += 1
                else:
                    # Remove points without time information
                    trkseg.remove(trkpt)
                    points_removed += 1
    
    # Write the trimmed GPX file with proper formatting
    tree.write(output_file, encoding='UTF-8', xml_declaration=True, method='xml')
    
    # Calculate elapsed time
    elapsed_seconds = 0
    if first_time and last_time:
        elapsed_seconds = (last_time - first_time).total_seconds()
    
    # Calculate interval statistics
    min_interval = min(intervals) if intervals else 0
    max_interval = max(intervals) if intervals else 0
    avg_interval = sum(intervals) / len(intervals) if intervals else 0
    
    print(f"✓ Track trimmed successfully!")
    print(f"  Points kept: {points_kept}")
    print(f"  Points removed: {points_removed}")
    
    if first_time and last_time:
        print(f"  Start time: {first_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  End time: {last_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Elapsed time: {format_duration(elapsed_seconds)}")
    
    if intervals:
        print(f"  Data point intervals:")
        print(f"    Min: {min_interval:.2f}s")
        print(f"    Max: {max_interval:.2f}s")
        print(f"    Average: {avg_interval:.2f}s")
    
    if max_speed > 0:
        max_speed_mph = max_speed * 1.15078
        max_speed_ms = max_speed * 0.514444
        speed_source = "recorded" if has_navionics_speed else "calculated"
        print(f"  Max speed ({speed_source}): {max_speed:.2f} knots ({max_speed_mph:.2f} mph, {max_speed_ms:.2f} m/s)")
    
    print(f"  Output written to: {output_file}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Trim GPX track files based on time range (Navionics and Garmin compatible)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s track.gpx output.gpx "2025-09-27T08:53:15Z" "2025-09-27T08:54:00Z"
  %(prog)s track.gpx output.gpx "2025-09-27 08:53:15" "2025-09-27 08:54:00"
        '''
    )
    
    parser.add_argument('input', help='Input GPX file')
    parser.add_argument('output', help='Output GPX file')
    parser.add_argument('start_time', help='Start time (ISO format: YYYY-MM-DDTHH:MM:SSZ)')
    parser.add_argument('end_time', help='End time (ISO format: YYYY-MM-DDTHH:MM:SSZ)')
    
    args = parser.parse_args()
    
    try:
        success = trim_gpx_by_time(
            args.input,
            args.output,
            args.start_time,
            args.end_time
        )
        sys.exit(0 if success else 1)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()