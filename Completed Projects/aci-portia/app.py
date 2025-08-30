import streamlit as st
import os
from dotenv import load_dotenv
from portia import (
    Portia,
    PlanRunState,
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification,
)
# config and tool_registry will be imported after loading .env
import json
import traceback

# --- Constants ---
# Updated SAMPLE_PROMPTS with new templates referencing specific tool function names
SAMPLE_PROMPTS = {
    "Weather": {
        "display_name": "🌦️ Weather (OpenWeatherMap)",
        "prompt_template": "Using the MCP's OPEN_WEATHER_MAP_CURRENT_WEATHER tool, get the current weather in {weather_location}.",
        "fields": [
            {"label": "Location (e.g., Springfield):", "key": "weather_location", "default": "Springfield"}
        ],
        "category": "ACI Tools"
    },
    "GmailDraft": {
        "display_name": "📧 Gmail: Draft Email",
        "prompt_template": "With the MCP's GMAIL_DRAFTS_CREATE and GMAIL_SEND_EMAIL tools, draft and send an email to '{gmail_to_email}' with subject '{gmail_subject}' and body:\n\n{gmail_body}",
        "fields": [
            {"label": "To Email:", "key": "gmail_to_email", "default": "team@example.com"},
            {"label": "Subject:", "key": "gmail_subject", "default": "ACI Demo Follow-up"},
            {"label": "Body:", "key": "gmail_body", "default": "Hi team, this is a test from the Portia ACI demo app."}
        ],
        "category": "ACI Tools"
    },
    "SlackMessage": {
        "display_name": "💬 Slack: Send Channel Message",
        "prompt_template": "Use the MCP's SLACK_CHAT_POST_MESSAGE tool to send to {slack_channel} the message:\n\n\"{slack_message}\"",
        "fields": [
            {"label": "Slack Channel (e.g., #general):", "key": "slack_channel", "default": "#general"},
            {"label": "Message:", "key": "slack_message", "default": "Hello ACI users! Portia is live."}
        ],
        "category": "ACI Tools"
    },
    "GitHubSearchRepos": {
        "display_name": "🛠️ GitHub: Search Repositories",
        "prompt_template": "With the MCP's GITHUB_SEARCH_REPOSITORIES tool, find repositories matching '{github_search_query}'.",
        "fields": [
            {"label": "Search Query:", "key": "github_search_query", "default": "streamlit examples"}
        ],
        "category": "ACI Tools"
    },
    "ACISearch": {
        "display_name": "🔍 ACI Search (Brave)",
        "prompt_template": "Invoke the MCP's BRAVE_SEARCH_WEB_SEARCH tool to look up: \"{aci_search_topic}\" and return the top results.",
        "fields": [
            {"label": "Search Topic:", "key": "aci_search_topic", "default": "recent reviews of the new AI models"}
        ],
        "category": "ACI Tools"
    },
    "SummarizeDocs": {
        "display_name": "📄 Summarize Webpage",
        "prompt_template": "Fetch the content at {summarize_url} (using Portia's default fetcher) and summarize the key points.",
        "fields": [
            {"label": "URL to Summarize:", "key": "summarize_url", "default": "https://docs.portialabs.ai/"}
        ],
        "category": "General"
    },
    "GitHubIssueDigest": {
        "display_name": "📝 GitHub Issue Digest to Slack",
        "prompt_template": "1) Use the MCP's GITHUB_LIST_ISSUES tool on '{digest_github_repo}' filtering by label '{digest_issue_label}'.\n2) If there are matches, build a summary of titles + URLs.\n3) Post that summary to Slack channel '{digest_slack_channel}' via the MCP's SLACK_CHAT_POST_MESSAGE tool.\n4) If none found, send: \"No new issues labeled '{digest_issue_label}' in {digest_github_repo}.\"",
        "fields": [
            {"label": "GitHub Repository (owner/repo):", "key": "digest_github_repo", "default": "PortiaAI/portia-sdk-python"},
            {"label": "Issue Label:", "key": "digest_issue_label", "default": "bug"},
            {"label": "Slack Channel for Digest:", "key": "digest_slack_channel", "default": "#general"}
        ],
        "category": "Multi-Tool Examples"
    },
    "BraveSearchToSlack": {
        "display_name": "🔎📝 Brave Search & Post to Slack",
        "prompt_template": "1) Use the MCP's BRAVE_SEARCH_WEB_SEARCH tool to find information about: \"{search_query_for_slack}\". Ensure the search is performed with safesearch set to 'moderate'.\n2) Take the top search results (e.g., a summary or list of titles/URLs).\n3) Post this summary to the Slack channel '{slack_channel_for_search_results}' using the MCP's SLACK_CHAT_POST_MESSAGE tool.",
        "fields": [
            {"label": "Search Query for Brave:", "key": "search_query_for_slack", "default": "latest AI advancements"},
            {"label": "Slack Channel for Results:", "key": "slack_channel_for_search_results", "default": "#general"}
        ],
        "category": "Multi-Tool Examples"
    }
}

