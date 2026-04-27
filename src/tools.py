import re 
from langchain_core.tools import tool

@tool
def mock_searxng_search(query: str) -> str:
    """Search for recent news headlines based on a keyword query."""
    query_lower =query.lower().strip()

    if not query_lower:
        return "Breaking: AI reshapes global economy in 2026."
    
    keyword_map = {
        "crypto"      : "Bitcoin hits new all-time high amid regulatory ETF approvals.",
        "bitcoin"     : "Bitcoin surges past $100K as institutional adoption accelerates.",
        "ai"          : "OpenAI releases GPT-5, automating 40% of software coding tasks.",
        "openai"      : "OpenAI releases GPT-5, automating 40% of software coding tasks.",
        "market"      : "S&P 500 hits record high as inflation cools to 2.1%.",
        "fed"         : "Federal Reserve holds rates steady, hints at cuts later this year.",
        "facebook"    : "Facebook whistleblower: platform knew of teen mental health harm for years.",
        "meta"        : "Internal Meta documents reveal algorithm intentionally maximises outrage.",
        "capitalism"  : "Oxfam report: world's 5 richest men doubled wealth since 2020.",
        "neural"    : "Neuralink receives FDA approval for second human brain-chip trial.",
        "monopoly"  : "DOJ files landmark antitrust case to break up Google's ad business.",
        "elon"      : "Elon Musk's xAI raises $6B to build supercomputer rivalling OpenAI.",
        "tech"      : "Tech sector leads S&P gains as AI adoption accelerates.",
        "society"   : "Oxfam report: world's 5 richest men doubled wealth since 2020.",
    }

    matched_headlines = []
    seen=set()

    for keyword , headline in keyword_map.items() : 
        if re.search(rf"\b{re.escape(keyword)}\b", query_lower) : 
            if headline not in seen:
                matched_headlines.append(headline)
                seen.add(headline)
    if matched_headlines:
            return " | ".join(matched_headlines[:2])
        
    return "Breaking: Major technological and economic shifts reshape global landscape in 2026."