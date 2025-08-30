#!/usr/bin/env python3
import asyncio
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

async def debug_tools_processing():
    """Debug the exact point where tools processing fails"""
    try:
        from create_config import create_config
        from camel.toolkits import MCPToolkit
        
        print("🔧 Creating config...")
        create_config()
        
        print("🔌 Connecting to MCP toolkit...")
        mcp_toolkit = MCPToolkit(config_path='config.json')
        await mcp_toolkit.connect()
        
        print("📋 Checking servers...")
        for server_name, server in mcp_toolkit.servers.items():
            print(f"Server: {server_name}")
            
            # Get raw tools first
            raw_tools_response = await server._client.call_function("tools/list")
            raw_tools = raw_tools_response.tools if hasattr(raw_tools_response, 'tools') else []
            print(f"Raw tools count: {len(raw_tools)}")
            
            # Try processing tools one by one
            processed_tools = []
            for i, tool in enumerate(raw_tools):
                try:
                    print(f"Processing tool {i+1}: {getattr(tool, 'name', 'Unknown')}")
                    processed_tool = server.generate_function_from_mcp_tool(tool)
                    processed_tools.append(processed_tool)
                    print(f"  ✅ Success")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    if "unhashable type: 'list'" in str(e):
                        print(f"  🔍 Investigating tool schema...")
                        if hasattr(tool, 'inputSchema') and tool.inputSchema:
                            print(f"    Input schema type: {type(tool.inputSchema)}")
                            if hasattr(tool.inputSchema, 'properties'):
                                print(f"    Properties: {tool.inputSchema.properties}")
                                for prop_name, prop_data in tool.inputSchema.properties.items():
                                    print(f"      {prop_name}: {type(prop_data)} -> {prop_data}")
                                    if isinstance(prop_data, dict) and 'type' in prop_data:
                                        param_type = prop_data['type']
                                        print(f"        type: {type(param_type)} -> {param_type}")
                                        if isinstance(param_type, list):
                                            print(f"        ⚠️  FOUND LIST TYPE: {param_type}")
                        break  # Stop after first error to examine
            
            print(f"Successfully processed: {len(processed_tools)} tools")
        
        await mcp_toolkit.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_tools_processing()) 