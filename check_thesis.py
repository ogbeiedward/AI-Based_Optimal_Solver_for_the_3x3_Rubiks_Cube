from docx import Document

doc = Document("docs/thesis_Edward_Ogbei_PCZ.docx")

print("=== THESIS CONTENT SAMPLE ===\n")
for i, p in enumerate(doc.paragraphs[:60]):
    if p.text.strip():
        print(f"{i}: {p.text[:90]}")
