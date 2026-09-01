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
    cursor.execute('DELETE FROM spray_events WHERE "Spray #" IN (%s, %s)', (101, 102))
    cursor.execute('DELETE FROM products WHERE "Product" = %s', ("Test_Clone_Chem",))
    cursor.execute('DELETE FROM vineyard_blocks WHERE block_code = %s', ("test_block_clone",))
    conn.commit()
    
    # Create vineyard block for dependency
    cursor.execute(
        "INSERT INTO vineyard_blocks (block_code, varieties, acres, vine_spacing, row_spacing, trellis_type, rootstock) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (block_code) DO NOTHING",
        ("test_block_clone", "Test Merlot", 2.5, 6.0, 9.0, "VSP", "3309C")
    )
    conn.commit()
    cursor.close()
    conn.close()

    yield repo, history_repo

    # Post-clean
    conn = repo._get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spray_events WHERE "Spray #" IN (%s, %s)', (101, 102))
    cursor.execute('DELETE FROM products WHERE "Product" = %s', ("Test_Clone_Chem",))
    cursor.execute('DELETE FROM vineyard_blocks WHERE block_code = %s', ("test_block_clone",))
    conn.commit()
    cursor.close()
    conn.close()

def test_clone_spray_group_api(client, clean_repos):
    repo, history_repo = clean_repos
    
    # 1. Add product
    repo.add_product({"Product": "Test_Clone_Chem", "Primary Disease": "Powdery"})
    
    # 2. Add history log (Spray # 101)
    log_data = {
        "Spray #": 101,
        "Date": "08/15/26",
        "End Time": "1200",
        "Block ": "test_block_clone",
        "Pesticide": "Test_Clone_Chem",
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
    
    # Verify insert
    entries = history_repo.load_history()
    source_logs = [e for e in entries if e.spray_number == 101]
    assert len(source_logs) == 1
    source_event_id = source_logs[0].event_id
    assert source_event_id is not None
    
    # 3. Call clone API to clone Spray # 101 to Spray # 102
    clone_payload = {
        "source_event_id": source_event_id,
        "new_spray_number": 102
    }
    resp = client.post("/api/history/clone_spray_group", 
                       data=json.dumps(clone_payload),
                       content_type='application/json')
    assert resp.status_code == 200
    resp_data = json.loads(resp.data.decode('utf-8'))
    assert resp_data["status"] == "success"
    
    # Verify cloned spray exists in DB
    entries = history_repo.load_history()
    cloned_logs = [e for e in entries if e.spray_number == 102]
    assert len(cloned_logs) == 1
    assert cloned_logs[0].pesticide == "Test_Clone_Chem"
    assert cloned_logs[0].block == "test_block_clone"
    
    # 4. Try cloning to an existing spray number (e.g. 101) - should fail with 400 Bad Request
    dup_payload = {
        "source_event_id": source_event_id,
        "new_spray_number": 101
    }
    resp = client.post("/api/history/clone_spray_group", 
                       data=json.dumps(dup_payload),
                       content_type='application/json')
    assert resp.status_code == 400
    resp_data = json.loads(resp.data.decode('utf-8'))
    assert "already exists" in resp_data["message"]
