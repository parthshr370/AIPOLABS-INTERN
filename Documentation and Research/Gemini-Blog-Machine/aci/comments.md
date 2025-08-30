The overall blog is getting close, but it’s still not quite there. Biggest issues right now:

- This paints tool-use and ACI.dev as too big a part of context engineering, it plays one part of it but it’s not the majority of context engineering. Users who are deep in the ecosystem will be put off by the inaccuracy.
- The blog dives into details about the SDK part but omits MCPs which is also an important part of the discussion.

Rather than this, something more like “ACI.dev Manages Tool-use in Agent Context Engineering”

It basically cannot just throw the reader into without knowing what context engineering is

Atm its like a shameless self promotion because it emphasises too much on the tool calling side of context engienering

we also need to bring in that ACI.dev also does MCP which is an integralpart of our offering

I don’t believe “infra required to let them act” is the accepted definition of context engineering at all. Context engineering pertains to filling up the context window with the correct data and information for the LLM to act. Part of that context includes tool definitions which is where ACI.dev can help

We would have to reframe the rest of this section and article specifically around how tool-use complicates context engineering i.e. tool-overload eats up contextual budget for other things, context rot if you add long tool descriptions that involve boilerplate information, tool-use support information e.g. if how to do auth etc needs to be crammed into the context window

These are all the things that ACI.dev can then support and reduce the contextual burden within the LLM context window

We should introduce early on that we provide both a unified MCP server and SDK. I’m worried it would be confusing for readers because you mention the Unified MCP here but later on for seeing ACI.dev in action you only illustrate it with the SDK
