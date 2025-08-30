# Contextual Database Chrome Extension

A browser extension that captures webpage content, processes it through an AI-powered pipeline, and enables contextual search across your browsed content.

## Overview

This system allows users to:
1. Capture webpage HTML content via browser extension
2. Process and store content in a personal contextual database
3. Search through captured content using natural language queries
4. Retrieve and return several most relevant raw webpage content


## Tech Stack

- **Frontend**: Chrome Extension (Manifest V3)
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Search**: RAG with vector embeddings
- **Containerization**: Docker

## Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Configure your Supabase credentials
   ```

2. **Start Services**:
   ```bash
   docker-compose up -d
   ```

3. **Install Extension**:

## Features

### Capture & Process
- One-click webpage content capture
- Intelligent content cleaning (removes ads, navigation, etc.)
- Text chunking for optimal processing
- Vector embedding generation for semantic search

### Search & Retrieve
- Natural language search queries
- Semantic similarity matching using pgvector
- Return relevant webpage URLs when accessible
- Personal content database per user

## Usage

1. **Capture Content**: Click extension icon on any webpage to save content
2. **Search Content**: Use extension popup to search your captured content
3. **View Results**: Get relevant webpages ranked by contextual similarity

## Development

See individual documentation files in `/docs` for detailed technical specifications:
- API endpoints and request/response formats
- Database schema and table structures  
- Data processing pipeline workflow

## License

Private project - All rights reserved