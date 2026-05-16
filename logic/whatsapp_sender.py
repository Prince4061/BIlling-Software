import os
import urllib.parse
import webbrowser

def send_whatsapp_bill(pdf_path, mobile_number, customer_name):
    """
    Opens WhatsApp Web in the browser to send a message.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found.")
        
    # Ensure mobile starts with country code, assuming India if len == 10
    mobile_str = str(mobile_number).strip()
    if len(mobile_str) == 10:
        mobile_str = "91" + mobile_str
        
    filename = os.path.basename(pdf_path)

    message = (
        f"Namaste {customer_name} Ji! \U0001f64f\n\n"
        f"Aapka bill H.H. MOBILE & Enterprises ki taraf se ready hai.\n"
        f"Please is folder se bill file ({filename}) attach karein.\n\n"
        f"Hamari dukaan par shopping karne ke liye shukriya! \U0001f60a\n"
        f"Koi bhi sawaal ho to humse zaroor sampark karein."
    )
    
    encoded_message = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={mobile_str}&text={encoded_message}"
    
    # Open browser
    webbrowser.open(url)
    
    # Open folder and highlight the PDF so user can easily attach it
    try:
        norm_path = os.path.normpath(os.path.abspath(pdf_path))
        import subprocess
        subprocess.run(['explorer', '/select,', norm_path])
    except Exception:
        pass
        
    return True, {"message": "Browser opened for WhatsApp Web."}

def send_whatsapp_text(mobile_number, message):
    """
    Sends a simple text message via browser WhatsApp Web.
    """
    mobile_str = str(mobile_number).strip()
    if len(mobile_str) == 10:
        mobile_str = "91" + mobile_str

    encoded_message = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={mobile_str}&text={encoded_message}"
    
    webbrowser.open(url)
    
    return True, {"message": "Browser opened for WhatsApp Web."}
