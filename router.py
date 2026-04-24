#FLOW 
#  1. Load bot persona description from persona.py 
#  2. Embed each persona using MiniLM-L6-v2 model 
#  3. route_post_to_bots takes the imcoming post content and embed the post , queries ChromaDB and retruns only bots above the  cosine similarity thresh (0.85) 

import os 
import chromadb 
from chromadb.utils import embedding_functions 
from personas import PERSONAS 

chroma_client= chromadb.EphemeralClient()

embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

persona_collection = chroma_client.get_or_create_collection(
    name ="bot_personas",
    embedding_function=embed_func,
    metadata={"hnsw:space":"cosine"},
)


# Embed & Store personas 

def load_personas_into_vectorstore() ->None : 
    """
    Embeds each persona description ands upserts it into ChromaDB 
    """

    ids = []
    documents = []
    metadatas = []

    for bot_id , persona in PERSONAS.items() : 
        ids.append(bot_id)
        documents.append(persona['description'])
        metadatas.append({"name" : persona['name']})

    persona_collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Loaded {len(ids)} personas into ChromaDB vector store")


#Route a post to matching bots 

def route_post_to_bots(post_content : str , threshold : float = 0.20) -> list[dict] : 
    """
    Embed post_content and finds  bot personas whose vector is within cosine similarity > threshold.
    As, ChromaDB returns 'distance' not 'similarity'
    For cosine space : similarity = 1- distance

    Args : 
        post_content : The raw text of the incoming social-media post.
        threshold : Minimum cosine similarity to qualify a bot (0-1).
    
    Returns:
        List of dicts: [{"bot_id": ..., "name": ..., "similarity": ...}, ...]
        Empty list if no bot clears the threshold.

    """



    #Query all 3 bots so we can inspect each similarity scroe

    results = persona_collection.query(
        query_texts=[post_content],
        n_results=len(PERSONAS),   # fetch all bots
        include=["metadatas", "distances"],
    )

    matched_bots = []


    # results["distances"][0]  :  list of distances for query 0
    # results["metadatas"][0]  :  list of metadata dicts for query 0
    # results["ids"][0] : list of bot_ids for query 0


    for bot_id , distance , metadata in zip(results['ids'][0],results['distances'][0],results['metadatas'][0]) :

        similarity = 1 - distance # convert cosine distance to similarity

        print(f"{metadata['name']:30s} | similarity = {similarity:.4f}", end="")

        if similarity >=threshold : 
            print(f" |    Matched ")
            matched_bots.append(
              {
                "bot_id": bot_id,
                "name": metadata["name"],
                "similarity": round(similarity, 4),
                }
            )

        else:
            print(f"  |  below threshold ({threshold})")
 
    return matched_bots


def display_routing_result(post: str, matched: list[dict]) -> None:
 
    if matched:
        print(f"Routed to {len(matched)} bots:")
        for bot in matched:
            print(f" {bot['name']}  (similarity: {bot['similarity']})")
    else:
        print(" No bot matched above the similarity threshold.")


#demo-run 

if __name__=='__main__' :
    # 1. Load personas into the vector store
    load_personas_into_vectorstore()

    # 2. Test posts : one for each bot + one edge case
    test_posts = [
        "OpenAI just released a new model that might replace junior developers.",
 
        "Facebook's algorithm is deliberately making teenagers depressed for engagement.",

        "The Fed just hiked interest rates by 50bps. What does this mean for my portfolio?",
 
        "Bitcoin just hit a new all-time high. Is this the decade of digital assets?",
 
        # Edge case likely matches nobody above 0.20
        "My cat knocked over my coffee this morning.",
    ]

    print(" Running Vector-Based Persona Matching")
 
    for post in test_posts:
        print(f'Routing: "{post}"')
        matched = route_post_to_bots(post, threshold=0.20)
        display_routing_result(post, matched)

 



