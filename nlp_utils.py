import spacy
import re

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def parse_command(command):
    # First, try to extract the title enclosed in single or double quotes
    title_match = re.search(r'["\']([^"\']+)["\']', command)
    if title_match:
        event_title = title_match.group(1)
    else:
        event_title = None
    
    # Process the rest of the command with spaCy
    doc = nlp(command)
    
    duration_minutes = 0
    intent = None
    
    # Detect intent and extract duration
    for token in doc:
        if token.lemma_ in ['add', 'create', 'schedule']:
            intent = 'add'
        elif token.lemma_ in ['update', 'change', 'modify', 'extend']:
            intent = 'update'
        elif token.lemma_ in ['delete', 'remove']:
            intent = 'delete'
        elif token.lemma_ in ['reschedule', 'move']:
            intent = 'reschedule'
        
        if token.like_num and token.head.text in ['minutes', 'minute', 'hours', 'hour']:
            duration_minutes = int(token.text)
            if token.head.text in ['hours', 'hour']:
                duration_minutes *= 60
                
    print(intent, event_title, duration_minutes)
    
    return intent, event_title, duration_minutes
