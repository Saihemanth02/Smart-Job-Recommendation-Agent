import re

def clean_text(text: str) -> str:
    """
    Cleans raw text by converting it to lowercase, removing non-alphabetic/non-tech symbols
    (keeps + and # for C++, C#), and normalizing whitespace.
    """
    if not text:
        return ""
    text = str(text).lower()
    # Keep standard characters, spaces, and common tech symbols (+ for C++, # for C#)
    text = re.sub(r'[^a-z0-9\s+#\-]', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def lemmatize_light(text: str) -> str:
    """
    Lightweight lemmatizer that handles standard plurals and gerunds
    without requiring external NLTK corpus downloads.
    """
    cleaned = clean_text(text)
    words = cleaned.split()
    processed_words = []
    
    for word in words:
        # Avoid truncating very short words or standard tech terms like 'aws', 'css', 'js'
        if len(word) > 4:
            if word.endswith("ing"):
                word = word[:-3]
            elif word.endswith("ed"):
                word = word[:-2]
            elif word.endswith("es") and not word.endswith("ces"): # keep words like databases/services
                word = word[:-2]
            elif word.endswith("s") and not word.endswith("ss") and not word.endswith("is"):
                word = word[:-1]
        processed_words.append(word)
        
    return " ".join(processed_words)
