# Build a "Deep Research Agent for Memory"

## 1. Objective

[cite_start]The objective is to design an autonomous research agent that automatically retrieves context and reasons over it to produce a well-structured answer[cite: 3, 7, 10]. [cite_start]The agent is given a `user_id` and a natural-language `prompt`[cite: 4, 5].

The process involves:

- [cite_start]**Retrieving context**: The agent pulls the most relevant memories for the `user_id` from the long-term Memory store (Memo) and fetches past conversation messages that may help answer the prompt[cite: 8, 9].
- [cite_start]**Reasoning over context**: The agent then uses this context to produce a grounded, well-structured answer[cite: 10].

## 2. Functional Requirements

| Area                   | Requirement                                                                                                                                                                                                                                                                                   |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agent Entry-Point      | [cite_start]A single function or CLI command that accepts a `user_id` and a `prompt`[cite: 12].                                                                                                                                                                                               |
| Context Retrieval      | [cite_start]The agent must efficiently identify and rank relevant memories and message snippets using methods like vector similarity, keyword heuristics, or a combination of both[cite: 12].                                                                                                 |
| Answer Generation      | [cite_start]The final answer must be factually aligned with the retrieved context and include inline citations or footnotes pointing to memory IDs or message timestamps[cite: 12]. [cite_start]It should also provide a brief, high-level rationale or a chain-of-thought summary[cite: 12]. |
| Memory Writing (bonus) | [cite_start]If new durable facts emerge, they should be appended to the Memory store in the correct schema[cite: 12].                                                                                                                                                                         |
| Model Choice           | [cite_start]Any LLM is permitted, but the selection must be briefly justified in the `README` file[cite: 12].                                                                                                                                                                                 |
| Local Demo             | [cite_start]An interactive way to run the agent with sample data should be provided (either a CLI or a simple web UI)[cite: 15].                                                                                                                                                              |

## 3. Deliverables

1.  [cite_start]**GitHub Repository** [cite: 17]
    - [cite_start]Clean, well-commented code[cite: 18].
    - [cite_start]A `README.md` file with setup and usage instructions that take less than 5 minutes to follow[cite: 19].
    - [cite_start]Unit and integration tests that cover both retrieval and generation[cite: 20].
2.  [cite_start]**Video Walk-through (5-10 min)** [cite: 21]
    - [cite_start]The video should demonstrate the installation process, provide example queries, and show how the answers cite memories and messages[cite: 22, 23].
3.  [cite_start]**Technical Write-up (Optional)** [cite: 24]
    - [cite_start]This can cover trade-offs, future improvements, and what would be tackled with more time[cite: 25].

## 4. Timeline

[cite_start]The timeline for this project is 3 calendar days from the moment the document is received[cite: 27]. [cite_start]Start and due dates should be stated in the pull request (PR) or email[cite: 28].

## 5. Evaluation Rubric

| Weight | Criterion                                                                                                                                                   |
| :----- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 40%    | [cite_start]**Accuracy & grounding**: Answers must correctly use relevant memories/messages and avoid "hallucinations" (fabricating information)[cite: 30]. |
| 25%    | [cite_start]**Retrieval quality**: The approach should reliably surface the correct context, even as data scales[cite: 30].                                 |
| 15%    | [cite_start]**Code quality**: This includes readability, modularity, tests, and performance[cite: 30].                                                      |
| 10%    | [cite_start]**Developer experience**: The setup should be smooth, documentation clear, and the project easy to extend[cite: 30].                            |
| 10%    | [cite_start]**Communication**: This is based on video clarity, explanation of decisions, and professionalism[cite: 30].                                     |

[cite_start]Bonus points will be awarded for robust memory-writing and thoughtful user experience (UX) touches[cite: 33].

## 6. Submission

- [cite_start]Push the code to a public or private GitHub repository[cite: 35]. [cite_start]If the repository is private, invite `@deshraj`[cite: 35].
- [cite_start]Include the demo-video link in the `README` file[cite: 36].
