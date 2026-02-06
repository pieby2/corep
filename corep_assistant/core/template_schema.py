from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AuditEntry(BaseModel):
    """Represents a justification for a value based on a rule."""
    rule_id: str = Field(..., description="The ID of the regulatory rule (e.g., 'CRR_ART_26')")
    justification: str = Field(..., description="Short explanation of why this rule applies")
    source_text: Optional[str] = Field(None, description="Snippet of the regulatory text used")

class TemplateCell(BaseModel):
    """Represents a single datapoint in the template."""
    column_id: str = Field(..., description="Column ID (e.g., '010' for Amount)")
    value: float = Field(..., description="The numerical value for this cell")
    audit_trail: List[AuditEntry] = Field(default_factory=list, description="List of rules justifying this value")

class TemplateRow(BaseModel):
    """Represents a row in the C01 template."""
    row_id: str = Field(..., description="Row ID (e.g., '010')")
    description: str = Field(..., description="Row Label (e.g., 'Common Equity Tier 1 (CET1) capital')")
    cells: Dict[str, TemplateCell] = Field(default_factory=dict, description="Map of Column ID to Cell Data")
    
    def set_value(self, column_id: str, value: float, audit: List[AuditEntry]):
        self.cells[column_id] = TemplateCell(column_id=column_id, value=value, audit_trail=audit)

class CorepTemplate(BaseModel):
    """Represents the full C01 Own Funds Template."""
    template_id: str = "C 01.00"
    template_name: str = "Own Funds"
    rows: List[TemplateRow] = Field(default_factory=list, description="Ordered list of rows in the template")

    def get_row(self, row_id: str) -> Optional[TemplateRow]:
        for row in self.rows:
            if row.row_id == row_id:
                return row
        return None
