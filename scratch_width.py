from reportlab.pdfbase.pdfmetrics import stringWidth
text = "block road takhatpur chhattiarhs koliya ke ghar ke baahr wale jila"
w = stringWidth(text, "Helvetica", 11)
print(f"Width of text: {w}")
print(f"max_addr_w_1: 295.275")
