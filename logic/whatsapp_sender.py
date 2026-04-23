import base64
import requests
import os

API_URL_BASE = "http://72.60.211.205:8080"
INSTANCE_NAME = "ali mobiles"
API_KEY = "CHANGE_THIS_TO_A_STRONG_PASSWORD"

def send_whatsapp_bill(pdf_path, mobile_number, customer_name):
    """
    Reads the PDF file, encodes to base64, and sends via Evolution API.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found.")
        
    url = f"{API_URL_BASE}/message/sendMedia/{INSTANCE_NAME.replace(' ', '%20')}"
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    
    # Ensure mobile starts with country code, assuming India if len == 10
    mobile_str = str(mobile_number).strip()
    if len(mobile_str) == 10:
        mobile_str = "91" + mobile_str
        
    filename = os.path.basename(pdf_path)

    payload = {
        "number": mobile_str,
        "mediatype": "document",
        "mimetype": "application/pdf",
        "caption": (
            f"Namaste {customer_name} Ji! \U0001f64f\n\n"
            f"Aapka bill H.H. MOBILE & Enterprises ki taraf se ready hai.\n"
            f"Bill PDF is message ke saath attached hai — please check karein.\n\n"
            f"Hamari dukaan par shopping karne ke liye shukriya! \U0001f60a\n"
            f"Koi bhi sawaal ho to humse zaroor sampark karein."
        ),
        "media": base64_pdf,
        "fileName": filename
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        return True, response.json()
    else:
        return False, response.text
