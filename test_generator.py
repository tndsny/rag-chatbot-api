from core.generator import answer

# Tes 1: pertanyaan yang JAWABANNYA ADA di dokumen
result = answer("Apa itu Bavar-373?")
print("JAWABAN:", result["answer"])
print("SUMBER :", result["sources"])

print("\n" + "="*50 + "\n")

# Tes 2: pertanyaan yang JAWABANNYA TIDAK ADA (uji guardrail)
result = answer("Bagaimana cuaca di Jakarta hari ini?")
print("JAWABAN:", result["answer"])
print("SUMBER :", result["sources"])