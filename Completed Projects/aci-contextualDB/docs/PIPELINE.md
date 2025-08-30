# Data Processing Pipeline Documentation

This document describes the data processing pipeline that transforms raw documents into searchable, contextually-aware content through a four-stage process: clean → chunk → embed → upsert.

## Pipeline Overview

The processing pipeline consists of four sequential stages:

1. **Clean**: Document preprocessing and text normalization
2. **Chunk**: Document segmentation into manageable pieces
3. **Embed**: Vector embedding generation for semantic search
4. **Upsert**: Database storage and indexing