ACI_PORTIA_DIR = os.path.dirname(__file__)
ENV_PATH = os.path.join(ACI_PORTIA_DIR, '.env')

# --- Portia Initialization ---
@st.cache_resource # Cache Portia instance
def init_portia_and_load_config():
    # Load .env from the same directory as app.py
    # This is crucial because config.py might try to read env vars at import time for MCP
    load_dotenv(dotenv_path=ENV_PATH)
    
    # Now that .env is loaded, importing config and tool_registry should work as expected
    from config import config as portia_config, tool_registry as portia_tool_registry

    portia_instance = Portia(config=portia_config, tools=portia_tool_registry)
    # available_tools will be populated after the first plan generation
    return portia_instance, [] # Return Portia instance and an empty list for tools initially

# --- Session State Management ---
def ensure_session_state():
    if "portia_instance" not in st.session_state or "available_tools" not in st.session_state:
        st.session_state.portia_instance, st.session_state.available_tools = init_portia_and_load_config()

    # UI and flow states
    if "prompt" not in st.session_state:
        st.session_state.prompt = ""
    if "plan_generated" not in st.session_state:
        st.session_state.plan_generated = False
    if "plan_obj" not in st.session_state:
        st.session_state.plan_obj = None
    if "plan_run_obj" not in st.session_state:
        st.session_state.plan_run_obj = None
    if "tool_ids_in_plan_steps" not in st.session_state:
        st.session_state.tool_ids_in_plan_steps = []
    if "output_display" not in st.session_state:
        st.session_state.output_display = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None
    if "info_message" not in st.session_state: 
        st.session_state.info_message = None
    if "execution_started" not in st.session_state:
        st.session_state.execution_started = False

    # States for clarification handling
    if "clarifications_to_resolve" not in st.session_state: # List of Clarification objects
        st.session_state.clarifications_to_resolve = []
    if "clarification_answers" not in st.session_state: # Store {clar_id: answer}
        st.session_state.clarification_answers = {}

    # Initialize session state for structured prompt fields
    for key, prompt_config in SAMPLE_PROMPTS.items():
        for field in prompt_config.get("fields", []):
            if field["key"] not in st.session_state:
                st.session_state[field["key"]] = field["default"]
    
    # Remove old structured prompt builder session states if they exist to avoid conflicts
    # (These were github_repo_input, issue_label_input, slack_channel_input)
    old_keys = ["github_repo_input", "issue_label_input", "slack_channel_input"]
    for old_key in old_keys:
        if old_key in st.session_state:
            del st.session_state[old_key]

# --- Helper Functions ---
def reset_flow_state(clear_prompt=False):
    if clear_prompt:
        st.session_state.prompt = ""
        if "prompt_input_key" in st.session_state:
             st.session_state.prompt_input_key = ""

    st.session_state.plan_generated = False
    st.session_state.plan_obj = None
    st.session_state.plan_run_obj = None
    st.session_state.tool_ids_in_plan_steps = []
    st.session_state.output_display = None
    st.session_state.clarifications_to_resolve = []
    st.session_state.clarification_answers = {}
    st.session_state.execution_started = False


