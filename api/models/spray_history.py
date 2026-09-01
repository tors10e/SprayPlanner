class SprayHistoryEntry:
    def __init__(
        self,
        entry_id: int,
        spray_number: int,
        date: str,
        end_time: str,
        block: str,
        pesticide: str,
        epa_no: str,
        group: str,
        active_ingredient: str,
        pest: str,
        signal_word: str,
        rei_h: float,
        phi_d: int,
        units: str,
        phi_date: str,
        rei_time: str,
        liters_acre: float,
        min_dose: float,
        max_dose: float,
        dose_acre: float,
        dose_per_l: float,
        rate_units: str,
        calculated_dose: float,
        dose_units: str,
        notes: str,
        event_id: int = None,
        block_application_id: int = None,
        max_annual_rate: float = None,
        max_applications: int = None
    ):
        self.entry_id = entry_id
        self.spray_number = spray_number
        self.date = date
        self.end_time = end_time
        self.block = block
        self.pesticide = pesticide
        self.epa_no = epa_no
        self.group = group
        self.active_ingredient = active_ingredient
        self.pest = pest
        self.signal_word = signal_word
        self.rei_h = rei_h
        self.phi_d = phi_d
        self.units = units
        self.phi_date = phi_date
        self.rei_time = rei_time
        self.liters_acre = liters_acre
        self.min_dose = min_dose
        self.max_dose = max_dose
        self.dose_acre = dose_acre
        self.dose_per_l = dose_per_l
        self.rate_units = rate_units
        self.calculated_dose = calculated_dose
        self.dose_units = dose_units
        self.notes = notes
        self.event_id = event_id
        self.block_application_id = block_application_id
        self.max_annual_rate = max_annual_rate
        self.max_applications = max_applications

    def to_dict(self) -> dict:
        return {
            "id": self.entry_id,
            "Spray #": self.spray_number,
            "Date": self.date,
            "End Time": self.end_time,
            "Block ": self.block,
            "Pesticide": self.pesticide,
            "EPA No": self.epa_no,
            "Group": self.group,
            "Active Ingredient": self.active_ingredient,
            "Pest": self.pest,
            "Singal Word": self.signal_word,
            "REI (h)": self.rei_h,
            "PHI (d)": self.phi_d,
            "Units": self.units,
            "PHI Date": self.phi_date,
            "REI_TIME": self.rei_time,
            "Liters/Acre": self.liters_acre,
            "Min Dose": self.min_dose,
            "Max Dose": self.max_dose,
            "Dose/acre": self.dose_acre,
            "Dose per L @150 l": self.dose_per_l,
            "Rate Units": self.rate_units,
            "Calculated Dose": self.calculated_dose,
            "Dose Units": self.dose_units,
            "Notes": self.notes,
            "event_id": self.event_id,
            "block_application_id": self.block_application_id,
            "Max Annual Rate": self.max_annual_rate,
            "Max Applications": self.max_applications
        }
