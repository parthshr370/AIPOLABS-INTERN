#!/usr/bin/env python3
"""
Demo showing the difference between search and store embeddings
"""

def demo_openai_embeddings():
    """OpenAI: Same embeddings for all operations"""
    text = "I love Italian food, especially pizza"
    
    # Simulate OpenAI behavior (same embedding regardless of action)
    print("=== OpenAI Behavior ===")
    print(f"Text: '{text}'")
    print()
    
    # All three calls return IDENTICAL vectors
    add_embedding = [0.123, -0.456, 0.789, 0.234, -0.567]  # 1536 dims in reality
    search_embedding = [0.123, -0.456, 0.789, 0.234, -0.567]  # SAME as add
    update_embedding = [0.123, -0.456, 0.789, 0.234, -0.567]  # SAME as add
    
    print(f"add_embedding:    {add_embedding}")
    print(f"search_embedding: {search_embedding}")  
    print(f"update_embedding: {update_embedding}")
    print(f"Are they identical? {add_embedding == search_embedding == update_embedding}")
    print()

def demo_vertexai_embeddings():
    """VertexAI: Different embeddings per operation"""
    text = "I love Italian food, especially pizza"
    
    print("=== VertexAI Behavior ===")
    print(f"Text: '{text}'")
    print()
    
    # Different vectors for different operations!
    add_embedding = [0.823, -0.156, 0.489, 0.734, -0.267]     # RETRIEVAL_DOCUMENT
    search_embedding = [0.645, -0.289, 0.712, 0.456, -0.891]  # RETRIEVAL_QUERY (different!)
    update_embedding = [0.823, -0.156, 0.489, 0.734, -0.267]  # RETRIEVAL_DOCUMENT (same as add)
    
    print(f"add_embedding:    {add_embedding}  (RETRIEVAL_DOCUMENT)")
    print(f"search_embedding: {search_embedding}  (RETRIEVAL_QUERY)")
    print(f"update_embedding: {update_embedding}  (RETRIEVAL_DOCUMENT)")
    print(f"Are add/search identical? {add_embedding == search_embedding}")
    print(f"Are add/update identical? {add_embedding == update_embedding}")
    print()

def demo_asymmetric_search():
    """How asymmetric embeddings work in practice"""
    print("=== Asymmetric Search Example ===")
    
    # Stored memory (using RETRIEVAL_DOCUMENT)
    stored_text = "I had amazing sushi at Nobu restaurant last night"
    stored_embedding = [0.823, -0.156, 0.489, 0.734, -0.267]  # Document-optimized
    
    # Search query (using RETRIEVAL_QUERY) 
    query_text = "What restaurants do I like?"
    query_embedding = [0.645, -0.289, 0.712, 0.456, -0.891]   # Query-optimized
    
    print(f"Stored: '{stored_text}'")
    print(f"Stored embedding: {stored_embedding}")
    print()
    print(f"Query: '{query_text}'")  
    print(f"Query embedding: {query_embedding}")
    print()
    
    # Even though vectors are different, they're designed to be similar in vector space
    # when the query should match the document
    similarity = 0.87  # Simulated cosine similarity
    print(f"Cosine similarity: {similarity}")
    print(f"Match found! ✓ (similarity > 0.7 threshold)")
    print()

def demo_same_text_different_embeddings():
    """Same text gets different embeddings based on operation"""
    text = "I prefer vegetarian restaurants"
    
    print("=== Same Text, Different Operations ===")
    print(f"Text: '{text}'")
    print()
    
    # VertexAI would return different vectors for the same text!
    when_storing = [0.412, -0.789, 0.234, 0.567, -0.891]   # RETRIEVAL_DOCUMENT
    when_searching = [0.651, -0.234, 0.789, 0.412, -0.567] # RETRIEVAL_QUERY
    
    print(f"When storing (add):    {when_storing}")
    print(f"When searching (search): {when_searching}")
    print(f"Same text, different vectors! Numbers are different.")
    print(f"But both represent the same semantic meaning in their respective spaces.")
    print()

if __name__ == "__main__":
    demo_openai_embeddings()
    demo_vertexai_embeddings()
    demo_asymmetric_search()
    demo_same_text_different_embeddings()
    
    print("=== Key Takeaways ===")
    print("1. OpenAI/HuggingFace: memory_action parameter is IGNORED")
    print("2. VertexAI: memory_action changes the actual vector numbers")
    print("3. Same text can have different embeddings for different operations")
    print("4. Asymmetric embeddings are designed to work together despite being different")
    print("5. Vector dimensions stay the same (1536 for OpenAI, 256 for VertexAI, etc.)")