# --- Main Application ---
st.set_page_config(page_title="Portia ACI Demo", layout="wide", initial_sidebar_state="expanded")
ensure_session_state()

st.title("🧪 Portia + ACI Interactive Demo")

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 Portia Control Panel")
    st.markdown("---") 
    st.subheader("📝 Structured Prompts")

    # Group prompts by category
    categories = {}
    for prompt_key, prompt_config in SAMPLE_PROMPTS.items():
        category = prompt_config.get("category", "General")
        if category not in categories:
            categories[category] = []
        categories[category].append((prompt_key, prompt_config))

    for category_name, prompts_in_category in sorted(categories.items()):
        with st.expander(f"**{category_name}**", expanded=category_name == "ACI Tools"):
            for prompt_key, prompt_config in prompts_in_category:
                with st.container(border=True):
                    st.markdown(f"**{prompt_config['display_name']}**")
                    field_values = {}
                    for field in prompt_config.get("fields", []):
                        # Use a unique key for the widget by combining prompt_key and field key
                        widget_key = f"{prompt_key}_{field['key']}"
                        st.session_state[field["key"]] = st.text_input(
                            field["label"],
                            value=st.session_state[field["key"]],
                            key=widget_key # widget_key ensures Streamlit tracks this input uniquely
                        )
                        field_values[field["key"]] = st.session_state[field["key"]]
                    
                    button_gen_key = f"generate_btn_{prompt_key}"
                    if st.button(f"Generate & Use {prompt_config['display_name']} Prompt", key=button_gen_key, use_container_width=True, type="secondary"):
                        # Construct the prompt using the template and current field values
                        # Ensure all necessary keys are present in field_values for formatting
                        template_params = {f_key: field_values.get(f_key, "") for f_key in [f["key"] for f in prompt_config.get("fields", [])]}
                        
                        try:
                            # The prompt_template should be a valid Python string with placeholders.
                            # .format() will handle these placeholders.
                            # Escaped characters like \n or \" in the template string itself are fine.
                            generated_prompt = prompt_config["prompt_template"].format(**template_params)
                        except KeyError as e:
                            st.error(f"Missing field for prompt template: {e}. Check prompt_template and field definitions.")
                            generated_prompt = "Error generating prompt (KeyError). Check console and template definitions."
                        except Exception as e:
                            st.error(f"Error formatting prompt: {e}")
                            generated_prompt = f"Error generating prompt ({type(e).__name__}). Check console and template definitions."

                        st.session_state.prompt = generated_prompt
                        st.session_state.prompt_input_key = generated_prompt
                        reset_flow_state(clear_prompt=False)
                        st.session_state.info_message = f"{prompt_config['display_name']} prompt generated. Review and click 'Generate Plan'."
                        st.session_state.error_message = None
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True) # Bit of spacing

    st.markdown("---")
    st.subheader("🛠️ Available Tools")
    with st.expander("Show tools considered by Portia", expanded=False):
        if st.session_state.get("available_tools") and st.session_state.available_tools:
            st.caption(f"{len(st.session_state.available_tools)} tools considered in last successful plan:")
            for tool_id in st.session_state.available_tools:
                st.markdown(f"- `{tool_id}`")
        else:
            st.caption("Generate a plan successfully to see tools Portia considered.")
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    with st.expander("About this App", expanded=True):
        st.info(
            "This app demonstrates Portia with ACI tools. "
            "Enter a prompt, generate a plan, execute, and handle clarifications."
        )
        st.markdown(
            "**Key Libraries:**\n"
            "- [Portia](https://docs.portialabs.ai/)\n"
            "- [ACI.DEV](https://www.aci.dev/docs)\n"
            "- [Streamlit](https://streamlit.io/)"
            )

# Main Area layout
prompt_section = st.container()
plan_section = st.container()
execution_section = st.container()

