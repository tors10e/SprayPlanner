from pdfminer.high_level import extract_text
import re

pdf_path = "SprayPlanner/pesticide labels/abound_label.pdf"
text = extract_text(pdf_path)

# Look for Grapes section
grapes_match = re.search(r'Grapes', text, re.IGNORECASE)
if grapes_match:
    print("Found 'Grapes' in text.")
    # Extract some context around Grapes
    start = max(0, grapes_match.start() - 500)
    end = min(len(text), grapes_match.end() + 2000)
    print("--- Context around 'Grapes' ---")
    print(text[start:end])
else:
    print("'Grapes' not found in text.")

# Look for PHI or Pre-Harvest Interval
phi_match = re.search(r'(PHI|Pre-Harvest Interval)[:\s]+(\d+)', text, re.IGNORECASE)
if phi_match:
    print(f"Potential PHI found: {phi_match.group(0)}")
