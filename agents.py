import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url

import os

load_dotenv()
mistral_key = os.getenv("MISTRAL_API_KEY")
try:
    mistral_key = st.secrets.get("MISTRAL_API_KEY", mistral_key)
except StreamlitSecretNotFoundError:
    # Streamlit secrets are optional; .env or the process environment can supply the key.
    pass

if not mistral_key:
    st.error("Missing MISTRAL_API_KEY. Please configure it in your secrets or .env file.")
    st.stop()

llm = ChatMistralAI(
    api_key=mistral_key,
    model="mistral-small-2506",
    temperature=0,
)

st.title("Mistral AI App")


def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt="""
You are a research search agent.

Always use the web_search tool to answer the user's request.

Never answer from your own knowledge.
Return all relevant URLs and snippets.
"""
    )
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt="""
You are a web reading agent.

Always use the scrape_url tool.

Choose the most relevant URL and scrape it.

Return only the extracted content.
"""
    )
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. Write clear, structured and insightful reports."
    ),
    (
        "human",
        """
Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Return one response using this exact format:

=== REPORT ===

- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

=== CRITIC FEEDBACK ===

Score: X/10
Strengths
Areas to Improve
Verdict

Be detailed, factual and professional.
"""
    )
])
writer_chain = writer_prompt | llm | StrOutputParser()
