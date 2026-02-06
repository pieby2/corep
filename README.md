# PRA COREP Reporting Assistant (Prototype)

An LLM-assisted regulatory reporting tool designed to help UK Banks populate the **COREP C 01.00 (Own Funds)** template. This prototype uses a Retrieval-Augmented Generation (RAG) approach to map natural language scenarios to specific regulatory lines (EBA/PRA Rulebook) and validates the output.

## Live Demo
Try the application here: **[PRA COREP Assistant App](https://pieby2-corep-corep-assistantapp-mrgx73.streamlit.app/)**

## Features
- **Natural Language Parsing**: Converts descriptions of capital issuance/status into structured reporting data.
- **Regulatory Retrieval**: Uses a simulated knowledge base of CRR (Capital Requirements Regulation) articles to find relevant rules.
- **Automated Mapping**: Populates the C 01.00 Own Funds template rows (e.g., CET1, AT1, Tier 2).
- **Audit Trail**: Every populated field includes a citation to the specific regulation used for justification.
- **Validation Engine**: Flags business logic errors (e.g., negative capital values) and missing rule references.

## Tech Stack
- **Frontend**: Streamlit
- **LLM Integration**: Groq API (Llama 3.3 70B)
- **Data Validation**: Pydantic
- **Retrieval**: Keyword/Semantic RAG (Custom implementation)

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/pieby2/corep.git
   cd corep
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run corep_assistant/app.py
   ```

## Configuration
To use the live LLM features, you need a Groq API Key. You can enter this directly in the application sidebar.

## Project Structure
- `corep_assistant/app.py`: Main application entry point.
- `corep_assistant/core/`: Application logic (LLM processor, RAG engine, Schema, Validator).
- `corep_assistant/data/`: Simulated regulatory knowledge base (`knowledge_base.json`).
- `verify_prototype.py`: Script for end-to-end programmatic testing.
