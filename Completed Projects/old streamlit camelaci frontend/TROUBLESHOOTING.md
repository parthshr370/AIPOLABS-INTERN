# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Asyncio Errors in Streamlit

**Error Messages:**
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
asyncio - ERROR - an error occurred during closing of asynchronous generator
```

**Solution:**
The app now includes `nest-asyncio` to handle these issues automatically. If you still see these errors:

1. **Install nest-asyncio:**
   ```bash
   pip install nest-asyncio
   ```

2. **Restart the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **These errors are usually non-critical** - the app should still work correctly even if you see them in the console.

### 2. MCP Connection Issues

**Error Messages:**
```
Failed to connect to MCP server
Failed to call MCP tool 'BRAVE_SEARCH__WEB_SEARCH'
```

**Solutions:**

1. **Check ACI API Key:**
   - Verify your ACI API key is correct in the sidebar
   - Test it at [ACI Platform](https://platform.aci.dev/apps)

2. **Verify Linked Account Owner ID:**
   - Make sure your Linked Account Owner ID is correct
   - This should match what you set up during OAuth flow

3. **Install uvx and aci-mcp:**
   ```bash
   pip install uv
   uvx install aci-mcp
   ```

4. **Check Internet Connection:**
   - MCP server needs internet access to connect to ACI services

### 3. Tool Loading Issues

**Symptoms:**
- "No tools available" message
- Tools show as "Unknown" names

**Solutions:**

1. **The app will work in fallback mode** without external tools
2. **Check MCP server logs** in the terminal for specific errors
3. **Verify your ACI account** has access to the required apps (BRAVE_SEARCH, GITHUB, ARXIV)

### 4. Streamlit-Specific Issues

**Error: "This app has encountered an error"**

**Solutions:**

1. **Clear Streamlit cache:**
   ```bash
   streamlit cache clear
   ```

2. **Restart the app:**
   - Stop with Ctrl+C
   - Run again: `streamlit run streamlit_app.py`

3. **Check browser console** for JavaScript errors

### 5. Environment Variable Issues

**Error: "Please fill in all required fields"**

**Solutions:**

1. **Check .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify .env format:**
   ```env
   GOOGLE_API_KEY="your_actual_key_here"
   ACI_API_KEY="your_actual_key_here"
   LINKED_ACCOUNT_OWNER_ID="your_actual_id_here"
   ```

3. **No spaces around the = sign**
4. **Use quotes around values**

### 6. Model/API Issues

**Error: "Failed to create model" or API errors**

**Solutions:**

1. **Check Google API Key:**
   - Test at [Google AI Studio](https://aistudio.google.com/)
   - Make sure it has Gemini access

2. **Try different model:**
   - Switch to `gemini-1.5-flash` in sidebar (faster, cheaper)
   - Reduce max tokens if hitting limits

3. **Check API quotas:**
   - Google AI Studio has rate limits
   - Wait a few minutes and try again

## Debug Mode

### Enable Detailed Logging

1. **Use the Raw Output expander** in the app to see detailed information
2. **Check terminal output** where you ran `streamlit run`
3. **Run the test script:**
   ```bash
   python test_app.py
   ```

### Manual Testing

Test individual components:

1. **Test CLI version:**
   ```bash
   python camel_mcp_aci.py
   ```

2. **Test MCP connection:**
   ```bash
   uvx aci-mcp apps-server --apps=BRAVE_SEARCH --linked-account-owner-id=your_id
   ```

## Performance Tips

### Reduce Latency

1. **Use gemini-1.5-flash** instead of gemini-2.5-pro
2. **Lower temperature** (0.3-0.5) for faster responses
3. **Reduce max tokens** to 10000-20000 for shorter responses

### Handle Rate Limits

1. **Wait between requests** if you hit API limits
2. **Use smaller queries** to reduce token usage
3. **Check your API quotas** in Google AI Studio

## Still Having Issues?

### Fallback Mode

The app is designed to work even if MCP tools fail:
- ✅ **Basic AI responses** will still work
- ❌ **No external search/GitHub/arXiv access**
- 💡 **Perfect for testing** the interface

### Get Help

1. **Check the main README.md** for setup instructions
2. **Run the test script:** `python test_app.py`
3. **Look at the original CLI version** to compare behavior
4. **Check CAMEL-AI documentation** for model issues

### Emergency Reset

If everything breaks:

```bash
# Stop the app
# Ctrl+C

# Clear everything
rm config.json
streamlit cache clear

# Restart fresh
streamlit run streamlit_app.py
```

The app will recreate the config and start fresh. 