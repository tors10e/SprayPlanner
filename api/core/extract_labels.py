from pdfminer.high_level import extract_text
import re

def extract_grape_info(pdf_path):
    print(f"\n--- Analyzing {pdf_path} ---")
    text = extract_text(pdf_path)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Look for Grapes section
    # Many labels have a table or specific header for GRAPES
    grapes_idx = text.lower().find('grapes')
    if grapes_idx == -1:
        print("Grapes not found.")
        return
    
    # Take a chunk of text after 'Grapes'
    chunk = text[grapes_idx:grapes_idx+3000]
    print(f"Snippet: {chunk[:500]}...")
    
    # Extract PHI
    phi_match = re.search(r'(?:PHI|Pre-Harvest Interval|Do not apply within).*?(\d+)\s*(?:days|day)', chunk, re.IGNORECASE)
    if phi_match:
        print(f"PHI found: {phi_match.group(0)}")
    
    # Extract Max Application
    max_match = re.search(r'(?:Maximum|Do not apply more than).*?(\d+(?:\.\d+)?)\s*(?:fl oz|lb|applications|oz)', chunk, re.IGNORECASE)
    if max_match:
        print(f"Max Application info found: {max_match.group(0)}")

files = [
    "SprayPlanner/pesticide labels/abound_label.pdf",
    "SprayPlanner/pesticide labels/pristine.pdf",
    "SprayPlanner/pesticide labels/vivando_label.pdf",
    "SprayPlanner/pesticide labels/Rally_40_WSP1c_Label.pdf",
    "SprayPlanner/pesticide labels/Captan_4L.pdf"
]

for f in files:
    try:
        extract_grape_info(f)
    except Exception as e:
        print(f"Error processing {f}: {e}")
