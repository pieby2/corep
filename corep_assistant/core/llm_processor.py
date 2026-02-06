import json
import os
from typing import List, Dict, Any
from groq import Groq
from .template_schema import CorepTemplate, TemplateRow, AuditEntry, TemplateCell

class LLMProcessor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
             # We will handle missing key gracefully in process() or UI
             pass
        else:
            self.client = Groq(api_key=self.api_key)

    def construct_prompt(self, user_query: str, context_rules: List[Dict[str, Any]]) -> str:
        """Constructs the prompt for the LLM."""
        
        rules_text = ""
        for rule in context_rules:
            rules_text += f"- **{rule['id']}** ({rule['title']}): {rule['text']}\n"

        prompt = f"""
You are an expert PRA/COREP Regulatory Reporting Assistant.
Your task is to extract data from the user's scenario and map it to the COREP C 01.00 (Own Funds) template schema.

### Regulatory Context (Use these rules to justify your mapping):
{rules_text}

### Template Structure:
The C 01.00 template requires the following rows (among others):
- Row 010: Common Equity Tier 1 (CET1) capital
- Row 020: Capital instruments eligible as CET1 Capital
- Row 350: Total deductions from Common Equity Tier 1
- Row 530: Additional Tier 1 (AT1) capital
- Row 750: Tier 2 (T2) capital

### User Scenario:
"{user_query}"

### Instructions:
1. Identify the relevant financial figures from the scenario.
2. Determine which COREP row they belong to based on the Regulatory Context.
3. If a figure belongs to a detailed row (like 020), it often also contributes to aggregate rows (like 010). YOU MUST EXPLICITLY CREATE separate entries for BOTH the detailed row and the aggregate row (010). The template does not auto-sum in this step.
4. Provide a citation (Rule ID) for why you mapped it there.
5. Return the output as a valid JSON object matching this structure:
{{
  "rows": [
    {{
      "row_id": "010",
      "description": "...",
      "amount": 1000000,
      "rule_ref": "CRR_ART_XX",
      "justification": "..."
    }}
  ]
}}
IMPORTANT: valid JSON only. Do not wrap in markdown code blocks.
"""
        return prompt

    def process(self, prompt: str) -> CorepTemplate:
        """
        Calls Groq API to process the prompt.
        """
        if not hasattr(self, 'client'):
             raise ValueError("Groq API Key is missing. Please provide it in the UI or environment.")

        print("DEBUG: Sending request to Groq API...")
        
        # try:
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful regulatory assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        # print(f"DEBUG: Groq Response: {response_content}")
        
        data = json.loads(response_content)
        rows_data = data.get("rows", [])
            
        # except Exception as e:
        #     print(f"Error calling Groq: {e}")
        #     raise e # Re-raise to let UI handle it

        # Construct the CorepTemplate object
        template = CorepTemplate()
        
        # Helper to merge or add rows (in case LLM outputs duplicates or multiple chunks for same row)
        row_map = {}
        
        for item in rows_data:
            r_id = str(item.get("row_id")) # ensure string
            if r_id not in row_map:
                row_map[r_id] = TemplateRow(row_id=r_id, description=item.get("description", ""))
            
            # Add cell 010 (Amount)
            current_val = 0.0
            if "010" in row_map[r_id].cells:
                current_val = row_map[r_id].cells["010"].value
            
            val = float(item.get("amount", 0))
            new_val = current_val + val
            
            # Create Audit
            audit = AuditEntry(
                rule_id=item.get("rule_ref", "Unknown"), 
                justification=item.get("justification", "Extracted by LLM")
            )
            
            # We append audit trails if there are multiple contributions to the same row
            existing_audit = []
            if "010" in row_map[r_id].cells:
                existing_audit = row_map[r_id].cells["010"].audit_trail
                
            row_map[r_id].set_value("010", new_val, existing_audit + [audit])
            
        template.rows = list(row_map.values())
        return template
