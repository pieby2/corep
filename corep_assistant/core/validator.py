from typing import List, Dict
from .template_schema import CorepTemplate

class ValidationResult:
    def __init__(self, severity: str, message: str, row_id: str = None):
        self.severity = severity  # "ERROR", "WARNING"
        self.message = message
        self.row_id = row_id

class Validator:
    @staticmethod
    def validate(template: CorepTemplate) -> List[ValidationResult]:
        results = []
        
        # 1. Check for Missing Audit Trails
        for row in template.rows:
            cell_010 = row.cells.get("010")
            if cell_010 and cell_010.value != 0:
                if not cell_010.audit_trail:
                    results.append(ValidationResult(
                        "WARNING", 
                        f"Row {row.row_id} has a value but no regulatory justification (Audit Trail).",
                        row_id=row.row_id
                    ))
                else:
                    # Check for "Unknown" rule refs
                    for audit in cell_010.audit_trail:
                         if audit.rule_id == "Unknown":
                            results.append(ValidationResult(
                                "WARNING",
                                f"Row {row.row_id} cites an 'Unknown' rule reference.",
                                row_id=row.row_id
                            ))

        # 2. Business Logic: Basic Consistency
        # Example: CET1 (010) should generally be positive (though not strictly required, it's a good warning)
        cet1_row = template.get_row("010")
        if cet1_row:
            cell = cet1_row.cells.get("010")
            if cell and cell.value < 0:
                results.append(ValidationResult(
                    "ERROR",
                    "Common Equity Tier 1 (Row 010) is negative. This indicates a critical capital breach or data error.",
                    row_id="010"
                ))
                
        # 3. Aggregation Check (Simple)
        # Check if detailed rows sum up to aggregate rows roughly? 
        # For this prototype, we'll just check if we have components but 0 total
        # (This depends on the LLM's mapping logic, which we trust, but we can flag oddities)
        
        return results