with prompt_section:
    st.markdown("### 💬 1. Enter Your Prompt")
    try:
        with st.container(border=True):
            st.session_state.prompt = st.text_area("Your query for Portia:", value=st.session_state.prompt, height=100, key="prompt_input_key", label_visibility="collapsed")
            generate_plan_button = st.button("🧠 Generate Plan", type="primary", disabled=not st.session_state.prompt, use_container_width=True)
    except TypeError: 
         st.session_state.prompt = st.text_area("Your query for Portia:", value=st.session_state.prompt, height=100, key="prompt_input_key", label_visibility="collapsed")
         generate_plan_button = st.button("🧠 Generate Plan", type="primary", disabled=not st.session_state.prompt, use_container_width=True)

    if generate_plan_button:
        reset_flow_state(clear_prompt=False)
        st.session_state.info_message = "Generating plan..."
        st.session_state.error_message = None
        try:
            with st.spinner("🤖 Portia is planning your request..."):
                plan = st.session_state.portia_instance.plan(st.session_state.prompt)
            st.session_state.plan_obj = plan
            st.session_state.plan_generated = True
            st.session_state.info_message = "Plan generated successfully! Review below & click 'Execute Plan' when ready."
            st.session_state.tool_ids_in_plan_steps = sorted(list(set(step.tool_id for step in plan.steps if step.tool_id)))
            if hasattr(plan, 'plan_context') and hasattr(plan.plan_context, 'tool_ids') and plan.plan_context.tool_ids:
                st.session_state.available_tools = sorted(list(set(plan.plan_context.tool_ids)))
            else:
                st.session_state.available_tools = []
        except Exception as e:
            st.session_state.error_message = f"Error generating plan: {e}\n{traceback.format_exc()}"
            st.session_state.plan_generated = False
            st.session_state.available_tools = []
        st.rerun()

    if st.session_state.info_message:
        st.info(st.session_state.info_message, icon="ℹ️")
    if st.session_state.error_message:
        st.error(st.session_state.error_message, icon="🚨")

with plan_section:
    if st.session_state.plan_generated and st.session_state.plan_obj:
        st.markdown("### 📜 2. Review Plan")
        try:
            with st.container(border=True):
                plan_display_col1, plan_display_col2 = st.columns(2)
                with plan_display_col1:
                    st.subheader("Plan Steps (JSON)")
                    try:
                        st.json(st.session_state.plan_obj.model_dump(), expanded=True)
                    except Exception as e:
                        st.error(f"Could not display plan JSON: {e}")
                        st.text(str(st.session_state.plan_obj))
                with plan_display_col2:
                    st.subheader("Tools in Plan Steps")
                    if st.session_state.tool_ids_in_plan_steps:
                        for tool_id in st.session_state.tool_ids_in_plan_steps:
                            st.markdown(f"- `{tool_id}`")
                    else:
                        st.markdown("No specific tools identified in the plan steps.")
                    st.markdown("---")
                    st.caption("📝 Clarifications may be requested during execution if Portia needs more input.")

                if st.button("🚀 Execute Plan", type="primary", disabled=st.session_state.execution_started, use_container_width=True):
                    st.session_state.execution_started = True
                    st.session_state.info_message = "Executing plan..."
                    st.session_state.error_message = None
                    st.session_state.output_display = None
                    st.session_state.plan_run_obj = None
                    st.session_state.clarifications_to_resolve = []
                    st.session_state.clarification_answers = {}
                    try:
                        with st.spinner("🛰️ Portia is executing the plan..."):
                            run = st.session_state.portia_instance.run_plan(st.session_state.plan_obj)
                        st.session_state.plan_run_obj = run
                        st.session_state.info_message = "Initial execution step completed. Current state: " + run.state.value
                    except Exception as e:
                        st.session_state.error_message = f"Error starting plan execution: {e}\n{traceback.format_exc()}"
                        st.session_state.execution_started = False
                    st.rerun()
        except TypeError: 
            plan_display_col1, plan_display_col2 = st.columns(2)
            with plan_display_col1:
                st.subheader("Plan Steps (JSON)")
                try: st.json(st.session_state.plan_obj.model_dump(), expanded=True) 
                except: st.text(str(st.session_state.plan_obj))
            with plan_display_col2:
                st.subheader("Tools in Plan Steps")
                if st.session_state.tool_ids_in_plan_steps: 
                    for tool_id in st.session_state.tool_ids_in_plan_steps: st.markdown(f"- `{tool_id}`")
                else: st.markdown("No specific tools identified.")
                st.markdown("---")
                st.caption("📝 Clarifications may be requested.")
            if st.button("🚀 Execute Plan", type="primary", disabled=st.session_state.execution_started, use_container_width=True):
                 st.session_state.execution_started = True # Simplified fallback execution logic
                 st.rerun()

