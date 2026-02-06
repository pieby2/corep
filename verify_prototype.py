import sys
import os
from pprint import pprint

# Ensure we can import from the current directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'corep_assistant'))

from corep_assistant.core.rag_engine import RagEngine
from corep_assistant.core.llm_processor import LLMProcessor

def verify():
    print("--- Starting Verification of PRA COREP Assistant ---")
    
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(base_dir, 'corep_assistant', 'data', 'knowledge_base.json')
    
    print(f"Loading Knowledge Base from: {kb_path}")
    
    # 2. Initialize Engine
    try:
        rag = RagEngine(kb_path)
        llm = LLMProcessor()
        print("[OK] Engines initialized successfully.")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        return

    # 3. Test Query
    query = "We have issued 50m in ordinary shares directly to the market, fully paid up. We also have 20m in retained earnings."
    print(f"\nTest Query: '{query}'")

    # 4. Run Retrieval
    print("\n--- Testing Retrieval ---")
    context = rag.retrieve(query)
    if context:
        print(f"[OK] Retrieved {len(context)} rules.")
        for r in context:
            print(f"   - {r['id']}: {r['title']}")
    else:
        print("[ERROR] Retrieval returned no results.")

    # 5. Run LLM Processing (Mock)
    print("\n--- Testing LLM Processing (Mock) ---")
    prompt = llm.construct_prompt(query, context)
    # print(f"Generated Prompt (First 200 chars): {prompt[:200]}...")
    
    result = llm.process(prompt)
    
    print("\n--- Resulting Template ---")
    if result.rows:
        print(f"[OK] Template populated with {len(result.rows)} rows.")
        for row in result.rows:
            cell_010 = row.cells.get("010")
            val = cell_010.value if cell_010 else 0
            audit_ids = [a.rule_id for a in cell_010.audit_trail] if cell_010 else []
            print(f"Row {row.row_id}: {row.description}")
            print(f"  -> Value: {val:,.2f}")
            print(f"  -> Audit: {audit_ids}")
    else:
        print("[ERROR] Template returned empty rows.")

if __name__ == "__main__":
    verify()
