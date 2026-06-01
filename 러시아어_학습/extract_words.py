import re
import json

# Read the HTML file
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract VOCAB array
vocab_match = re.search(r'const VOCAB = \[(.*?)\];', content, re.DOTALL)
if vocab_match:
    vocab_str = vocab_match.group(1)
    
    # Extract all words using regex
    pattern = r"\{ru:'([^']+)',ko:'([^']+)',lesson:'([^']+)'\}"
    words = re.findall(pattern, vocab_str)
    
    # Create dictionary organized by lesson
    vocab_by_lesson = {}
    for ru, ko, lesson in words:
        if lesson not in vocab_by_lesson:
            vocab_by_lesson[lesson] = []
        vocab_by_lesson[lesson].append({'ru': ru, 'ko': ko, 'lesson': lesson})
    
    # Print summary
    print(f"Total unique words: {len(words)}")
    print("\nWords by lesson:")
    for lesson in sorted(vocab_by_lesson.keys(), key=lambda x: (x != 'conv', x)):
        count = len(vocab_by_lesson[lesson])
        print(f"  Lesson {lesson}: {count} words")
    
    # Save to JSON for processing
    with open('vocab_data.json', 'w', encoding='utf-8') as f:
        json.dump(vocab_by_lesson, f, ensure_ascii=False, indent=2)
    
    print("\nData saved to vocab_data.json")

