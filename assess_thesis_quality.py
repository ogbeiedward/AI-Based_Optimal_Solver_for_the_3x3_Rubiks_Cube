"""
Assess thesis for plagiarism and AI detection risks.
"""
from docx import Document
import re

doc = Document("docs/thesis_Edward_Ogbei_PCZ.docx")

# Extract all paragraphs
all_text = []
for p in doc.paragraphs:
    if p.text.strip():
        all_text.append(p.text)

full_text = " ".join(all_text)

print("=" * 70)
print("THESIS QUALITY ASSESSMENT - PLAGIARISM & AI DETECTION RISKS")
print("=" * 70)

# Check 1: Generic AI phrases that could flag AI detection
ai_flags = [
    r"in this paper",
    r"as mentioned",
    r"to summarize",
    r"furthermore",
    r"additionally",
    r"in conclusion",
    r"it is important to note",
    r"it can be observed",
    r"as we can see",
    r"the results show that",
]

print("\n1. POTENTIAL AI-DETECTION RED FLAGS:")
for phrase in ai_flags:
    count = len(re.findall(phrase, full_text, re.IGNORECASE))
    if count > 0:
        print(f"   '{phrase}': {count} occurrences")

# Check 2: Citation coverage
citation_pattern = r"\[\d+\]"
citations = re.findall(citation_pattern, full_text)
print(f"\n2. CITATION COVERAGE:")
print(f"   Total citations found: {len(citations)}")
print(f"   Citation density: ~1 per {len(full_text)//len(citations) if citations else 'N/A'} characters")

# Check 3: Passive vs active voice
passive_patterns = [
    r"is \w+ed",
    r"was \w+ed",
    r"are \w+ed",
    r"were \w+ed",
    r"by .{1,20}",
]
passive_count = sum(len(re.findall(p, full_text, re.IGNORECASE)) for p in passive_patterns)
print(f"\n3. PASSIVE VOICE RISK:")
print(f"   Passive voice patterns: {passive_count} (lower is better)")
print(f"   Recommendation: Keep under 30% for natural language")

# Check 4: Code snippet presence
code_keywords = ["def ", "class ", "import ", "for ", "while ", "if ", "return "]
code_count = sum(full_text.count(kw) for kw in code_keywords)
print(f"\n4. CODE PRESENCE:")
print(f"   Code-like patterns: {code_count}")
if code_count < 5:
    print("   WARNING: Very few code snippets - consider adding implementation details")

# Check 5: Personal voice markers (good for originality)
personal_markers = ["we implemented", "we developed", "our approach", "our model",
                   "we trained", "we evaluated", "in our experiments"]
personal_count = sum(len(re.findall(m, full_text, re.IGNORECASE)) for m in personal_markers)
print(f"\n5. PERSONAL VOICE (originality marker):")
print(f"   Personal expressions: {personal_count}")
if personal_count < 10:
    print("   NOTE: Could emphasize your own work more (but avoid first-person excess)")

# Check 6: Repetition (plagiarism risk)
sentences = [s.strip() for s in re.split(r'[.!?]+', full_text) if len(s.strip()) > 20]
print(f"\n6. TEXT LENGTH AND STRUCTURE:")
print(f"   Total sentences: {len(sentences)}")
print(f"   Average sentence length: {len(full_text)//len(sentences) if sentences else 'N/A'} chars")

# Check 7: Uncommon words (good for originality detection)
words = re.findall(r'\b\w+\b', full_text.lower())
word_freq = {}
for word in words:
    if len(word) > 6:  # longer words
        word_freq[word] = word_freq.get(word, 0) + 1

long_repeated = {w: c for w, c in word_freq.items() if c > 5}
print(f"\n7. DISTINCTIVE VOCABULARY:")
print(f"   Long words used 6+ times: {len(long_repeated)}")
if len(long_repeated) > 0:
    print(f"   Examples: {list(long_repeated.keys())[:5]}")

print("\n" + "=" * 70)
print("KEY RECOMMENDATIONS:")
print("=" * 70)
print("""
1. ADD CODE SNIPPETS:
   - Include 3-5 key implementation snippets (curriculum loop, model definition, etc.)
   - This demonstrates real implementation and reduces AI-detection risk
   - Standard practice in CS theses
   - Add to: Chapter 4 (architecture), Chapter 5 (training), Chapter 6 (curriculum)

2. PLAGIARISM PREVENTION:
   - Verify all external ideas are cited with [N] references
   - Paraphrase actively (don't copy phrases from papers)
   - Your results/analysis sections should be 100% original

3. AI-DETECTION PREVENTION:
   - Use natural transitions, not forced academic connectors
   - Include specific data, measurements, and personal observations
   - Reference your own figures and code, not just existing work
   - Vary sentence structure (avoid repetitive patterns)

4. ORIGINALITY MARKERS:
   - Use "we implemented", "we discovered", "our results show"
   - Include discussion of failures and unexpected findings
   - Reference your ablation study and specific benchmark numbers

5. CRITICAL REVIEW:
   - Plagiarism check: Use iThenticate, Turnitin, or similar
   - AI detection: Use Winston AI, GPTZero, or similar
   - Both checks should pass BEFORE submission
""")
