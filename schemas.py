from typing import TypedDict 
from pydantic import BaseModel , Field 

class GraphState(TypedDict) : 
    """The state dictionary that flows through the LangGraph nodes"""
    bot_id : str 
    persona : str
    reasoning : str 
    search_query : str 
    search_result : str 
    final_post : dict

class SearchQueryOutput(BaseModel)  : 
    """Structured output for Node 1 to extract reasoning and query """
    reasoning : str = Field(description="One short sentence explaining why you chose this topic.")
    query: str = Field(description="A 4-8 word search engine query with no punctuation.")


class PostOutput(BaseModel): 
    """Structured output for Node 3 to guarantee JSON constraints."""
    bot_id :str =Field(description="The bot's unique identifier e.g. bot_a")
    topic : str = Field(description="One short phrase describing what the post is about")
    post_content: str = Field(description="The actual post text, strictly max 280 characters")


