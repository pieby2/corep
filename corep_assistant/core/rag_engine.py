import json
import os
from typing import List, Dict, Any

class RagEngine:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.knowledge_base_path):
            raise FileNotFoundError(f"Knowledge base not found at {self.knowledge_base_path}")
        with open(self.knowledge_base_path, 'r') as f:
            return json.load(f)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Simple retrieval based on keyword overlap. 
        In a real system, this would use vector embeddings (e.g., ChromaDB/FAISS).
        """
        query_words = set(query.lower().split())
        scored_rules = []

        for rule in self.knowledge_base:
            score = 0
            # Check overlap with explicit keywords
            rule_keywords = set([k.lower() for k in rule.get('keywords', [])])
            score += len(query_words.intersection(rule_keywords)) * 2
            
            # Check overlap with title
            title_words = set(rule['title'].lower().split())
            score += len(query_words.intersection(title_words))
            
            # Check overlap with text (lower weight)
            text_words = set(rule['text'].lower().split())
            score += len(query_words.intersection(text_words)) * 0.5

            if score > 0:
                scored_rules.append((score, rule))

        # Sort by score descending
        scored_rules.sort(key=lambda x: x[0], reverse=True)
        
        return [rule for score, rule in scored_rules[:top_k]]

if __name__ == "__main__":
    # Test
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'knowledge_base.json')
    engine = RagEngine(base_path)
    results = engine.retrieve("We have issued common equity tier 1 capital instruments")
    for r in results:
        print(f"Retrieved: {r['id']} - {r['title']}")
