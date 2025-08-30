#!/usr/bin/env python3
"""
Script to insert real test data from processing pipeline output into the database.
Uses actual processed HTML files from test_end_to_end/output/ directory.
"""

import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.supabase_client import supabase
import uuid
from datetime import datetime

def clear_test_data():
    """Clear all existing test data from tables"""
    print("🧹 Clearing existing test data...")
    
    try:
        # Delete in correct order due to foreign key constraints
        result1 = supabase.table('context_chunks').delete().gte('created_at', '1900-01-01').execute()
        print(f"   Cleared {len(result1.data) if result1.data else 0} chunks")
        
        result2 = supabase.table('context_metadata').delete().gte('created_at', '1900-01-01').execute()
        print(f"   Cleared {len(result2.data) if result2.data else 0} metadata entries")
        
        result3 = supabase.table('contexts').delete().gte('created_at', '1900-01-01').execute()
        print(f"   Cleared {len(result3.data) if result3.data else 0} contexts")
        
        print("✅ Test data cleared successfully!")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not clear all data: {e}")
        print("   Continuing with data insertion...")

def create_context_from_file(user_id: str, processed_data: dict, source_filename: str):
    """Create a context entry from processed file data"""
    
    # Determine processing status based on success
    processing_status = 'success' if processed_data.get('success', False) else 'failed'
    
    context_data = {
        'user_id': user_id,
        'source': 'html',
        'processing_status': processing_status,
        'chunks_count': len(processed_data.get('chunks', [])),
        'metadata_count': 1 if processed_data.get('metadata') else 0,
        'error': processed_data.get('error') if not processed_data.get('success', False) else None,
    }
    
    result = supabase.table('contexts').insert(context_data).execute()
    context = result.data[0] if result.data else None
    
    if context:
        print(f"✅ Created context for {source_filename}: {context['id']}")
    
    return context

def create_chunks_from_data(context_id: str, processed_data: dict):
    """Create chunks from processed file data"""
    chunks_data = processed_data.get('chunks', [])
    embeddings_data = processed_data.get('chunks_embeddings', [])
    
    if not chunks_data:
        return []
    
    # Prepare chunk records
    chunk_records = []
    for i, chunk_content in enumerate(chunks_data):
        # Use real embedding if available, otherwise use a placeholder
        if i < len(embeddings_data) and embeddings_data[i]:
            embedding = embeddings_data[i]
        else:
            embedding = [0.0] * 1536
        
        chunk_record = {
            'context_id': context_id,
            'chunk_index': i,
            'content': chunk_content,
            'embedding': embedding
        }
        chunk_records.append(chunk_record)
    
    if chunk_records:
        result = supabase.table('context_chunks').insert(chunk_records).execute()
        chunks = result.data if result.data else []
        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    
    return []

def create_metadata_from_data(context_id: str, processed_data: dict, source_filename: str):
    """Create metadata from processed file data"""
    metadata_content = processed_data.get('metadata', {})
    metadata_embedding = processed_data.get('metadata_embeddings', [])
    
    if not metadata_content:
        # Create basic metadata from available info
        metadata_content = {
            'source_file': source_filename,
            'processing_success': processed_data.get('success', False),
            'chunks_count': len(processed_data.get('chunks', [])),
            'source_type': processed_data.get('source', 'html')
        }
    
    # Use real embedding if available, otherwise use a placeholder  
    if not metadata_embedding:
        metadata_embedding = [0.0] * 1536
    elif metadata_embedding and len(metadata_embedding) > 0:
        # metadata_embeddings is a list of embeddings, we want the first one
        metadata_embedding = metadata_embedding[0]
    
    metadata_data = {
        'context_id': context_id,
        'content': f"Document: {source_filename} - Processed HTML content with {len(processed_data.get('chunks', []))} text chunks",
        'metadata_json': metadata_content,
        'embedding': metadata_embedding
    }
    
    result = supabase.table('context_metadata').insert(metadata_data).execute()
    metadata = result.data[0] if result.data else None
    
    if metadata:
        print(f"✅ Created metadata: {metadata['id']}")
    
    return metadata

def load_processed_files():
    """Load all processed JSON files from output directory"""
    script_dir = Path(__file__).parent
    output_dir = script_dir / '..' / 'app' / 'processing' / 'test_end_to_end' / 'output'
    
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        return []
    
    json_files = list(output_dir.glob("*.json"))
    
    if not json_files:
        print(f"⚠️  No JSON files found in {output_dir}")
        return []
    
    processed_files = []
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                processed_files.append((json_file.name, data))
                print(f"📄 Loaded: {json_file.name}")
        except Exception as e:
            print(f"⚠️  Failed to load {json_file.name}: {e}")
    
    return processed_files

def main():
    """Main function to insert real test data"""
    print("🚀 Starting real test data insertion...")
    
    # Clear existing test data first
    clear_test_data()
    
    # Load processed files
    processed_files = load_processed_files()
    
    if not processed_files:
        print("❌ No processed files found to insert")
        return
    
    # Using real user_id from auth.users table
    test_user_id = "6890cf8d-7699-4eb8-a06e-391209b89ade"
    print(f"✅ Using real user ID: {test_user_id}")
    
    try:
        print(f"\n📝 Processing {len(processed_files)} files...")
        
        successful_count = 0
        failed_count = 0
        
        for filename, processed_data in processed_files:
            print(f"\n📄 Processing {filename}...")
            
            # Create context
            context = create_context_from_file(test_user_id, processed_data, filename)
            
            if context and context['processing_status'] == 'success':
                # Create chunks for successful contexts
                chunks = create_chunks_from_data(context['id'], processed_data)
                
                # Create metadata
                metadata = create_metadata_from_data(context['id'], processed_data, filename)
                
                successful_count += 1
            elif context:
                # Failed processing, but context was created
                failed_count += 1
            else:
                print(f"❌ Failed to create context for {filename}")
                failed_count += 1
        
        print("\n" + "="*50)
        print(f"📊 Data Insertion Summary:")
        print(f"   ✅ Successful contexts: {successful_count}")
        print(f"   ❌ Failed contexts: {failed_count}")
        print(f"   📁 Total files processed: {len(processed_files)}")
        print("\n🎉 Real test data insertion completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error inserting real test data: {e}")
        print("\n💡 Tips:")
        print("1. Make sure your .env file has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        print("2. Make sure the database schema is updated with processing_status field")
        print("3. Run the processing pipeline first to generate output files")

if __name__ == "__main__":
    main()