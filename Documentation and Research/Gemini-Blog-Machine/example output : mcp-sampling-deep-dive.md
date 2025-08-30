# Understanding MCP Sampling: A Deep Dive into the Model Context Protocol

Ever wondered how an AI assistant in your code editor can suddenly access your company’s private documentation, or how a chatbot can seamlessly book a flight for you? The magic lies in a concept called "tooling," but until recently, it's been a bit of a wild west. Every AI provider had its own way of doing things, making it a headache to connect different systems. What if there was a universal translator for AI tools?

That's where the Model Context Protocol (MCP) comes in. It’s a game-changing open standard that lets any LLM, agent, or editor hook up with tools from any source. In this deep dive, we'll explore MCP, how it handles tooling, and a key feature called "MCP Sampling," which allows for powerful, human-in-the-loop AI workflows.

<!-- Diagram: A diagram illustrating the MCP client-server architecture -->
![Image: A diagram illustrating the MCP client-server architecture.](placeholder)

## What is the Model Context Protocol (MCP)?

At its heart, MCP is a simple but powerful idea. It creates a standardized way for AI models (the "clients") to talk to tools and data sources (the "servers"). Think of it like a universal USB port for AI. No matter the brand or type of device, you can plug it in and it just works.

This communication happens using a well-known standard called JSON-RPC 2.0. It’s a lightweight way to send messages back and forth between the client and server. The client can ask the server, "What can you do?" and the server will respond with a list of its "capabilities." These capabilities can be tools (like "create a GitHub repository"), resources (like "get the latest user data"), or prompts (pre-defined templates to help the LLM).

## MCP Tooling: How LLMs Discover and Select Tools

So, how does an LLM actually use these tools? The process starts with the client sending a `mcp/getCapabilities` request to the server. The server then sends back a list of all the tools it has to offer. This is like the LLM asking, "What's in your toolbox?"

Once the LLM knows what tools are available, it can decide which one to use based on the user's request. For example, if you ask it to "create a new GitHub repository," the LLM will see the `create_github_repo` tool in the list of capabilities and know that's the one to use.

## MCP Sampling: A Deeper Dive into Human-in-the-Loop AI

Now, let's look at one of the most powerful features of MCP: **Sampling**. In the context of MCP, "sampling" isn't about statistics. Instead, it refers to the server requesting an LLM completion *from the client*. This might seem backward, but it enables a powerful "human-in-the-loop" workflow.

Here’s how it works:

1.  **The Server Requests a Completion:** The server sends a `sampling/createMessage` request to the client. This request contains the prompt and other information for the LLM.
2.  **The Client Intervenes:** The client receives this request and can show it to a human user for approval or modification.
3.  **The LLM Generates a Response:** Once approved, the client sends the prompt to the LLM.
4.  **The Client Reviews the Response:** The LLM's response is sent back to the client, where the human user can again review, edit, or approve it.
5.  **The Final Response is Sent:** The approved response is then sent back to the server.

This process creates a robust system of checks and balances, ensuring that a human is always in control of the AI's actions.

## A Practical Example: Python and JSON-RPC

Let's make this more concrete with a simple example of MCP Sampling.

### The `sampling/createMessage` Request

Imagine a server wants to use an LLM to answer a question. It would send a `sampling/createMessage` request to the client like this:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "What is the capital of France?"
        }
      }
    ],
    "modelPreferences": {
      "hints": [
        {"name": "claude-3-sonnet"}
      ]
    }
  }
}
```

The client would then show this to the user. If the user approves it, the client sends it to the LLM.

### The Response

The LLM would generate a response, and the client would receive it, like this:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "role": "assistant",
    "content": {
      "type": "text",
      "text": "The capital of France is Paris."
    },
    "model": "claude-3-sonnet-20240307",
    "stopReason": "endTurn"
  }
}
```

The user can then approve this response, and it will be sent back to the server.

## Conclusion

The Model Context Protocol, with its powerful tooling and sampling features, is transforming how we build with AI. By creating a standardized way for LLMs to interact with the outside world and enabling robust human-in-the-loop workflows, MCP is paving the way for more powerful, flexible, and interconnected AI systems. It’s a simple idea with profound implications, and it’s just the beginning of what’s possible when we give AI the right tools for the job.

Happy coding!