with execution_section:
    if st.session_state.execution_started and st.session_state.plan_run_obj:
        st.markdown("### ⚙️ 3. Execution Status & Output")
        run = st.session_state.plan_run_obj
        try:
            with st.container(border=True):
                if run.state == PlanRunState.NEED_CLARIFICATION:
                    st.subheader("🗣️ Clarification Needed")
                    current_clarifications = run.get_outstanding_clarifications()
                    if not current_clarifications:
                        st.warning("Plan state is NEED_CLARIFICATION, but no outstanding clarifications found. Attempting to resume...")
                        try:
                            with st.spinner("Attempting to resume..."):
                                st.session_state.plan_run_obj = st.session_state.portia_instance.resume(run)
                            st.rerun()
                        except Exception as e:
                            st.session_state.error_message = f"Error trying to resume after empty clarification list: {e}"
                            st.session_state.execution_started = False 
                            st.rerun()
                    else:
                        st.session_state.clarifications_to_resolve = current_clarifications
                        with st.form(key="clarification_form"):
                            for i, clar in enumerate(st.session_state.clarifications_to_resolve):
                                field_key = f"clar_input_{clar.id}_{i}"
                                
                                # Safely get the title/question for the clarification
                                clar_title = getattr(clar, 'name', None) # Try 'name' first
                                if not clar_title:
                                    clar_title = getattr(clar, 'message', "Clarification Needed") # Try 'message' if 'name' is not found
                                
                                st.markdown(f"**{clar_title} asks:**") 
                                st.caption(clar.user_guidance)

                                if isinstance(clar, InputClarification):
                                    st.session_state.clarification_answers[clar.id] = st.text_input(
                                        label="Your response:", key=field_key,
                                        value=st.session_state.clarification_answers.get(clar.id, ""), label_visibility="collapsed"
                                    )
                                elif isinstance(clar, MultipleChoiceClarification):
                                    options_display = [str(opt) for opt in clar.options]
                                    prev_ans_display = str(st.session_state.clarification_answers.get(clar.id, ""))
                                    current_value_idx = options_display.index(prev_ans_display) if prev_ans_display in options_display and options_display else 0
                                    selected_display_option = st.selectbox(
                                        label="Choose an option:", options=options_display,
                                        index=current_value_idx, key=field_key, label_visibility="collapsed"
                                    )
                                    original_option_idx = options_display.index(selected_display_option)
                                    st.session_state.clarification_answers[clar.id] = clar.options[original_option_idx]
                                elif isinstance(clar, ActionClarification):
                                    st.markdown(f"Please complete the action at: [{clar.action_url}]({clar.action_url}) Click the button below once done.")
                                    # For ActionClarification, we don't take text input, user completes action externally.
                                    # The form submission itself will be the acknowledgment.
                                    st.session_state.clarification_answers[clar.id] = "ACTION_USER_WILL_COMPLETE"
                                else:
                                    st.warning(f"Unsupported clarification type: {type(clar)}")
                                if i < len(st.session_state.clarifications_to_resolve) - 1:
                                     st.markdown("---")

                            submitted_clarifications = st.form_submit_button("✅ Submit Clarifications / Acknowledge Action", use_container_width=True)
                        
                        if submitted_clarifications:
                            st.session_state.info_message = "Processing clarifications..."
                            st.session_state.error_message = None
                            current_run_obj = st.session_state.plan_run_obj
                            action_clarification_present = any(isinstance(c, ActionClarification) for c in st.session_state.clarifications_to_resolve)

                            try:
                                with st.spinner("🧠 Portia is thinking about your answers..."):
                                    for clar_obj in st.session_state.clarifications_to_resolve:
                                        if isinstance(clar_obj, (InputClarification, MultipleChoiceClarification)):
                                            user_response = st.session_state.clarification_answers.get(clar_obj.id)
                                            if user_response is None: 
                                                st.warning(f"No input provided for clarification: {clar_obj.name}")
                                                continue
                                            # Aligning with Portia docs: pass the clarification object directly
                                            current_run_obj = st.session_state.portia_instance.resolve_clarification(
                                                clar_obj, user_response, current_run_obj # Pass clar_obj, value, plan_run
                                            )
                                        elif isinstance(clar_obj, ActionClarification):
                                            # User has acknowledged they will complete the action.
                                            # Now we tell Portia to wait for the external system signal.
                                            st.info(f"Waiting for completion of action: {clar_obj.name} - {clar_obj.action_url}")
                                            try:
                                                current_run_obj = st.session_state.portia_instance.wait_for_ready(current_run_obj, timeout_seconds=180) # Added timeout
                                                st.success(f"Action {clar_obj.name} completed!")
                                            except TimeoutError:
                                                st.error(f"Timed out waiting for action {clar_obj.name} to complete.")
                                                # Plan might be stuck or failed; next resume might reflect this state.
                                            except Exception as wf_ex:
                                                st.error(f"Error during wait_for_ready for {clar_obj.name}: {wf_ex}")
                                    
                                    # After resolving all or waiting for actions, resume the main plan run
                                    st.session_state.plan_run_obj = st.session_state.portia_instance.resume(current_run_obj)
                                
                                st.session_state.clarifications_to_resolve = []
                                st.session_state.clarification_answers = {}
                                st.session_state.info_message = "Clarifications processed. Resuming plan. New state: " + st.session_state.plan_run_obj.state.value
                            except Exception as e:
                                st.session_state.error_message = f"Error processing clarifications: {e}\n{traceback.format_exc()}"
                            st.rerun()

                elif run.state == PlanRunState.COMPLETE:
                    st.balloons() 
                    st.success("✅ Plan Execution Complete!")
                    if run.outputs and run.outputs.final_output:
                        st.subheader("Final Output:")
                        output_val = run.outputs.final_output.value
                        try: 
                            parsed_json = json.loads(output_val) if isinstance(output_val, str) else output_val
                            st.json(parsed_json)
                        except (json.JSONDecodeError, TypeError):
                            if isinstance(output_val, str) and '\n' in output_val:
                                st.text_area("Output:", value=output_val, height=200, disabled=True)
                            else:
                                st.code(str(output_val), language=None)
                        st.session_state.output_display = output_val
                    else: st.info("Plan completed, but no final output value was provided by Portia.")
                    st.session_state.execution_started = False

                # Updated condition to catch other terminal states like FAILED
                elif run.state not in [PlanRunState.IN_PROGRESS, PlanRunState.NEED_CLARIFICATION, PlanRunState.COMPLETE]:
                    st.error(f"⚠️ Plan Execution Ended with State: {run.state.value}")
                    
                    # Safely try to get error_message from the PlanRun object
                    portia_specific_error = getattr(run, 'error_message', None)
                    
                    if portia_specific_error:
                        st.text_area("Error Details from Portia:", value=str(portia_specific_error), height=150, disabled=True)
                    elif st.session_state.error_message: 
                        # This is populated by the app's own try-except blocks around Portia SDK calls
                        st.text_area("Application Error Details:", value=str(st.session_state.error_message), height=150, disabled=True)
                    else:
                        st.text("Plan execution ended with an error, but no specific error message was available from Portia or the application. Check console logs for details.")
                    st.session_state.execution_started = False

                elif run.state == PlanRunState.IN_PROGRESS:
                    st.info(f"🏃 Plan is currently running (State: {run.state.value}). Waiting for next step or external action...")
                # No explicit else needed here as all known states are covered, 
                # or implicitly fall into the generic terminal state handler above.

        except TypeError:
            st.write("Execution status details...") # Simplified fallback for older Streamlit

st.markdown("---")
st.caption("Powered by Portia and Streamlit. Ensure `.env` is configured in the `aci-portia` directory.") 