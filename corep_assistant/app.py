import streamlit as st
import pandas as pd
import os
import sys

# Ensure core modules can be imported
sys.path.append(os.path.dirname(__file__))

from core.rag_engine import RagEngine
from core.llm_processor import LLMProcessor
from core.template_schema import CorepTemplate
from core.validator import Validator

# Page Config configuration
st.set_page_config(
    page_title="PRA COREP Assistant (Prototype)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium" feel
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #0E1117;
        font-weight: 700;
    }
    .metric-card {
        background-color: #ffffff;
        border-right: 1px solid #e6e6e6;
        border-bottom: 1px solid #e6e6e6; 
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 class='main-header'>PRA COREP Reporting Assistant</h1>", unsafe_allow_html=True)
    st.markdown("### LLM-Assisted Prototype for C 01.00 (Own Funds)")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        model = st.selectbox("Model", ["Groq (Llama 3.3 70B)", "Simulated LLM (Prototype)"])
        
        api_key = None
        if "Groq" in model:
            api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
            st.markdown("[Get your Groq API Key here](https://console.groq.com/keys)")
            if not api_key:
                st.warning("Please enter your Groq API Key.")
        
        st.info("Prototype Mode: Uses simulated regulatory knowledge base.")

    # Main Input Area
    st.subheader("Reporting Scenario")
    scenario_input = st.text_area(
        "Describe your capital movements or status:",
        height=150,
        placeholder="e.g., We have issued 50m in ordinary shares directly to the market, fully paid up. We also have 20m in retained earnings from the previous year...",
        help="Enter a natural language description of the bank's capital situation."
    )

    if st.button("Generate Report", type="primary"):
        if not scenario_input:
            st.warning("Please enter a scenario description.")
            return
            
        if "Groq" in model and not api_key:
            st.error("Groq API Key is required for this model.")
            return

        with st.spinner("Retrieving PRA Rulebook & EBA Instructions..."):
            # Initialize Engines
            base_path = os.path.join(os.path.dirname(__file__), 'data', 'knowledge_base.json')
            rag = RagEngine(base_path)
            
            # Initialize LLM with optional key
            llm = LLMProcessor(api_key=api_key)

            # 1. Retrieve Context
            context = rag.retrieve(scenario_input, top_k=3)
            
            # 2. Process with LLM
            prompt = llm.construct_prompt(scenario_input, context)
            try:
                template_result = llm.process(prompt)
            except Exception as e:
                st.error(f"LLM Processing Failed: {e}")
                return

        # Output Display
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Populated C 01.00 Template Extract")
            
            # Convert to DataFrame for display
            data = []
            for row in template_result.rows:
                row_val = row.cells.get("010") # Focus on Amount Column
                val_fmt = f"{row_val.value:,.2f}" if row_val else "0.00"
                
                # Get Rules for this row
                rules = []
                if row_val:
                    for audit in row_val.audit_trail:
                        rules.append(audit.rule_id)
                
                data.append({
                    "Row ID": row.row_id,
                    "Description": row.description,
                    "Amount (Col 010)": val_fmt,
                    "Rule Ref": ", ".join(rules)
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("### Audit Decision Log")
            for row in template_result.rows:
                 row_val = row.cells.get("010")
                 if row_val:
                     for audit in row_val.audit_trail:
                         with st.expander(f"Why {row.row_id} - {audit.rule_id}?"):
                             st.markdown(f"**Justification:** {audit.justification}")
                             st.markdown(f"**Source Text:**")
                             # Find text in context if available
                             rule_text = next((r['text'] for r in context if r['id'] == audit.rule_id), "Reference lookup in KB.")
                             st.caption(rule_text)

            # --- Validation Section ---
            validator = Validator()
            validation_results = validator.validate(template_result)
            
            if validation_results:
                st.divider()
                st.subheader("Validation & Consistency Checks")
                for result in validation_results:
                    if result.severity == "ERROR":
                        st.error(f"**{result.severity}**: {result.message}")
                    else:
                        st.warning(f"**{result.severity}**: {result.message}")
            else:
               st.divider()
               st.success("✅ Basic validation checks passed.")

        with col2:
            st.subheader("Regulatory Context Retrieved")
            for rule in context:
                with st.expander(f"{rule['id']}: {rule['title']}", expanded=True):
                    st.write(rule['text'])
                    st.caption(f"Source: {rule['source']}")

if __name__ == "__main__":
    main()
