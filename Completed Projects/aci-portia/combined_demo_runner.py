import os
from dotenv import load_dotenv
from portia import (
    Portia, 
    PlanRunState, 
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification
)
from config import config, tool_registry

load_dotenv()

# Initialize Portia once
try:
    portia = Portia(config=config, tools=tool_registry)
    print("Portia initialized successfully!")
except Exception as e:
    print(f"Error initializing Portia: {e}")
    exit()

def run_web_search_demo():
    print("\n--- Running Web Search Demo ---")
    search_query = input("Enter your web search query (e.g., best indian restaurant in NYC): ")
    if not search_query.strip():
        print("Search query cannot be empty.")
        return

    print(f"Using prompt: {search_query}\n")
    try:
        plan = portia.plan(search_query)
        print("--- Generated Plan ---")
        print(plan.model_dump_json(indent=2))
        print("----------------------\n")

        print("Running plan...")
        run = portia.run_plan(plan)
        
        if run.state == PlanRunState.NEED_CLARIFICATION:
            print("--- Web Search Demo Needs Clarification ---")
            print("This demo has basic clarification display. For full interactive handling, use option 3.")
            if run.get_outstanding_clarifications():
                clarification = run.get_outstanding_clarifications()[0]
                print(f"Guidance: {clarification.user_guidance}")
                if hasattr(clarification, 'action_url') and clarification.action_url:
                    print(f"Action URL: {clarification.action_url}")
            # For this simplified demo, we won't loop/resolve here.

        print("----------------------\n")
        print(f"Final Plan Run State: {run.state}")
        if run.outputs and run.outputs.final_output:
            print(f"Final Output Value: {run.outputs.final_output.value}")
        elif run.state == PlanRunState.COMPLETE:
            print("Plan completed. Output might be structured differently. Check Portia dashboard.")
        else:
            print(f"Plan did not complete successfully. Final state: {run.state}. Check logs or Portia dashboard.")
        print("----------------------")

    except Exception as e:
        print(f"An error occurred during the web search demo: {e}")

def run_github_issue_demo():
    print("\n--- Running GitHub Issue Digest Demo ---")
    
    default_repo = "PortiaAI/portia-sdk-python"
    default_label = "bug"
    default_slack_channel = "#general" # Can be an empty string if not used

    github_repo = input(f"Enter GitHub Repository (owner/repo) [default: {default_repo}]: ") or default_repo
    issue_label = input(f"Enter Issue Label to search for [default: {default_label}]: ") or default_label
    slack_channel = input(f"Enter Slack Channel (optional, e.g., #general or user ID) [default: {default_slack_channel}]: ") or default_slack_channel

    if not github_repo.strip(): # Issue label can be empty if desired for all issues
        print("GitHub Repository cannot be empty.")
        return

    prompt_parts = [
        f"Check the GitHub repository '{github_repo}' for any open issues with the label '{issue_label}'.",
        "If issues are found, create a concise summary of these issues including their titles and URLs."
    ]
    if slack_channel.strip():
        prompt_parts.append(f"Then, post this summary to the Slack channel '{slack_channel}'.")
        prompt_parts.append(f"If no issues with that label are found, state that: 'No new issues labeled \"{issue_label}\" found in {github_repo}.' in the Slack channel '{slack_channel}'.")
    else:
        prompt_parts.append("If no issues with that label are found, state that no new issues were found.")
    
    prompt = "\n".join(prompt_parts)
    print(f"Using prompt: {prompt}\n")

    try:
        plan = portia.plan(prompt)
        print("--- Generated Plan ---")
        print(plan.model_dump_json(indent=2))
        print("----------------------\n")

        print("Running plan...")
        run = portia.run_plan(plan)

        if run.state == PlanRunState.NEED_CLARIFICATION:
            print("--- GitHub Issue Demo Needs Clarification ---")
            print("This demo has basic clarification display. For full interactive handling, use option 3.")
            if run.get_outstanding_clarifications():
                clarification = run.get_outstanding_clarifications()[0]
                print(f"Guidance: {clarification.user_guidance}")
                if hasattr(clarification, 'action_url') and clarification.action_url:
                    print(f"Action URL: {clarification.action_url}")
            # For this simplified demo, we won't loop/resolve here.

        print("----------------------\n")
        print(f"Final Plan Run State: {run.state}")

        if run.outputs and run.outputs.final_output:
            print(f"Final Output Value: {run.outputs.final_output.value}")
        elif run.state == PlanRunState.COMPLETE:
            print("Plan completed. Output might be structured differently. Check Portia dashboard.")
        else:
            print(f"Plan did not complete successfully. Final state: {run.state}. Check logs or Portia dashboard.")
        print("----------------------")

    except Exception as e:
        print(f"An error occurred during the GitHub issue demo: {e}")

