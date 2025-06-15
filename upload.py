#!/usr/bin/env python3
# Script to upload all plugins from a folder to the Ultroid Plugin Store.

import asyncio
import aiohttp
import json
import base64
import os

from dotenv import load_dotenv
load_dotenv()

import logging
from pathlib import Path
from typing import Optional

# AI-related imports
try:
    from openai import OpenAI
except ImportError:
    print("Error: 'openai' is not installed. Please install it with 'pip install openai'")
    exit(1)


# Import from Ultroid modules
from pyUltroid.state_config import temp_config_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_plugin_metadata_with_ai(file_content: str, model_client: OpenAI) -> Optional[dict]:
    """
    Analyzes plugin code using an AI model to extract metadata.

    Args:
        file_content: The source code of the plugin.
        model_client: The AI client to use for analysis.

    Returns:
        A dictionary with extracted metadata or None on failure.
    """
    logger.info("Analyzing plugin with AI to extract metadata...")
    system_prompt = """
You are an expert Python developer specializing in Ultroid plugins.
Your task is to analyze a given plugin file and extract specific metadata.
Respond with ONLY a valid JSON object containing the following keys:
- "description": A short, clear description of what the plugin does, derived from its docstring or overall purpose.
- "commands": A list of strings, where each string is a command pattern (e.g., "ping", "start"). Find these in `@ultroid_cmd(pattern="...")` decorators.
- "packages": A list of strings, where each string is an external pip package required by the plugin. Analyze the import statements to determine these. Common built-in modules should be ignored.
"""
    
    user_prompt = f"""
Analyze this Ultroid plugin code and return the metadata as a JSON object.

```python
{file_content}
```
"""
    
    try:
        response = model_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        print(content)
        metadata = json.loads(content)
        logger.info("Successfully extracted metadata from AI.")
        return metadata

    except (json.JSONDecodeError, IndexError) as e:
        logger.error(f"Failed to get or parse AI response: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during AI analysis: {e}")
        return None

async def upload_addon_plugins():
    """
    Scans the UltroidAddons folder, extracts metadata for each plugin,
    and uploads them to the plugin store.
    """
    api_url = "http://localhost:8055"
    bot_id = 1444249738  # Placeholder, adjust if needed

    # Get stored authentication data
    encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{bot_id}")
    encoded_hash = temp_config_store.get(f"X-TG-HASH-{bot_id}")
    
    if not encoded_init_data or not encoded_hash:
        logger.error("Authentication data not found. Please authenticate with Ultroid Central first.")
        return

    init_data = base64.b64decode(encoded_init_data.encode()).decode()
    hash_value = base64.b64decode(encoded_hash.encode()).decode()
    
    # Initialize AI Client
    token = os.environ.get("GROQ_API_KEY")
    if not token:
        logger.error("GROQ_API_KEY not found in environment variables.")
        return
        
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=token,
    )
    
    # Path to addons, assuming it's a sibling to the 'Ultroid' directory
    addon_path = Path("addons_copy")
    if not addon_path.exists() or not addon_path.is_dir():
        logger.error(f"Could not find the UltroidAddons directory at: {addon_path}")
        return

    logger.info(f"Scanning for plugins in: {addon_path}")

    async with aiohttp.ClientSession() as session:
        for plugin_path in sorted(addon_path.glob("*.py")):
            if plugin_path.name == "__init__.py":
                continue

            logger.info(f"--- Processing plugin: {plugin_path.name} ---")
            
            try:
                content = plugin_path.read_text(encoding='utf-8')
                metadata = get_plugin_metadata_with_ai(content, client)

                if not metadata:
                    logger.warning(f"Could not get metadata for {plugin_path.name}. Skipping.")
                    continue

                # Prepare JSON data
                json_data = {
                    "title": plugin_path.stem.replace('_', ' ').title(),
                    "description": metadata.get("description", "N/A"),
                    "tags": ["community", plugin_path.stem],
                    "packages": metadata.get("packages", []),
                    "commands": metadata.get("commands", []),
                    "is_trusted": True,
                    "is_official": True,
                    "plugin_filename": plugin_path.name,
                    "plugin_content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
                }
                
                # Prepare headers with authentication
                headers = {
                    "Content-Type": "application/json",
                    "X-Telegram-Init-Data": init_data,
                    "X-Telegram-Hash": hash_value
                }
                
                # Upload the plugin
                logger.info(f"Uploading '{json_data['title']}'...")
                plugin_url = f"{api_url}/api/v1/plugins"
                
                async with session.post(
                    plugin_url, 
                    json=json_data,
                    headers=headers
                ) as response:
                    status = response.status
                    resp_text = await response.text()
                    
                    if status in (200, 201):
                        logger.info(f"Successfully uploaded '{json_data['title']}'. Status: {status}")
                    else:
                        logger.error(f"Failed to upload '{json_data['title']}'. Status: {status}, Response: {resp_text[:200]}")

            except Exception as e:
                logger.error(f"An unexpected error occurred while processing {plugin_path.name}: {e}")

            # Optional: Add a small delay to avoid overwhelming the server or AI service
            await asyncio.sleep(1)

