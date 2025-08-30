import numpy as np
import logging
import json
from typing import List, Dict
from app.core.supabase_client import supabase
from app.services.storage_service import StorageService
from app.processing.embedders import TextEmbedder


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchService:
    """Service for semantic and contextual search operations"""
    
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the search service
        
        Args:
            embedding_model: OpenAI embedding model to use for query encoding
        """
        self.embedder = TextEmbedder(model_name=embedding_model)
        self.storage_service = StorageService()
        
    def _parse_embedding(self, embedding_data: any) -> List[float]:
        """Parse embedding data from database format to list of floats"""
        if isinstance(embedding_data, str):
            embedding_data = json.loads(embedding_data)
        elif isinstance(embedding_data, list):
            pass  # Already a list
        else:
            logger.warning(f"Unexpected embedding format: {type(embedding_data)}")
            return None
        return embedding_data

    async def semantic_search(self, 
                            query: str, 
                            user_id: str,
                            top_k: int = 5,
                            similarity_threshold: float = 0.3) -> List[Dict]:
        """
        Search for the most semantically similar contexts to the query.
        
        Args:
            query: Search query text
            user_id: Required user ID to filter contexts (respects RLS)
            top_k: Number of top contexts to return
            similarity_threshold: Minimum similarity score to include
            
        Returns:
            List of context dictionaries with similarity scores
        """
        try:
            logger.info(f"Generating embedding for query: '{query[:50]}...'")
            query_embeddings = await self.embedder.embed([query])
            if not query_embeddings:
                logger.error("Failed to generate query embedding")
                return []
                
            query_embedding = query_embeddings[0]
            
            # Search in both chunks and metadata, then aggregate by context
            contexts_scores = {}
            
            # 1. Search in context_chunks
            chunk_matches = await self._search_chunks(query_embedding, similarity_threshold)
            logger.info(f"Found {len(chunk_matches)} chunk matches")
            
            for match in chunk_matches:
                context_id = match['context_id']
                similarity = match['similarity']
                # Prefer content text from the best matching chunk as a snippet
                chunk_content = match.get('content')
                
                if context_id not in contexts_scores:
                    contexts_scores[context_id] = {
                        'max_chunk_similarity': similarity,
                        'chunk_count': 1,
                        'chunk_similarities': [similarity],
                        'has_metadata': False,
                        'top_chunk_content': chunk_content
                    }
                else:
                    # Update best similarity and keep snippet from the best chunk
                    if similarity > contexts_scores[context_id]['max_chunk_similarity']:
                        contexts_scores[context_id]['max_chunk_similarity'] = similarity
                        if chunk_content:
                            contexts_scores[context_id]['top_chunk_content'] = chunk_content
                    contexts_scores[context_id]['chunk_count'] += 1
                    contexts_scores[context_id]['chunk_similarities'].append(similarity)
            
            # 2. Search in context_metadata
            metadata_matches = await self._search_metadata(query_embedding, similarity_threshold)
            logger.info(f"Found {len(metadata_matches)} metadata matches")
            
            for match in metadata_matches:
                context_id = match['context_id']
                similarity = match['similarity']
                metadata_content = match.get('content')
                
                if context_id not in contexts_scores:
                    contexts_scores[context_id] = {
                        'max_chunk_similarity': 0,
                        'chunk_count': 0,
                        'chunk_similarities': [],
                        'has_metadata': True,
                        'metadata_similarity': similarity,
                        'top_chunk_content': None,
                        'top_metadata_content': metadata_content
                    }
                else:
                    contexts_scores[context_id]['has_metadata'] = True
                    contexts_scores[context_id]['metadata_similarity'] = similarity
                    # Use metadata content as a fallback snippet if we don't have a chunk snippet
                    if not contexts_scores[context_id].get('top_chunk_content') and metadata_content:
                        contexts_scores[context_id]['top_metadata_content'] = metadata_content
            
            # 3. Calculate composite scores and get context details
            ranked_contexts = await self._rank_and_fetch_contexts(
                contexts_scores, user_id, top_k
            )
            
            logger.info(f"Returning {len(ranked_contexts)} ranked contexts")
            return ranked_contexts
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise
    
    async def _search_chunks(self, query_embedding: List[float], threshold: float) -> List[Dict]:
        """Search for similar chunks using pgvector cosine similarity"""
        try:
            # Using Supabase's vector similarity search
            result = supabase.rpc('search_chunks', {
                'query_embedding': query_embedding,
                'similarity_threshold': threshold,
                'match_count': 50  # Get more chunks to aggregate by context
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.warning(f"RPC search failed, falling back to direct query: {str(e)}")
            # Fallback to direct SQL if RPC doesn't exist
            return await self._direct_chunk_search(query_embedding, threshold)
    
    async def _direct_chunk_search(self, query_embedding: List[float], threshold: float) -> List[Dict]:
        """Direct SQL search for chunks (fallback method)"""
        try:
            result = supabase.table('context_chunks') \
                .select('context_id, content, embedding') \
                .limit(50) \
                .execute()
                
            logger.info(f"Raw query returned {len(result.data) if result.data else 0} chunks")
            
            if result.data:
                filtered_results = []
                
                for row in result.data:
                    embedding_data = self._parse_embedding(row['embedding'])
                    if embedding_data is None:
                        continue
                        
                    embedding = np.array(embedding_data, dtype=np.float32)
                    query_emb = np.array(query_embedding, dtype=np.float32)
                    
                    # Cosine similarity = dot product / (norm1 * norm2)
                    similarity = np.dot(embedding, query_emb) / (np.linalg.norm(embedding) * np.linalg.norm(query_emb))
                    
                    # Show content for high similarity chunks
                    if similarity >= 0.5:
                        content_preview = row['content'][:150] + "..." if len(row['content']) > 150 else row['content']
                        logger.info(f"HIGH similarity {similarity:.4f}: {content_preview}")
                    else:
                        logger.info(f"Chunk similarity: {similarity:.4f} (threshold: {threshold})")
                    
                    if similarity >= threshold:
                        row['similarity'] = float(similarity)
                        del row['embedding']  # Remove embedding to reduce response size
                        filtered_results.append(row)
                
                # Sort by similarity descending
                filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
                return filtered_results[:50]
                    
            return []
            
        except Exception as e:
            logger.error(f"Direct chunk search failed: {str(e)}")
            return []
    
    async def _search_metadata(self, query_embedding: List[float], threshold: float) -> List[Dict]:
        """Search for similar metadata using pgvector cosine similarity"""
        try:
            # Using Supabase's vector similarity search for metadata
            result = supabase.rpc('search_metadata', {
                'query_embedding': query_embedding,
                'similarity_threshold': threshold,
                'match_count': 20
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.warning(f"RPC search failed, falling back to direct query: {str(e)}")
            # Fallback to direct SQL
            return await self._direct_metadata_search(query_embedding, threshold)
    
    async def _direct_metadata_search(self, query_embedding: List[float], threshold: float) -> List[Dict]:
        """Direct SQL search for metadata (fallback method)"""
        try:
            result = supabase.table('context_metadata') \
                .select('context_id, content, metadata_json, embedding') \
                .limit(20) \
                .execute()
            
            if result.data:
                filtered_results = []
                
                for row in result.data:
                    embedding_data = self._parse_embedding(row['embedding'])
                    if embedding_data is None:
                        continue
                        
                    embedding = np.array(embedding_data, dtype=np.float32)
                    query_emb = np.array(query_embedding, dtype=np.float32)
                    
                    similarity = np.dot(embedding, query_emb) / (np.linalg.norm(embedding) * np.linalg.norm(query_emb))
                    
                    # Show content for high similarity metadata
                    if similarity >= 0.3:
                        content_preview = row['content'][:150] + "..." if len(row['content']) > 150 else row['content']
                        metadata_json = row.get('metadata_json', {})
                        logger.info(f"METADATA similarity {similarity:.4f}: {content_preview}")
                        if metadata_json:
                            logger.info(f"  Metadata: {str(metadata_json)[:200]}...")
                    
                    if similarity >= threshold:
                        row['similarity'] = float(similarity)
                        del row['embedding']
                        filtered_results.append(row)
                
                filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
                return filtered_results
                    
            return []
            
        except Exception as e:
            logger.error(f"Direct metadata search failed: {str(e)}")
            return []
    
    async def _rank_and_fetch_contexts(self, 
                                     contexts_scores: Dict, 
                                     user_id: str, 
                                     top_k: int) -> List[Dict]:
        """
        Calculate composite scores and fetch context details
        
        Scoring strategy:
        - 70% weight on best chunk similarity
        - 20% weight on metadata similarity (if available)  
        - 10% weight on number of matching chunks (diversity bonus)
        """
        scored_contexts = []
        
        for context_id, scores in contexts_scores.items():
            # Base score from best chunk match
            composite_score = scores['max_chunk_similarity'] * 0.7
            
            # Add metadata similarity bonus
            if scores['has_metadata']:
                metadata_score = scores.get('metadata_similarity', 0)
                composite_score += metadata_score * 0.2
            
            # Add diversity bonus based on number of matching chunks
            chunk_bonus = min(scores['chunk_count'] / 10.0, 0.1)  # Max 10% bonus
            composite_score += chunk_bonus
            
            # Average chunk similarity for additional insight
            avg_chunk_similarity = (
                sum(scores['chunk_similarities']) / len(scores['chunk_similarities'])
                if scores['chunk_similarities'] else 0
            )
            
            scored_contexts.append({
                'context_id': context_id,
                'composite_score': composite_score,
                'max_chunk_similarity': scores['max_chunk_similarity'],
                'avg_chunk_similarity': avg_chunk_similarity,
                'metadata_similarity': scores.get('metadata_similarity', 0),
                'matching_chunks_count': scores['chunk_count'],
                'has_metadata': scores['has_metadata']
            })
        
        # Sort by composite score
        scored_contexts.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Get top K context IDs
        top_context_ids = [ctx['context_id'] for ctx in scored_contexts[:top_k]]
        
        if not top_context_ids:
            return []
        
        # Fetch context details with associated asset details using JOIN
        contexts_query = supabase.table('contexts') \
            .select('id, source, processing_status, created_at, context_assets(id, original_filename, source_url, storage_bucket, storage_path)') \
            .in_('id', top_context_ids) \
            .eq('user_id', user_id)
        
        contexts_result = contexts_query.execute()
        
        if not contexts_result.data:
            return []
        
        # Build context to asset mapping
        context_details_map = {}
        for ctx in contexts_result.data:
            context_id = ctx['id']
            
            # Handle different possible data structures from Supabase JOIN
            asset = None
            if 'context_assets' in ctx and ctx['context_assets']:
                if isinstance(ctx['context_assets'], list) and len(ctx['context_assets']) > 0:
                    asset = ctx['context_assets'][0]
                elif isinstance(ctx['context_assets'], dict) and 'id' in ctx['context_assets']:
                    asset = ctx['context_assets']
            
            context_details_map[context_id] = {
                'source': ctx.get('source'),
                'processing_status': ctx.get('processing_status'),
                'created_at': ctx.get('created_at'),
                'asset': asset
            }
        
        # Build final results with context_id and asset_id
        final_results = []
        for scored_ctx in scored_contexts[:top_k]:
            context_id = scored_ctx['context_id']
            details = context_details_map.get(context_id)
            if details is not None:
                # Choose the best available snippet
                snippet = contexts_scores.get(context_id, {}).get('top_chunk_content') or \
                          contexts_scores.get(context_id, {}).get('top_metadata_content')
                # Trim long snippets for safety
                if isinstance(snippet, str) and len(snippet) > 500:
                    snippet = snippet[:500] + '...'

                # Attempt to retrieve raw HTML from storage for this context via associated asset
                raw_html_content = None
                asset_info = details.get('asset') if isinstance(details, dict) else None
                try:
                    if asset_info and isinstance(asset_info, dict):
                        storage_path = asset_info.get('storage_path')
                        # Fallback: derive from uploaded_filename if explicit path is missing (legacy rows)
                        if not storage_path:
                            uploaded_filename = asset_info.get('uploaded_filename')
                            if uploaded_filename:
                                sanitized_filename = self.storage_service._sanitize_filename(uploaded_filename)
                                storage_path = f"{user_id}/{sanitized_filename}"
                                logger.info(f"Derived storage path from uploaded_filename for context {context_id}: {storage_path} (sanitized from: {uploaded_filename})")

                        if storage_path:
                            logger.info(f"Downloading raw HTML for context {context_id} from storage path: {storage_path}")
                            html_bytes = self.storage_service.get_html_file(storage_path)
                            if html_bytes:
                                raw_html_content = html_bytes.decode('utf-8', errors='ignore')
                                logger.info(f"Successfully retrieved raw HTML for context {context_id} (length={len(raw_html_content)})")
                            else:
                                logger.warning(f"No data returned when downloading raw HTML for context {context_id}")
                        else:
                            logger.info(f"No storage_path on asset for context {context_id}; skipping raw HTML fetch")
                    else:
                        logger.info(f"No asset info for context {context_id}; skipping raw HTML fetch")
                except Exception as e:
                    logger.warning(f"Failed to retrieve raw HTML for context {context_id}: {str(e)}")

                result = {
                    # IDs
                    'id': context_id,  # also expose as `id` for frontend convenience
                    'context_id': context_id,
                    # Ranking
                    'relevance_score': scored_ctx['composite_score'],
                    'max_chunk_similarity': scored_ctx['max_chunk_similarity'],
                    'avg_chunk_similarity': scored_ctx['avg_chunk_similarity'],
                    'metadata_similarity': scored_ctx['metadata_similarity'],
                    'matching_chunks_count': scored_ctx['matching_chunks_count'],
                    'has_metadata_match': scored_ctx['has_metadata'],
                    # Content & metadata
                    'content': snippet,
                    'raw_html': raw_html_content,
                    'source': details.get('source'),
                    'processing_status': details.get('processing_status'),
                    'created_at': details.get('created_at'),
                    'asset': details.get('asset')
                }
                final_results.append(result)
        
        return final_results