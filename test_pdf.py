from core.pdf_loader import extract_text_from_pdf

text = extract_text_from_pdf("data/Bagaimana_Cara_Memasarkan_Genset.pdf")
print("PANJANG TEKS:", len(text))
print("CUPLIKAN 500 KARAKTER PERTAMA:\n")
print(text[:500])
