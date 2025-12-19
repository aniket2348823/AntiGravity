import re
from collections import Counter
from bs4 import BeautifulSoup

class ContextEngine:
    def generate_wordlist(self, html, top_n=15):
        """
        Phase 2: Vocabulary Extraction
        Extracts business nouns from the target's landing page.
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Regex to find words > 3 chars
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Common stop words to ignore
        stop_words = {
            'the', 'and', 'contact', 'login', 'copyright', 'privacy', 'policy', 
            'terms', 'about', 'home', 'sign', 'out', 'all', 'rights', 'reserved',
            'support', 'email', 'phone', 'address', 'sitemap', 'search', 'menu'
        }
        
        filtered = [w for w in words if w not in stop_words]
        
        # Get most common words
        common = [w for w, c in Counter(filtered).most_common(top_n)]
        
        # Expand vocabulary
        return self.expand_vocabulary(common)

    def expand_vocabulary(self, wordlist):
        """
        Phase 2: Semantic Expansion
        Horizontally fuzz discovered endpoints using nouns.
        """
        perms = set(wordlist)
        for w in wordlist:
            perms.add(w + 's')         # Plural: user -> users
            perms.add('get' + w)       # Action-Verb: users -> getusers
            perms.add(w + '-details')  # Kebab-case: user -> user-details
            perms.add(w + '_list')     # Snake_case: user -> user_list
        return list(perms)
