from dotenv import load_dotenv
from portia import (
    Portia,
    default_config,
    example_tool_registry,
)

load_dotenv()

portia = Portia(tools=example_tool_registry)

plan = portia.plan('Which Stock Price grew faster in tech area')

# Serialise into JSON and print the output
print(plan.model_dump_json(indent=2))