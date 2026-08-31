import pytest
from core.config import Config
from core.history_repository import SprayHistoryRepository
from models.spray_history import SprayHistoryEntry

@pytest.fixture
def history_repo():
    config = Config()
    return SprayHistoryRepository(config)

def test_history_crud_flow(history_repo):
    # 0. Clean up previous runs
    conn = history_repo._get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM spray_history WHERE "Pesticide" = %s', ("Test_Pesticide_Log",))
    cursor.execute('DELETE FROM products WHERE "Product" = %s', ("Test_Pesticide_Log",))
    conn.commit()
    cursor.close()
    conn.close()

    # 1. Add unique entry
    new_entry_data = {
        "Spray #": 99,
        "Date": "08/15/26",
        "End Time": "1200",
        "Block ": "cs",
        "Pesticide": "Test_Pesticide_Log",
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
    
    # Create
    new_id = history_repo.add_entry(new_entry_data)
    assert new_id is not None
    
    # 2. Read & Verify
    entries = history_repo.load_history()
    inserted = next((e for e in entries if e.entry_id == new_id), None)
    
    assert inserted is not None
    assert inserted.spray_number == 99
    assert inserted.date == "08/15/26"
    assert inserted.end_time == "1200"
    assert inserted.block == "cs"
    assert inserted.pesticide == "Test_Pesticide_Log"
    assert inserted.rei_h == 4.0
    assert inserted.phi_d == 5
    assert inserted.notes == "Test log entry notes"
    
    # 3. Update
    updated_entry_data = {
        "Spray #": 99,
        "Date": "08/15/26",
        "End Time": "1300",
        "Block ": "tr",
        "Pesticide": "Test_Pesticide_Log",
        "EPA No": "123-45",
        "Group": "test_group",
        "Active Ingredient": "test_active",
        "Pest": "test_pest",
        "Singal Word": "warning",
        "REI (h)": 8.0,
        "PHI (d)": 10,
        "Units": "fl oz",
        "PHI Date": "08/25/26",
        "REI_TIME": "2100",
        "Liters/Acre": 200.0,
        "Min Dose": 2.0,
        "Max Dose": 4.0,
        "Dose/acre": 3.0,
        "Dose per L @150 l": 0.02,
        "Rate Units": "fl oz",
        "Calculated Dose": 300.0,
        "Dose Units": "ml",
        "Notes": "Updated notes"
    }
    
    history_repo.update_entry(new_id, updated_entry_data)
    
    # Verify Update
    entries = history_repo.load_history()
    updated = next((e for e in entries if e.entry_id == new_id), None)
    
    assert updated is not None
    assert updated.end_time == "1300"
    assert updated.block == "tr"
    assert updated.signal_word == "warning"
    assert updated.rei_h == 8.0
    assert updated.phi_d == 10
    assert updated.units == "fl oz"
    assert updated.notes == "Updated notes"
    
    # 4. Delete
    history_repo.delete_entry(new_id)
    
    # Verify Deletion
    entries = history_repo.load_history()
    assert not any(e.entry_id == new_id for e in entries)
