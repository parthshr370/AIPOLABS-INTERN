# **Context Engineering: Building Better AI Worlds Beyond Prompts**

In the early days of LLM, working with it felt like a new way to communicate with a being with no idea of how to. Making the most out of the token spitting machine was to prompt it the right way.

This led to everyone being the **prompt engineer** of their own league, squeezing the most out of LLMs in the most effective way possible, but soon everyone realised that we were hitting a wall.

A perfect prompt is like a well rehearsed dialogue, great for *one-shot* output but fails as the context grows. Things start to become foggy, outputs start to become dim. The once LLM that always had the potential suddenly shifts to become a convoluted mess.

This makes us realise that maybe *one-shot* outputs and prompting was not the way, maybe talking to AI wasnt enough and what we needed was a **system** an environment to build effective AI systems.

That's where **context engineering** comes in to pump up the capabilities and make things shine.

## How **Context** Pumps and Shines

At its heart **context engineering** is basically creating an *information ecosystem*, an AI/LLM that operates within.

Maybe think of it as this way, Basic prompting is like a chef with access to just the knife, surely can cut a lot of stuff but not complete enough to do long complex tasks.

And **context engineer** is like giving that chef a whole kitchen with every utensil, tool and ingredient spawning out when needed.

Its basically is juggling and managing the information, the tools and the *memory* that AI can access at any given moment. This is critical when you realise all LLMs are bound to their fixed **context windows**, which in turn rots away if not caught up with all the time.

**Context engineering** is the art of giving the model exactly what it needs, when it needs it, in the format it understands best.

There even might be cases where **context engineering** is used by you without knowing anything about it.

But rules alone aren't enough—let's talk about keeping things current with dynamic information.

### How **Context Engineering** Even Works 

It has some basic pillars, you cant just stuff a prompt inside an LLM and call it a day, its not just text its more of an *architectural challenge*. You need to create a system of prompts and information and tools in such a way that when the Agent comes inside it works with all that in a synergy picking the right context and triggering the right tools.

### The **Foundational Rules**

This acts like the central **rulebook**, in context engineering, set of foundational instructions and checklists that define the agents core purpose, its structure, its personality and rules of engagement.

Like a central hub to coordinate all other tools at our disposal. This offloads the clutter from the models context window and creates a systematic way to keep track of things.

One example for this can be how `Claude.md` is used by Claude code to create a central file of checklists and repetitive tasks that is first loaded into the context window before even anything is started, it provides and pumps just the right info into the LLM to get a sense of direction and skeleton.

But rules alone aren't enough—let's talk about keeping things current with **dynamic information**.

### **Dynamic Information**

While setting up the right environment is one step in the right direction, we need to realise that LLMs are trained on *static historical data*, leaving them ignorant of the present. Context engineering solves this by giving the AI access to the *real world*.

The most common way to do this is through *RAG*, which allows agent to pull *real-time* info from documents, databases or APIs.

This helps us fetch *real-time* data such as latest stock on financial history of a company. The information is fetched and dynamically injected into the context, grounding the AI's response in current, factual data.

Once again without pulling the main context window.

Now that we've got fresh data flowing, let's equip our agent with the right **tools**.

### **Tools** for the Job

To move from talking to *doing*, an agent needs tools. This could be anything from a simple calculator to a complex `search_flights` function or a code executor.

We provide these tools with better description and metadata that can help the model to trigger them at the right time.

This is where things get messy though, once the agents context is filled with hundreds of tools it gets confused and its performance and speed overall drop. While working with ACI, they solved this with something called **Unified MCP server**—a smart dispatcher that picks the right tool without cluttering the LLM's context. This made the tool calling smarter and long-lasting.

For even more complex tasks, we can break things down with specialized helpers.

### **Subagents**: The Specialized Staff

Instead of asking one agent/LLM to just do one task or bunch of tasks sequentially, subagents divide it into specific tasks, small minions working towards their own small special goals that meet together in the end with a joint output that was needed.

This is necessary because when each subagent has its own separate context window, it performs much better without one influencing another. Agents with one focused environment then allow far more complex and focused environments, this prevents the context pollution and allows for far more complex, multi-step workflows.

Once again we can do a callback on how Claude code uses `Claude.md` as a central way to maintain context across whole environments, this file when working contains context of all the subagents spawned and makes sure they finish their tasks with checkboxes and points to maintain coherence.

Finally, to tie it all together, agents need a way to remember.

### **Memory**: Remembering When the Time Comes

Finally, an effective agent needs to remember. Context engineering provides mechanisms for both *short-term memory* (tracking the current conversation) and *long-term memory* (storing user preferences or past interactions).

One of the most fascinating techniques I've seen is how some agents use their environment as a form of memory. The Manus agent, for example, often creates a `todo.md` file for complex tasks and updates it as it progresses. By constantly rewriting its goals at the end of the context, it keeps the main objective in its "recent attention," preventing it from getting "lost-in-the-middle" of a long task. This is a brilliant, low-tech way to manipulate the model's attention and ensure it stays on track.

### The **Real-World Payoff**: Why This All Matters

While the mechanisms are enough to outdo the goods and bad of our good old prompt engineering, this shift isnt just going to be in your own lab, it has its own engineering benefits. By managing the information flow we see benefits which werent there before.

- **Increased Reliability:** With a clean, relevant context, agents are far less likely to make mistakes or hallucinate. When Claude Code runs a task, it has access to the project's specific error handling patterns and testing requirements, leading to more robust code.
- **Smarter Tool Use:** By providing only the necessary tools—or delegating to subagents—the AI can more accurately select and use the right tool for the job.
- **Greater Efficiency:** A focused context means fewer tokens are needed, which reduces costs and speeds up response times. This is not a small saving; it can cut token consumption dramatically.
- **Learning from Failure:** One of the most effective, if counter-intuitive, lessons is to *keep failures in the context*. When an agent tries something and gets an error, seeing that failed action and the resulting stack trace helps it learn. It implicitly updates its internal model and avoids making the same mistake twice.

### **Conclusion**: Building Better Worlds

The conversation around AI is maturing. Prompt engineering taught us how to speak to these new minds, and it remains a vital skill. But to build the truly intelligent and autonomous systems we envision for the future, we have to think beyond single commands. We have to become architects of their worlds.

By shifting our focus from isolated prompts to expanding our horizon towards environments that are more and more capable, reliable, and more aligned with our goals—that's how we create better agents.