import os 
from dotenv import load_dotenv
from portia import (
    Portia,
    PlanRunState,
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification
)
from config import config,tool_registry

load_dotenv()

portia_instance = Portia(config=config,tools=tool_registry) # Renamed for clarity

# Original prompt
prompt = (
    "What's the weather like in Springfield?"  # Changed to a more ambiguous query
)

print(f"Using prompt: {prompt}\n")

try:
    print("\nGenerating plan...")
    plan = portia_instance.plan(prompt)
    print("--- Generated Plan ---")
    print(plan.model_dump_json(indent=2))
    print("----------------------")

    print("\nExecuting plan...")
    plan_run = portia_instance.run_plan(plan)

    # Clarification Handling Loop (adapted from simple_portia_cli.py)
    while plan_run.state == PlanRunState.NEED_CLARIFICATION:
        print("\n--- Clarification Needed ---") # Simplified
        outstanding_clarifications = plan_run.get_outstanding_clarifications()
        if not outstanding_clarifications:
            print("Warning: Plan state is NEED_CLARIFICATION but no outstanding clarifications found. Resuming.")
            break

        for clarification in outstanding_clarifications:
            print(f"Query: {clarification.user_guidance}") # Simplified
            
            if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                options_text = ""
                if isinstance(clarification, MultipleChoiceClarification) and clarification.options:
                    options_text = "\nOptions:\n" + "\n".join([f"  {i+1}. {opt}" for i, opt in enumerate(clarification.options)]) + "\n"
                
                user_input_value = input(f"Your answer for '{clarification.name}':{options_text}\n> ") # Simplified prompt
                
                if isinstance(clarification, MultipleChoiceClarification) and clarification.options:
                    try:
                        choice_idx = int(user_input_value) - 1
                        if 0 <= choice_idx < len(clarification.options):
                            user_input_value = clarification.options[choice_idx]
                    except ValueError:
                        pass # Use literal input if not a valid number
                
                plan_run = portia_instance.resolve_clarification(clarification.id, user_input_value, plan_run)
                print(f"Clarification for '{clarification.name}' submitted.") # Simplified
            
            elif isinstance(clarification, ActionClarification):
                print(f"Action URL: {clarification.action_url}")
                print("Please complete the action in your browser. Waiting for completion (up to 3 minutes)...")
                try:
                    plan_run = portia_instance.wait_for_ready(plan_run, timeout_seconds=180)
                except TimeoutError:
                    print(f"Timed out waiting for action on {clarification.id}.")
            else:
                print(f"Skipping unhandled clarification type: {type(clarification)}")
        
        if plan_run.state == PlanRunState.NEED_CLARIFICATION:
            print("Attempting to resume plan run after clarifications...") # Simplified
            plan_run = portia_instance.resume(plan_run)
            if plan_run.state == PlanRunState.NEED_CLARIFICATION:
                print("Plan still needs further clarification.") # Simplified

    print("\n--- Final Plan Run Details ---")
    print(f"Run status (State): {plan_run.state}")

    if plan_run.outputs and plan_run.outputs.final_output:
        print(f"Final Output Value: {plan_run.outputs.final_output.value}")
    elif plan_run.state == PlanRunState.COMPLETE:
        print("Plan completed successfully.")
    else:
        print(f"Plan run ended with state: {plan_run.state}. No specific final_output or not completed.")

except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()