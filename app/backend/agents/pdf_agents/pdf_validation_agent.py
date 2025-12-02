from app.backend.core.state import PdfState
from langgraph.prebuilt import create_react_agent


def pdf_validation_agent(state: PdfState = {}):
    print("=========================================================",state['file'])