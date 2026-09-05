import io
import struct
import zipfile
import pytest
from core.gis_importer import (
    calculate_geodesic_acres,
    parse_kml_content,
    parse_shp_bytes,
    import_boundary_file
)
from api import app

SAMPLE_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Test Farm Boundary</name>
    <Placemark>
      <name>Property Line</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -83.5030,34.7340,0
              -83.5010,34.7340,0
              -83.5010,34.7320,0
              -83.5030,34.7320,0
              -83.5030,34.7340,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
"""

def create_sample_shp_bytes():
    """Build a valid binary Polygon Shapefile buffer in memory."""
    # Points in (longitude, latitude) = (X, Y)
    pts = [
        (-83.5030, 34.7340),
        (-83.5010, 34.7340),
        (-83.5010, 34.7320),
        (-83.5030, 34.7320),
        (-83.5030, 34.7340)
    ]
    num_pts = len(pts)
    num_parts = 1
    
    # Record content: shape_type(4) + box(32) + num_parts(4) + num_points(4) + parts(4) + points(num_pts*16)
    rec_len_bytes = 4 + 32 + 4 + 4 + 4 + (num_pts * 16)
    rec_len_words = rec_len_bytes // 2
    
    rec_content = io.BytesIO()
    rec_content.write(struct.pack("<i", 5)) # Polygon
    rec_content.write(struct.pack("<4d", -83.5030, 34.7320, -83.5010, 34.7340)) # Box
    rec_content.write(struct.pack("<ii", num_parts, num_pts))
    rec_content.write(struct.pack("<i", 0)) # Part 0 start
    for x, y in pts:
        rec_content.write(struct.pack("<2d", x, y))
        
    rec_bytes = rec_content.getvalue()
    
    # File Header: 100 bytes
    total_length_bytes = 100 + 8 + len(rec_bytes)
    total_length_words = total_length_bytes // 2
    
    hdr = io.BytesIO()
    hdr.write(struct.pack(">i", 9994)) # File code
    hdr.write(b"\x00" * 20) # 5 unused 32-bit ints
    hdr.write(struct.pack(">i", total_length_words)) # File length
    hdr.write(struct.pack("<ii", 1000, 5)) # Version 1000, Shape type 5 (Polygon)
    hdr.write(struct.pack("<4d", -83.5030, 34.7320, -83.5010, 34.7340)) # Bounding box
    hdr.write(b"\x00" * 32) # Z and M ranges
    
    # Combine header + record header (number 1, length) + record content
    out = io.BytesIO()
    out.write(hdr.getvalue())
    out.write(struct.pack(">ii", 1, rec_len_words))
    out.write(rec_bytes)
    return out.getvalue()


def test_calculate_geodesic_acres():
    # Roughly a 200m x 200m square (approx 40,000 sq meters ≈ 9.88 acres)
    # Latitude ~34.73: 1 deg lat ≈ 111320m -> 0.002 deg ≈ 222.6m
    # Longitude ~ -83.5: 1 deg lng ≈ 91490m -> 0.002 deg ≈ 183m
    coords = [
        [34.7340, -83.5030],
        [34.7340, -83.5010],
        [34.7320, -83.5010],
        [34.7320, -83.5030]
    ]
    acres = calculate_geodesic_acres(coords)
    assert acres > 8.0 and acres < 12.0


def test_parse_kml_content():
    coords = parse_kml_content(SAMPLE_KML)
    assert len(coords) == 4 # duplicate closing point stripped for Leaflet
    assert coords[0] == [34.7340, -83.5030]
    assert coords[1] == [34.7340, -83.5010]


def test_parse_shp_bytes():
    shp_data = create_sample_shp_bytes()
    coords = parse_shp_bytes(shp_data)
    assert len(coords) == 4
    assert coords[0] == [34.7340, -83.5030]
    assert coords[1] == [34.7340, -83.5010]


def test_import_boundary_kml():
    bio = io.BytesIO(SAMPLE_KML.encode('utf-8'))
    result = import_boundary_file(bio, "test_farm.kml")
    assert result["status"] == "success"
    assert len(result["coordinates"]) == 4
    assert result["acres"] > 0
    assert result["filename"] == "test_farm.kml"


def test_import_boundary_kmz():
    # Build KMZ archive in memory
    kmz_io = io.BytesIO()
    with zipfile.ZipFile(kmz_io, "w") as z:
        z.writestr("doc.kml", SAMPLE_KML)
    kmz_io.seek(0)
    
    result = import_boundary_file(kmz_io, "test_farm.kmz")
    assert result["status"] == "success"
    assert len(result["coordinates"]) == 4


def test_import_boundary_shp_zip():
    shp_data = create_sample_shp_bytes()
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w") as z:
        z.writestr("farm_boundary.shp", shp_data)
        z.writestr("farm_boundary.shx", b"\x00" * 100)
    zip_io.seek(0)
    
    result = import_boundary_file(zip_io, "farm_boundary.zip")
    assert result["status"] == "success"
    assert len(result["coordinates"]) == 4


def test_upload_boundary_api_endpoint():
    client = app.test_client()
    data = {
        'file': (io.BytesIO(SAMPLE_KML.encode('utf-8')), 'estate_boundary.kml')
    }
    response = client.post('/api/farm/upload-boundary', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["status"] == "success"
    assert len(res_json["coordinates"]) == 4
    assert res_json["acres"] > 0
