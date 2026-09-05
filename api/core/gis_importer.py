import io
import math
import struct
import zipfile
import xml.etree.ElementTree as ET

def calculate_geodesic_acres(coords):
    """
    Calculate area in acres from a list of [[lat, lng], ...] coordinates
    using the shoelace formula projected onto a local tangent plane.
    """
    if not coords or len(coords) < 3:
        return 0.0
    
    ref_lat = coords[0][0]
    ref_lng = coords[0][1]
    cos_lat = math.cos(math.radians(ref_lat))
    
    # Convert lat/lng to local meters
    meters = []
    for lat, lng in coords:
        x = (lng - ref_lng) * 111320.0 * cos_lat
        y = (lat - ref_lat) * 111320.0
        meters.append((x, y))
        
    # Shoelace formula
    area = 0.0
    n = len(meters)
    for i in range(n):
        p1 = meters[i]
        p2 = meters[(i + 1) % n]
        area += (p1[0] * p2[1]) - (p2[0] * p1[1])
        
    area_sq_meters = abs(area) / 2.0
    acres = area_sq_meters / 4046.8564
    return round(acres, 2)


def parse_kml_content(kml_text):
    """
    Parse KML XML content and extract the polygon outer boundary coordinates.
    Returns list of [latitude, longitude] pairs.
    """
    # Remove XML namespaces to simplify element finding
    try:
        root = ET.fromstring(kml_text)
    except Exception:
        # If encoding declaration causes issue, try bytes or stripping header
        if isinstance(kml_text, str):
            kml_text = kml_text.encode('utf-8')
        root = ET.fromstring(kml_text)
        
    # Search for coordinates tags
    coords_elements = []
    for elem in root.iter():
        # Match any tag ending with 'coordinates' (ignoring namespace)
        tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag_name.lower() == 'coordinates':
            coords_elements.append(elem)
            
    if not coords_elements:
        raise ValueError("No <coordinates> elements found in the KML file.")
        
    # Take the first or largest polygon coordinates block
    best_coords = []
    for elem in coords_elements:
        text = (elem.text or '').strip()
        if not text:
            continue
        
        raw_points = text.split()
        parsed = []
        for pt_str in raw_points:
            parts = pt_str.strip().split(',')
            if len(parts) >= 2:
                try:
                    lng = float(parts[0])
                    lat = float(parts[1])
                    parsed.append([lat, lng])
                except ValueError:
                    continue
        if len(parsed) > len(best_coords):
            best_coords = parsed
            
    if len(best_coords) < 3:
        raise ValueError("Could not find a valid polygon with at least 3 points in the KML.")
        
    # If the last coordinate equals the first, remove the duplicate closing point for Leaflet
    if len(best_coords) > 3 and best_coords[0] == best_coords[-1]:
        best_coords = best_coords[:-1]
        
    return best_coords