async def delete_all_plugins():
    """Delete all plugins uploaded by the current user."""
    api_url = "http://localhost:8055"
    bot_id = 1444249738  # Placeholder, adjust if needed

    # Get stored authentication data
    encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{bot_id}")
    encoded_hash = temp_config_store.get(f"X-TG-HASH-{bot_id}")
    
    if not encoded_init_data or not encoded_hash:
        logger.error("Authentication data not found. Please authenticate with Ultroid Central first.")
        return

    init_data = base64.b64decode(encoded_init_data.encode()).decode()
    hash_value = base64.b64decode(encoded_hash.encode()).decode()

    # Prepare headers with authentication
    headers = {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": init_data,
        "X-Telegram-Hash": hash_value
    }

    async with aiohttp.ClientSession() as session:
        plugin_url = f"{api_url}/api/v1/plugins/user/plugins"
        
        async with session.delete(
            plugin_url,
            headers=headers
        ) as response:
            status = response.status
            resp_text = await response.text()
            
            if status in (200, 201):
                data = json.loads(resp_text)
                logger.info(f"Successfully deleted {data.get('deleted_count', 0)} plugins")
            else:
                logger.error(f"Failed to delete plugins. Status: {status}, Response: {resp_text[:200]}")

async def upload_single_plugin(plugin_path_str):
    """
    Upload a single plugin file to the plugin store.
    """
    api_url = "http://localhost:8055"
    bot_id = 1444249738  # Placeholder, adjust if needed

    # Get stored authentication data
    encoded_init_data = temp_config_store.get(f"X-TG-INIT-DATA-{bot_id}")
    encoded_hash = temp_config_store.get(f"X-TG-HASH-{bot_id}")
    
    if not encoded_init_data or not encoded_hash:
        logger.error("Authentication data not found. Please authenticate with Ultroid Central first.")
        return

    init_data = base64.b64decode(encoded_init_data.encode()).decode()
    hash_value = base64.b64decode(encoded_hash.encode()).decode()

    # Initialize AI Client
    token = os.environ.get("GROQ_API_KEY")
    if not token:
        logger.error("GROQ_API_KEY not found in environment variables.")
        return
        
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=token,
    )

    plugin_path = Path(plugin_path_str)
    if not plugin_path.exists() or not plugin_path.is_file():
        logger.error(f"Plugin file not found: {plugin_path}")
        return

    logger.info(f"Processing single plugin: {plugin_path.name}")

    async with aiohttp.ClientSession() as session:
        try:
            content = plugin_path.read_text(encoding='utf-8')
            metadata = get_plugin_metadata_with_ai(content, client)

            if not metadata:
                logger.warning(f"Could not get metadata for {plugin_path.name}.")
                return

            # Prepare JSON data
            json_data = {
                "title": plugin_path.stem.replace('_', ' ').title(),
                "description": metadata.get("description", "N/A"),
                "tags": ["community", plugin_path.stem],
                "packages": metadata.get("packages", []),
                "commands": metadata.get("commands", []),
                "is_trusted": True,
                "is_official": True,
                "plugin_filename": plugin_path.name,
                "plugin_content": base64.b64encode(content.encode('utf-8')).decode('utf-8')
            }
            
            # Prepare headers with authentication
            headers = {
                "Content-Type": "application/json",
                "X-Telegram-Init-Data": init_data,
                "X-Telegram-Hash": hash_value
            }
            
            # Upload the plugin
            logger.info(f"Uploading '{json_data['title']}'...")
            plugin_url = f"{api_url}/api/v1/plugins"
            
            async with session.post(
                plugin_url, 
                json=json_data,
                headers=headers
            ) as response:
                status = response.status
                resp_text = await response.text()
                
                if status in (200, 201):
                    logger.info(f"Successfully uploaded '{json_data['title']}'. Status: {status}")
                else:
                    logger.error(f"Failed to upload '{json_data['title']}'. Status: {status}, Response: {resp_text[:200]}")

        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {plugin_path.name}: {e}")

if __name__ == "__main__":
    import sys
    import argparse

    if "GROQ_API_KEY" not in os.environ:
        print("Error: GROQ_API_KEY environment variable is not set.")
        print("Please set it to a valid Groq API key.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Ultroid Plugin Store Management')
    parser.add_argument('action', choices=['upload', 'delete', 'upload_one'], 
                       help='Action to perform: upload all, upload one, or delete all plugins')
    parser.add_argument('--path', type=str, help='Path to the plugin file (for upload_one)')

    args = parser.parse_args()

    if args.action == 'upload':
        asyncio.run(upload_addon_plugins())
    elif args.action == 'delete':
        asyncio.run(delete_all_plugins())
    elif args.action == 'upload_one':
        if not args.path:
            print("Please provide --path to the plugin file for upload_one.")
            sys.exit(1)
        asyncio.run(upload_single_plugin(args.path)) 