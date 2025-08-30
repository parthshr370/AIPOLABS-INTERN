"""
Utility functions for deep memory research pipeline
Handles paths, artifact persistence, and common functionality
"""

import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Union

# Project root and path setup  
ROOT = pathlib.Path(__file__).resolve().parent  # Current directory is now root
ARTIFACTS_DIR = ROOT / "artifacts"

# Add required modules to Python path
sys.path.append(str(ROOT / "camel"))
sys.path.append(str(ROOT / "mem0"))

# Ensure artifacts directory exists
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def get_timestamp() -> str:
    """Get current timestamp string for artifact naming"""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def save_artifact(kind: str, data: Union[str, Dict[str, Any]], ext: str = "json") -> str:
    """
    Save data as timestamped artifact
    
    Args:
        kind: Type of artifact (metadata, plan, search_list, etc.)
        data: Data to save (string or dict)
        ext: File extension (json, md, jsonl)
    
    Returns:
        str: Path to saved file
    """
    timestamp = get_timestamp()
    filename = f"{timestamp}_{kind}.{ext}"
    filepath = ARTIFACTS_DIR / filename
    
    if isinstance(data, dict):
        content = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        content = str(data)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return str(filepath)


def save_jsonl_artifact(kind: str, data_list: list) -> str:
    """
    Save list of objects as JSONL artifact
    
    Args:
        kind: Type of artifact 
        data_list: List of objects to save as JSONL
        
    Returns:
        str: Path to saved file
    """
    timestamp = get_timestamp()
    filename = f"{timestamp}_{kind}.jsonl"
    filepath = ARTIFACTS_DIR / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    return str(filepath)


def load_artifact(filepath: str) -> Union[str, Dict[str, Any], list]:
    """
    Load artifact from file
    
    Args:
        filepath: Path to artifact file
        
    Returns:
        Content of the file (parsed if JSON)
    """
    filepath = pathlib.Path(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Try to parse as JSON
    if filepath.suffix == ".json":
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content
    elif filepath.suffix == ".jsonl":
        # Parse JSONL
        lines = []
        for line in content.strip().split("\n"):
            if line.strip():
                try:
                    lines.append(json.loads(line))
                except json.JSONDecodeError:
                    lines.append(line)
        return lines
    else:
        return content


def get_latest_artifact(kind: str, ext: str = "json") -> Union[str, None]:
    """
    Get path to most recent artifact of given kind
    
    Args:
        kind: Type of artifact to find
        ext: File extension
        
    Returns:
        Path to latest artifact or None if not found
    """
    pattern = f"*_{kind}.{ext}"
    artifacts = list(ARTIFACTS_DIR.glob(pattern))
    
    if not artifacts:
        return None
    
    # Sort by creation time, return latest
    latest = max(artifacts, key=lambda x: x.stat().st_ctime)
    return str(latest)


def list_artifacts() -> Dict[str, list]:
    """
    List all artifacts by type
    
    Returns:
        Dictionary mapping artifact types to file lists
    """
    artifacts = {}
    
    for file in ARTIFACTS_DIR.glob("*"):
        if file.is_file():
            # Extract kind from filename (timestamp_kind.ext)
            parts = file.stem.split("_", 1)
            if len(parts) == 2:
                kind = parts[1]
                if kind not in artifacts:
                    artifacts[kind] = []
                artifacts[kind].append(str(file))
    
    return artifacts


def clean_old_artifacts(keep_recent: int = 10):
    """
    Clean old artifacts, keeping only the most recent ones
    
    Args:
        keep_recent: Number of recent artifacts to keep per type
    """
    artifacts_by_type = list_artifacts()
    
    for artifact_type, files in artifacts_by_type.items():
        if len(files) > keep_recent:
            # Sort by modification time
            files_with_time = [(f, pathlib.Path(f).stat().st_mtime) for f in files]
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            
            # Remove older files
            for file_path, _ in files_with_time[keep_recent:]:
                try:
                    pathlib.Path(file_path).unlink()
                    print(f"Cleaned old artifact: {file_path}")
                except Exception as e:
                    print(f"Failed to clean {file_path}: {e}")


if __name__ == "__main__":
    # Test the utilities
    print(f"ROOT: {ROOT}")
    print(f"ARTIFACTS_DIR: {ARTIFACTS_DIR}")
    print(f"Timestamp: {get_timestamp()}")
    
    # Test save/load
    test_data = {"test": "data", "timestamp": get_timestamp()}
    saved_path = save_artifact("test", test_data)
    print(f"Saved to: {saved_path}")
    
    loaded_data = load_artifact(saved_path)
    print(f"Loaded: {loaded_data}")
    
    # List artifacts
    print(f"Artifacts: {list_artifacts()}")