def run_generic_portia_demo():
    print("\n--- Running Generic Portia Demo with Clarification Handling ---")
    user_prompt = input("Enter the prompt for Portia: ")
    if not user_prompt.strip():
        print("Prompt cannot be empty.")
        return

    print(f"Using prompt: {user_prompt}\n")
    try:
        plan = portia.plan(user_prompt)
        print("--- Generated Plan ---")
        print(plan.model_dump_json(indent=2))
        print("----------------------\n")

        print("Running plan...")
        run = portia.run_plan(plan)

        while run.state == PlanRunState.NEED_CLARIFICATION:
            print("--- Plan Needs Clarification ---")
            clarifications_resolved_in_loop = False # Flag to see if we made progress in this iteration
            
            outstanding_clarifications = run.get_outstanding_clarifications()
            if not outstanding_clarifications:
                print("State is NEED_CLARIFICATION but no outstanding clarifications found. Waiting for potential external updates or breaking.")
                break

            for clarification in outstanding_clarifications:
                print(f"User Guidance: {clarification.user_guidance}")
                
                if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                    options_text = ""
                    if isinstance(clarification, MultipleChoiceClarification) and clarification.options:
                        options_text = "\nAvailable options:\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(clarification.options)]) + "\n"
                    
                    user_input_value = input(f"Please provide input:{options_text}\n> ")
                    
                    if isinstance(clarification, MultipleChoiceClarification) and clarification.options:
                        try:
                            choice_idx = int(user_input_value) - 1
                            if 0 <= choice_idx < len(clarification.options):
                                user_input_value = clarification.options[choice_idx]
                            else:
                                print("Invalid choice number. Please enter the exact text or a valid number.")
                                continue 
                        except ValueError:
                            pass
                    
                    run = portia.resolve_clarification(clarification, user_input_value, run)
                    print(f"Clarification resolved with input: '{user_input_value}'")
                    clarifications_resolved_in_loop = True

                elif isinstance(clarification, ActionClarification):
                    print(f"Action Required: {clarification.user_guidance}")
                    print(f"Please visit this URL to complete the action: {clarification.action_url}")
                    print("After completing the action in your browser, Portia will attempt to resume.")
                    print("Waiting for action to be completed (up to 3 minutes)...")
                    try:
                        run = portia.wait_for_ready(run, timeout_seconds=180)
                        if run.state != PlanRunState.NEED_CLARIFICATION: 
                             print("Action completed and clarification resolved.")
                             clarifications_resolved_in_loop = True
                        else: 
                             print("Action completed. Checking for further clarifications.")
                    except TimeoutError:
                        print("Timed out waiting for action completion. The plan run may still be paused.")
                        print("You might need to re-run the demo or check the Portia dashboard.")
                        return 
                    except Exception as e:
                        print(f"An error occurred while waiting for action completion: {e}")
                        return 
                else:
                    print(f"Unhandled clarification type: {type(clarification)}. Skipping.")
            
            if run.state == PlanRunState.NEED_CLARIFICATION and clarifications_resolved_in_loop:
                print("Some clarifications resolved, attempting to resume for any further steps or new clarifications...")
                run = portia.resume(run)
            elif not clarifications_resolved_in_loop and run.state == PlanRunState.NEED_CLARIFICATION:
                print("No clarifications were resolved in this pass. User action likely required externally (e.g. OAuth). Waiting before next check.")
                break 
        
        print("----------------------\n")
        print(f"Final Plan Run State: {run.state}")

        if run.outputs and run.outputs.final_output:
            print(f"Final Output Value: {run.outputs.final_output.value}")
        elif run.state == PlanRunState.COMPLETE:
            print("Plan completed successfully.")
        else:
            print(f"Plan did not complete successfully. Final state: {run.state}.")
            print("Check logs or Portia dashboard for more details (e.g., errors, pending clarifications).")
        print("----------------------")

    except Exception as e:
        print(f"An error occurred during the generic Portia demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    while True:
        print("\nSelect a demo to run:")
        print("1: Web Search Demo")
        print("2: GitHub Issue Digest Demo")
        print("3: Generic Portia Demo (with full clarification handling)")
        print("q: Quit")
        
        choice = input("Enter your choice (1, 2, 3, or q): ")
        
        if choice == '1':
            run_web_search_demo()
        elif choice == '2':
            run_github_issue_demo()
        elif choice == '3':
            run_generic_portia_demo()
        elif choice.lower() == 'q':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.") 