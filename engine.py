import os 
import json 
from dotenv import load_dotenv 
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph ,END 
from schemas import GraphState , SearchQueryOutput , PostOutput
from tools import mock_searxng_search 
from personas import PERSONAS 

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY, temperature=0.7)
llm_search = llm.with_structured_output(SearchQueryOutput)
llm_post = llm.with_structured_output(PostOutput)


#NODES 

def node_deciding_search(state:GraphState)->dict :

    print(f"\n Node 1 : Deciding search query for {state['bot_id']}")
    
    messages = [
        ("system", f"You are the following social media bot persona:\n{state['persona']}\nYou must act strictly in character."),
        ("human", "Think about what topic excites or concerns you the most right now, given your personality. Return your reasoning and a search query.")
    ]
    
    try:
        response: SearchQueryOutput = llm_search.invoke(messages)
        
        print(f" Node 1 Reasoning : {response.reasoning}")
        print(f" Node 1 Query : '{response.query}'")
        return {"reasoning": response.reasoning, "search_query": response.query}
    except Exception as e:
        print(f"  Node 1 LLM Error: {e}")
        return {"reasoning": "Fallback invoked.", "search_query": "technology news 2026"}
    

def node_web_search(state:GraphState) ->dict : 

    print(f" Node 2 Searching for: '{state['search_query']}'")
    try:
        
        # Call the tool imported from tools.py
        result = mock_searxng_search.invoke({"query": state["search_query"]})

        print(f" Node 2 Result: '{result}'")
        return {"search_result": result}
    
    except Exception as e:

        print(f" Node 2 Tool Error: {e}")
        return {"search_result": "AI and markets dominate global headlines in 2026."}
    
def node_draft_post(state: GraphState) -> dict:

    print(f" Node 3 Drafting post for {state['bot_id']} ")

    messages = [
        ("system", f"""You are the following social media bot: {state['persona']}
            YOUR REASONING for today's post: {state['reasoning']}
            BREAKING NEWS HEADLINE: "{state['search_result']}"
            
            Write a single Twitter/X-style post reacting to this headline, STRICTLY in your persona's voice.
            HARD LIMIT: 280 characters maximum. bot_id is "{state['bot_id']}".
            FORMATTING RULE: Output valid JSON. Do not escape single quotes or apostrophes.
            Avoid repeating phrasing. Express ideas in a fresh way each time.
        """),
        ("human", f"YOUR REASONING: {state['reasoning']}\nBREAKING NEWS: '{state['search_result']}'\nWrite a single Twitter/X-style post reacting to this headline. HARD LIMIT: 280 characters. bot_id is {state['bot_id']}.")
    ]
    
    try:
        response: PostOutput = llm_post.invoke(messages)
        post_content = response.post_content
        if len(post_content) > 280:
            post_content = post_content[:277] + "..."

        final_post = {
            "bot_id"      : response.bot_id,
            "topic"       : response.topic,
            "post_content": post_content,
        }

        print(f" Node 3 Post drafted ({len(post_content)} chars)")

        return {"final_post": final_post}
    
    except Exception as e:

        print(f" Node 3 LLM Error: {e}")

        return {"final_post": {"bot_id": state["bot_id"], "topic": "error", "post_content": "System error."}}
    

def build_graph() -> StateGraph:

    graph = StateGraph(GraphState)
    graph.add_node("decide_search", node_deciding_search)
    graph.add_node("web_search",    node_web_search)
    graph.add_node("draft_post",    node_draft_post)
    
    graph.set_entry_point("decide_search")
    graph.add_edge("decide_search", "web_search")
    graph.add_edge("web_search",    "draft_post")
    graph.add_edge("draft_post",    END)
    
    return graph.compile()

def run_bot_post(bot_id: str) -> dict:

    if bot_id not in PERSONAS:
        raise ValueError(f"Unknown bot_id '{bot_id}'.")

    app = build_graph()
    initial_state: GraphState = {
        "bot_id"        : bot_id,
        "persona"       : PERSONAS[bot_id]["description"],
        "reasoning"     : "",
        "search_query"  : "",
        "search_result" : "",
        "final_post"    : {},
    }

    return app.invoke(initial_state)["final_post"]


if __name__ == "__main__":
    print(" Autonomous Content Engine ")
    for bot_id in PERSONAS.keys():
        post = run_bot_post(bot_id)
        
        print(f"\n  FINAL OUTPUT:")
        print(f"  {json.dumps(post, indent=4)}")