def parse_shp_bytes(shp_bytes):
    """
    Parse an ESRI Shapefile binary buffer (.shp) for Polygon / PolygonZ features.
    Extracts the polygon outer ring coordinates as list of [latitude, longitude] pairs.
    """
    if len(shp_bytes) < 100:
        raise ValueError("File is too small to be a valid Shapefile.")
        
    file_code, = struct.unpack(">i", shp_bytes[0:4])
    if file_code != 9994:
        raise ValueError(f"Invalid Shapefile header code: {file_code} (expected 9994).")
        
    file_length_words, = struct.unpack(">i", shp_bytes[24:28])
    version, shape_type = struct.unpack("<ii", shp_bytes[28:36])
    
    # Supported polygon shape types: 5 = Polygon, 15 = PolygonZ, 25 = PolygonM
    if shape_type not in (5, 15, 25):
        # We also allow inspecting records in case global shape_type is generic (NullShape or Polygon)
        pass
        
    # Iterate through shapefile records starting at offset 100
    offset = 100
    total_bytes = len(shp_bytes)
    polygons_found = []
    
    while offset + 8 <= total_bytes:
        rec_num, content_len = struct.unpack(">ii", shp_bytes[offset:offset+8])
        rec_content_bytes = content_len * 2
        rec_data = shp_bytes[offset+8 : offset+8+rec_content_bytes]
        offset += 8 + rec_content_bytes
        
        if len(rec_data) < 4:
            continue
            
        rec_shape_type, = struct.unpack("<i", rec_data[0:4])
        # 5: Polygon, 15: PolygonZ, 25: PolygonM
        if rec_shape_type in (5, 15, 25):
            if len(rec_data) < 44:
                continue
            # minX, minY, maxX, maxY (32 bytes = 4 doubles)
            num_parts, num_points = struct.unpack("<ii", rec_data[36:44])
            
            parts_offset = 44
            points_offset = parts_offset + (num_parts * 4)
            
            # Read parts
            parts = []
            for p_idx in range(num_parts):
                part_start, = struct.unpack("<i", rec_data[parts_offset + p_idx * 4 : parts_offset + (p_idx + 1) * 4])
                parts.append(part_start)
            parts.append(num_points)
            
            # Read points (X, Y pairs as 8-byte IEEE doubles)
            pts_count = num_points
            points_data = rec_data[points_offset : points_offset + pts_count * 16]
            if len(points_data) < pts_count * 16:
                continue
                
            raw_pts = struct.unpack(f"<{pts_count * 2}d", points_data)
            all_pts = []
            for i in range(pts_count):
                x = raw_pts[i * 2]      # Longitude
                y = raw_pts[i * 2 + 1]  # Latitude
                all_pts.append([y, x])   # [lat, lng]
                
            # Extract rings. Part 0 is usually the outer boundary
            for p_idx in range(num_parts):
                ring = all_pts[parts[p_idx] : parts[p_idx + 1]]
                if len(ring) >= 3:
                    if ring[0] == ring[-1]:
                        ring = ring[:-1]
                    polygons_found.append(ring)
                    
    if not polygons_found:
        raise ValueError("No valid polygon features found in the Shapefile.")
        
    # Return the polygon with the highest number of vertices (primary boundary)
    polygons_found.sort(key=lambda p: len(p), reverse=True)
    return polygons_found[0]


def import_boundary_file(file_storage, filename):
    """
    Universal importer for boundary files (.kml, .kmz, .shp, .zip).
    Accepts Flask FileStorage or file-like object and filename.
    Returns dict with { "coordinates": [[lat, lng], ...], "acres": float, "filename": str }
    """
    fn_lower = filename.lower()
    content = file_storage.read()
    
    coordinates = []
    
    if fn_lower.endswith('.kmz'):
        # KMZ is a zipped KML
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            kml_names = [n for n in z.namelist() if n.lower().endswith('.kml')]
            if not kml_names:
                raise ValueError("No .kml file found inside the KMZ archive.")
            # Prefer doc.kml if present
            kml_target = 'doc.kml' if 'doc.kml' in kml_names else kml_names[0]
            with z.open(kml_target) as kml_file:
                kml_text = kml_file.read()
                coordinates = parse_kml_content(kml_text)
                
    elif fn_lower.endswith('.kml'):
        coordinates = parse_kml_content(content)
        
    elif fn_lower.endswith('.zip'):
        # Shapefile ZIP archive
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            shp_names = [n for n in z.namelist() if n.lower().endswith('.shp')]
            if not shp_names:
                # Also check if it's a zipped KML with .zip extension
                kml_names = [n for n in z.namelist() if n.lower().endswith('.kml')]
                if kml_names:
                    with z.open(kml_names[0]) as kml_file:
                        coordinates = parse_kml_content(kml_file.read())
                else:
                    raise ValueError("No .shp or .kml file found inside the ZIP archive.")
            else:
                with z.open(shp_names[0]) as shp_file:
                    coordinates = parse_shp_bytes(shp_file.read())
                    
    elif fn_lower.endswith('.shp'):
        coordinates = parse_shp_bytes(content)
        
    else:
        raise ValueError(f"Unsupported file format '{filename}'. Please upload a .kml, .kmz, .shp, or .zip file.")
        
    if not coordinates or len(coordinates) < 3:
        raise ValueError("Could not extract a valid polygon boundary from the file.")
        
    acres = calculate_geodesic_acres(coordinates)
    
    return {
        "status": "success",
        "coordinates": coordinates,
        "acres": acres,
        "filename": filename
    }
