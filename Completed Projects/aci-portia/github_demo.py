import os
from dotenv import load_dotenv
from portia import Portia, PlanRunState # Import PlanRunState
from config import config,tool_registry

load_dotenv()

portia = Portia(config=config,tools=tool_registry)

GITHUB_REPO = "PortiaAI/portia-sdk-python"  # Example: "your-username/your-repo"
SLACK_CHANNEL = "#general"                  # Example: "#your-slack-channel" or a user ID
ISSUE_LABEL = "bug"                         # Example: "bug", "enhancement", or an empty string for all issues

# This prompt focuses on GitHub actions first, then Slack.
# You can simplify this prompt to ONLY do GitHub actions if you prefer,
# for example, by removing the Slack parts.
prompt = f"""
Check the GitHub repository '{GITHUB_REPO}' for any open issues with the label '{ISSUE_LABEL}'.
If issues are found, create a concise summary of these issues including their titles and URLs.
Then, post this summary to the Slack channel '{SLACK_CHANNEL}'.
If no issues with that label are found, state that: 'No new issues labeled "{ISSUE_LABEL}" found in {GITHUB_REPO}.' in the Slack channel '{SLACK_CHANNEL}'.
"""

print(f"Using prompt: {prompt}\n")

plan = portia.plan(prompt)
print("--- Generated Plan ---")
# Printing the plan.model_dump_json helps you see which tools Portia intends to use,
# including the specific ACI GitHub tools.
print(plan.model_dump_json(indent=2))
print("----------------------\n")

print("Running plan...")
run = portia.run_plan(plan)

# Basic clarification handling loop (optional, but good practice for more complex flows)
while run.state == PlanRunState.NEED_CLARIFICATION:
    print("--- Plan Needs Clarification ---")

    if run.get_outstanding_clarifications():
        clarification = run.get_outstanding_clarifications()[0]
        print(f"Guidance: {clarification.user_guidance}")
        if hasattr(clarification, 'action_url') and clarification.action_url:
            print(f"Action URL (if any): {clarification.action_url}")
    else:
        print("No specific clarification details found, but state is NEED_CLARIFICATION.")
    
    print("Stopping due to unhandled clarification for this demo.")
    print("Check Portia dashboard or logs for details on the clarification needed.")
    break # Exit loop for simplicity in this demo.

print("----------------------\n")
print(f"Final Plan Run State: {run.state}")

if run.outputs and run.outputs.final_output:
    print(f"Final Output Value: {run.outputs.final_output.value}")
elif run.state == PlanRunState.COMPLETE:
    print("Plan completed. The final output might be structured within step outputs or not have a single value.")
    print("Check the Portia dashboard or logs for detailed step outputs.")
else:
    print("Plan did not complete successfully or produce a standard final output.")
    print("Review logs or the Portia dashboard for more details, especially if clarifications were indicated.")
print("----------------------")