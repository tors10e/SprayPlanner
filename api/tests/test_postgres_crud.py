import pytest
import psycopg2
from core.config import Config
from core.repository import ProductRepository
from models.product import Product

@pytest.fixture
def repo():
    config = Config()
    # Force postgres database connection
    return ProductRepository(config)

def test_postgres_crud_flow(repo):
    test_product_name = "Test_Integration_Chemical"
    
    # 1. Cleanup before starting
    repo.delete_product(test_product_name)
    
    # Verify it doesn't exist
    products = repo.load_products(include_all=True)
    assert not any(p.name == test_product_name for p in products)
    
    # 2. CREATE (Add Product)
    new_product_data = {
        "Product": test_product_name,
        "Primary Disease": "Powdery",
        "FRAC": "3,11",
        "omri": "1",
        "phi": 7,
        "Max Applications": 4,
        "Container Size": 2.5,
        "units": "gal",
        "Price": 150.0,
        "Dose (avg)": 0.25,
        "Cost/Dose": 15.0,
        "package_size": 10.5,
        "price_source": "Test Source",
        "label_url": "https://example.com/label.pdf",
        "rei": 12,
        "ppe_long_sleeves_pants": True,
        "ppe_socks_shoes": True,
        "ppe_waterproof_gloves": True,
        "ppe_protective_eyewear": False,
        "min_rate": 1.5,
        "max_rate": 3.0,
        "max_annual_rate": 12.0,
        "Anthracnose": "na",
        "Black Rot": "na",
        "Bitter Rot": "na",
        "Botrytis": "na",
        "Downy": "na",
        "Phomopsis": "na",
        "Powdery": "vg"
    }
    
    repo.add_product(new_product_data)
    
    # 3. READ (Load & Verify)
    products = repo.load_products(include_all=True)
    inserted_product = next((p for p in products if p.name == test_product_name), None)
    
    assert inserted_product is not None
    assert inserted_product.name == test_product_name
    assert inserted_product.primary_disease == "Powdery"
    assert set(inserted_product.frac_codes) == {"3", "11"}
    assert inserted_product.omri == "1"
    assert inserted_product.phi == 7
    assert inserted_product.max_applications == 4
    assert inserted_product.container_size == 2.5
    assert inserted_product.units == "gal"
    assert inserted_product.price == 150.0
    assert inserted_product.dose_avg == 0.25
    assert inserted_product.cost_per_dose == 15.0
    assert inserted_product.package_size == 10.5
    assert inserted_product.price_source == "Test Source"
    assert inserted_product.label_url == "https://example.com/label.pdf"
    assert inserted_product.rei == 12
    assert inserted_product.ppe_long_sleeves_pants is True
    assert inserted_product.ppe_socks_shoes is True
    assert inserted_product.ppe_waterproof_gloves is True
    assert inserted_product.ppe_protective_eyewear is False
    assert inserted_product.min_rate == 1.5
    assert inserted_product.max_rate == 3.0
    assert inserted_product.max_annual_rate == 12.0
    assert inserted_product.effectiveness["Powdery"] == 3.0  # 'vg' maps to 3.0
    
    # 4. UPDATE (Modify values)
    updated_product_data = {
        "Product": test_product_name,
        "Primary Disease": "Downy",
        "FRAC": "M",
        "omri": "0",
        "phi": 0,
        "Max Applications": 6,
        "Container Size": 5.0,
        "units": "lbs",
        "Price": 120.0,
        "Dose (avg)": 0.5,
        "Cost/Dose": 12.0,
        "package_size": 25.0,
        "price_source": "New Source",
        "label_url": "https://example.com/new_label.pdf",
        "rei": 24,
        "ppe_long_sleeves_pants": False,
        "ppe_socks_shoes": False,
        "ppe_waterproof_gloves": False,
        "ppe_protective_eyewear": True,
        "min_rate": 2.0,
        "max_rate": 5.0,
        "max_annual_rate": 30.0,
        "Anthracnose": "na",
        "Black Rot": "na",
        "Bitter Rot": "na",
        "Botrytis": "na",
        "Downy": "e",
        "Phomopsis": "na",
        "Powdery": "na"
    }
    
    repo.update_product(test_product_name, updated_product_data)
    
    # Verify Update
    products = repo.load_products(include_all=True)
    updated_product = next((p for p in products if p.name == test_product_name), None)
    
    assert updated_product is not None
    assert updated_product.primary_disease == "Downy"
    assert updated_product.frac_codes == ["m"]
    assert updated_product.omri == "0"
    assert updated_product.phi == 0
    assert updated_product.max_applications == 6
    assert updated_product.container_size == 5.0
    assert updated_product.units == "lbs"
    assert updated_product.price == 120.0
    assert updated_product.dose_avg == 0.5
    assert updated_product.cost_per_dose == 12.0
    assert updated_product.package_size == 25.0
    assert updated_product.price_source == "New Source"
    assert updated_product.label_url == "https://example.com/new_label.pdf"
    assert updated_product.rei == 24
    assert updated_product.ppe_long_sleeves_pants is False
    assert updated_product.ppe_socks_shoes is False
    assert updated_product.ppe_waterproof_gloves is False
    assert updated_product.ppe_protective_eyewear is True
    assert updated_product.min_rate == 2.0
    assert updated_product.max_rate == 5.0
    assert updated_product.max_annual_rate == 30.0
    assert updated_product.effectiveness["Downy"] == 4.0  # 'e' maps to 4.0
    
    # 5. DELETE
    repo.delete_product(test_product_name)
    
    # Verify Deletion
    products = repo.load_products(include_all=True)
    assert not any(p.name == test_product_name for p in products)

