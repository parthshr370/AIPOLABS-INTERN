import os
from dotenv import load_dotenv
from portia import (
    Portia,
    PlanRunState,
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification
)
# Assuming config.py is in the same directory (aci-portia)
from config import config, tool_registry

# Load environment variables from .env file in the current directory
load_dotenv()

def run_simple_portia_cli():
    try:
        portia_instance = Portia(config=config, tools=tool_registry)
        print("Portia initialized successfully! CLI is ready.")
    except Exception as e:
        print(f"Error initializing Portia: {e}")
        return

    while True:
        print("\n------------------------------------------")
        user_query = input("Enter your query for Portia (or type 'quit' to exit): \n> ")
        if user_query.lower() == 'quit':
            print("Exiting CLI.")
            break
        if not user_query.strip():
            print("Query cannot be empty.")
            continue

        try:
            print("\nGenerating plan...")
            plan = portia_instance.plan(user_query)
            print("--- Generated Plan ---")
            print(plan.model_dump_json(indent=2))
            print("----------------------")

            print("\nExecuting plan...")
            plan_run = portia_instance.run_plan(plan)

            # Simplified Clarification Handling Loop
            while plan_run.state == PlanRunState.NEED_CLARIFICATION:
                print("\n--- Plan Needs Clarification ---")
                outstanding_clarifications = plan_run.get_outstanding_clarifications()
                if not outstanding_clarifications:
                    print("Warning: Plan state is NEED_CLARIFICATION but no outstanding clarifications found. Resuming.")
                    # This case should ideally not be hit if state is NEED_CLARIFICATION
                    # but as a fallback, we attempt to resume.
                    break # Exit clarification loop and proceed to resume or final state check

                for clarification in outstanding_clarifications:
                    print(f"Guidance: {clarification.user_guidance}")
                    
                    if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                        options_text = ""
                        if isinstance(clarification, MultipleChoiceClarification) and clarification.options:
                            options_text = "\nOptions:\n" + "\n".join([f"  {i+1}. {opt}" for i, opt in enumerate(clarification.options)]) + "\n"
                        
                        user_input_value = input(f"Input for '{clarification.name}':{options_text}\n> ")
                        
                        if isinstance(clarification, MultipleChoiceClarification) and clarification.options:
                            try:
                                choice_idx = int(user_input_value) - 1
                                if 0 <= choice_idx < len(clarification.options):
                                    user_input_value = clarification.options[choice_idx]
                            except ValueError:
                                pass # Use literal input if not a valid number
                        
                        plan_run = portia_instance.resolve_clarification(clarification.id, user_input_value, plan_run)
                        print(f"Response for '{clarification.name}' submitted.")
                    
                    elif isinstance(clarification, ActionClarification):
                        print(f"Action URL: {clarification.action_url}")
                        print("Please complete the action in your browser. Waiting for completion (up to 3 minutes)...")
                        try:
                            plan_run = portia_instance.wait_for_ready(plan_run, timeout_seconds=180)
                        except TimeoutError:
                            print(f"Timed out waiting for action on {clarification.id}.")
                        # After wait_for_ready, the loop will re-evaluate outstanding clarifications.
                    else:
                        print(f"Skipping unhandled clarification type: {type(clarification)}")
                
                # After iterating through all current clarifications and attempting to resolve them,
                # if the state is still NEED_CLARIFICATION, we resume. 
                # The loop will then re-check the state.
                if plan_run.state == PlanRunState.NEED_CLARIFICATION:
                    print("Attempting to resume plan run...")
                    plan_run = portia_instance.resume(plan_run)
                    if plan_run.state == PlanRunState.NEED_CLARIFICATION:
                        print("Plan still needs clarification after resume attempt. Manual action or different input may be required.")
                        # If only ActionClarifications that timed out or weren't completed remain, the loop might continue.
                        # User would need to complete them externally.

            # After the while loop (i.e., state is no longer NEED_CLARIFICATION or loop was broken)
            print("\n--- Final Plan Run Details ---")
            print(f"State: {plan_run.state}")

            if plan_run.outputs and plan_run.outputs.final_output:
                print(f"Final Output Value: {plan_run.outputs.final_output.value}")
            elif plan_run.state == PlanRunState.COMPLETE:
                print("Plan completed successfully.")
            else:
                print(f"Plan run ended with state: {plan_run.state}. No specific final_output in run.outputs or not completed.")
            
            if plan_run.steps:
                print("--- Step Breakdown ---")
                for i, step_run in enumerate(plan_run.steps):
                    # Guarding attribute access for robustness
                    task_name = getattr(step_run, 'task_name', 'N/A')
                    tool_name = getattr(step_run, 'tool_name', 'N/A')
                    step_state = getattr(step_run, 'state', 'N/A')
                    output_value = getattr(step_run, 'output_value', None)
                    error_value = getattr(step_run, 'error', None)

                    print(f"  Step {i+1}: {task_name}")
                    print(f"    Tool: {tool_name}")
                    print(f"    State: {step_state}")
                    if output_value is not None:
                        print(f"    Output: {output_value}")
                    elif error_value:
                        print(f"    Error: {error_value}")
            print("----------------------")

        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_simple_portia_cli() 