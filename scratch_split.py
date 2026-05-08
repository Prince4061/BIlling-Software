from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import simpleSplit

def robust_split(text, fontName, fontSize, maxWidth):
    lines = simpleSplit(text, fontName, fontSize, maxWidth)
    result = []
    for line in lines:
        if stringWidth(line, fontName, fontSize) <= maxWidth:
            result.append(line)
        else:
            current_line = ""
            for char in line:
                if stringWidth(current_line + char, fontName, fontSize) <= maxWidth:
                    current_line += char
                else:
                    result.append(current_line)
                    current_line = char
            if current_line:
                result.append(current_line)
    return result

text = "block road takhatpur chhattiarhs koliya ke ghar ke baahr wale jila"
maxWidth = 295.275
print("Result of robust_split:")
print(robust_split(text, "Helvetica", 11, maxWidth))
