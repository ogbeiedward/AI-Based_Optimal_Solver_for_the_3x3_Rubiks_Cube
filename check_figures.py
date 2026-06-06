from docx import Document

doc = Document("docs/thesis_Edward_Ogbei_PCZ.docx")

print("Figure captions found in thesis:\n")
for i, p in enumerate(doc.paragraphs):
    if p.text.startswith("Fig."):
        print(f"  {p.text[:100]}")