def test_case_insensitive_product_uniqueness(repo):
    p1 = "Uniqueness_Test_Chem"
    p2 = "uniqueness_test_chem"
    p3 = "Another_Test_Chem"
    
    # 1. Cleanup
    repo.delete_product(p1)
    repo.delete_product(p2)
    repo.delete_product(p3)
    
    # 2. Add first product
    repo.add_product({"Product": p1, "Primary Disease": "Powdery"})
    
    # 3. Try to add same product name with different casing (should throw ValueError)
    with pytest.raises(ValueError) as excinfo:
        repo.add_product({"Product": p2, "Primary Disease": "Downy"})
    assert "already exists (case-insensitive duplicate)" in str(excinfo.value)
    
    # 4. Add third product
    repo.add_product({"Product": p3, "Primary Disease": "Powdery"})
    
    # 5. Try to update third product to conflict with first product's name (case-insensitive)
    with pytest.raises(ValueError) as excinfo:
        repo.update_product(p3, {"Product": p2, "Primary Disease": "Powdery"})
    assert "already exists (case-insensitive duplicate)" in str(excinfo.value)
    
    # 6. Clean up
    repo.delete_product(p1)
    repo.delete_product(p3)

def test_vineyard_blocks_crud(repo):
    conn = repo._get_connection()
    cursor = conn.cursor()
    
    # 1. Cleanup test block if exists
    cursor.execute("DELETE FROM vineyard_blocks WHERE block_code = %s", ("test_b1",))
    conn.commit()
    
    # 2. Insert block with PostGIS polygon geometry and dynamic acreage calculation
    # A polygon of ~2.44 acres centered near Clarkesville, GA
    wkt = "POLYGON((-83.5026 34.7333, -83.5026 34.7342, -83.5015 34.7342, -83.5015 34.7333, -83.5026 34.7333))"
    cursor.execute(
        '''
        INSERT INTO vineyard_blocks (block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock, block_area) 
        VALUES (%s, %s, COALESCE(ST_Area(ST_GeomFromText(%s, 4326)::geography) / 4046.8564224, %s), %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
        ''',
        ("test_b1", "Test Merlot", wkt, 2.5, 6.0, 9.0, "VSP", "3309C", wkt)
    )
    
    # 3. Insert rows
    cursor.execute("INSERT INTO vineyard_rows (block_code, row_number, row_length) VALUES (%s, %s, %s)", ("test_b1", 1, 300.0))
    cursor.execute("INSERT INTO vineyard_rows (block_code, row_number, row_length) VALUES (%s, %s, %s)", ("test_b1", 2, 280.0))
    conn.commit()
    
    # 4. Verify insertion, dynamic acreage calculation, and spatial values (Centroid)
    cursor.execute("SELECT varieties, acres, ST_AsText(block_area), ST_Y(ST_Centroid(block_area)), ST_X(ST_Centroid(block_area)) FROM vineyard_blocks WHERE block_code = %s", ("test_b1",))
    block = cursor.fetchone()
    assert block[0] == "Test Merlot"
    # Verify that the calculated acres is close to 2.44 and is NOT the fallback 2.5
    assert abs(block[1] - 2.44) < 0.2
    assert block[1] != 2.5
    assert block[2] is not None
    assert block[3] is not None
    assert block[4] is not None
    
    cursor.execute("SELECT row_number, row_length FROM vineyard_rows WHERE block_code = %s ORDER BY row_number", ("test_b1",))
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert rows[0] == (1, 300.0)
    assert rows[1] == (2, 280.0)
    
    # 5. Clean up
    cursor.execute("DELETE FROM vineyard_blocks WHERE block_code = %s", ("test_b1",))
    conn.commit()
    
    # 6. Verify cascade deletion of rows
    cursor.execute("SELECT COUNT(*) FROM vineyard_rows WHERE block_code = %s", ("test_b1",))
    assert cursor.fetchone()[0] == 0
    
    cursor.close()
    conn.close()
