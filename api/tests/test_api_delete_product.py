import pytest
import json
from api import app
from core.config import Config
from core.repository import ProductRepository
from core.history_repository import SprayHistoryRepository

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def clean_repos():
    config = Config()
    repo = ProductRepository(config)
    history_repo = SprayHistoryRepository(config)
    
    # Pre-clean
    conn = repo._get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spray_events WHERE "Spray #" = %s', (888,))
    cursor.execute('DELETE FROM products WHERE "Product" IN (%s, %s)', ("Test_Chem_A", "Test_Chem_B"))
    cursor.execute('DELETE FROM vineyard_blocks WHERE block_code = %s', ("test_block_delete",))
    conn.commit()
    
    # Create vineyard block for dependency
    cursor.execute(
        "INSERT INTO vineyard_blocks (block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (block_code) DO NOTHING",
        ("test_block_delete", "Test Merlot", 2.5, 6.0, 9.0, "VSP", "3309C")
    )
    conn.commit()
    cursor.close()
    conn.close()

    yield repo, history_repo

    # Post-clean
    conn = repo._get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spray_events WHERE "Spray #" = %s', (888,))
    cursor.execute('DELETE FROM products WHERE "Product" IN (%s, %s)', ("Test_Chem_A", "Test_Chem_B"))
    cursor.execute('DELETE FROM vineyard_blocks WHERE block_code = %s', ("test_block_delete",))
    conn.commit()
    cursor.close()
    conn.close()

def test_delete_product_with_replacement_api(client, clean_repos):
    repo, history_repo = clean_repos
    
    # 1. Add two products
    repo.add_product({"Product": "Test_Chem_A", "Primary Disease": "Powdery"})
    repo.add_product({"Product": "Test_Chem_B", "Primary Disease": "Downy"})
    
    # 2. Add a history log referencing product A
    log_data = {
        "Spray #": 888,
        "Date": "08/15/26",
        "End Time": "1200",
        "Block ": "test_block_delete",
        "Pesticide": "Test_Chem_A",
        "EPA No": "123-45",
        "Group": "test_group",
        "Active Ingredient": "test_active",
        "Pest": "test_pest",
        "Singal Word": "caution",
        "REI (h)": 4.0,
        "PHI (d)": 5,
        "Units": "lbs",
        "PHI Date": "08/20/26",
        "REI_TIME": "1600",
        "Liters/Acre": 150.0,
        "Min Dose": 1.0,
        "Max Dose": 2.0,
        "Dose/acre": 1.5,
        "Dose per L @150 l": 0.01,
        "Rate Units": "lbs",
        "Calculated Dose": 150.0,
        "Dose Units": "g",
        "Notes": "Test log entry notes"
    }
    history_repo.add_entry(log_data)
    
    # 3. Try to delete product A without replacement (should return 409 Conflict)
    resp = client.delete("/api/products/Test_Chem_A")
    assert resp.status_code == 409
    data = json.loads(resp.data.decode('utf-8'))
    assert data["status"] == "conflict"
    assert data["usage_count"] == 1
    
    # 4. Try to delete product A with replacement that doesn't exist (should return 400 Bad Request)
    resp = client.delete("/api/products/Test_Chem_A?replacement=Nonexistent_Chem")
    assert resp.status_code == 400
    
    # 5. Delete product A with replacement B (should return 200 OK)
    resp = client.delete("/api/products/Test_Chem_A?replacement=Test_Chem_B")
    assert resp.status_code == 200
    data = json.loads(resp.data.decode('utf-8'))
    assert data["status"] == "success"
    
    # 6. Verify product A is deleted, and history log now references product B
    products = repo.load_products(include_all=True)
    assert not any(p.name == "Test_Chem_A" for p in products)
    assert any(p.name == "Test_Chem_B" for p in products)
    
    entries = history_repo.load_history()
    test_logs = [e for e in entries if e.spray_number == 888]
    assert len(test_logs) == 1
    assert test_logs[0].pesticide == "Test_Chem_B"
