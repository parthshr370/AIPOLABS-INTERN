Agentic Data Model Generation and Structured Output Powered by CAMEL & Qwen
You can also check this cookbook in Colab.CAMEL Homepage | Join Discord | ⭐ Star us on GitHub
This notebook demonstrates how to set up and leverage CAMEL’s ability to produce structured output, such as JSON and Pydantic objects. In this notebook, you’ll explore:

CAMEL: A powerful multi-agent framework that enables Retrieval-Augmented Generation and multi-agent role-playing scenarios, allowing for sophisticated AI-driven tasks.
Structured Output: The ability of LLMs to return structured output.
Qwen: A series of LLMs and multimodal models developed by the Qwen Team at Alibaba Group. Designed for diverse scenarios, Qwen integrates advanced AI capabilities, such as natural language understanding, text and vision processing, programming assistance, and dialogue simulation.

This setup not only demonstrates a practical application but also serves as a flexible framework that can be adapted for various scenarios requiring structured output and data generation.
📦 Installation
First, install the CAMEL package with all its dependencies:
!pip install "camel-ai==0.2.16"

🔑 Setting Up API Keys
You can obtain an API Key from Qwen AI.
# Prompt for the API key securely
import os
from getpass import getpass

qwen_api_key = getpass('Enter your API key: ')
os.environ["QWEN_API_KEY"] = qwen_api_key

Alternatively, if running on Colab, you can save your API keys and tokens as Colab Secrets and use them across notebooks. To do so, comment out the above manual API key prompt code block(s), and uncomment the following code block. ⚠️ Don’t forget to grant access to the API key you would be using to the current notebook.
# import os
# from google.colab import userdata

# os.environ["QWEN_API_KEY"] = userdata.get("QWEN_API_KEY")

Qwen Data Generation
In this section, we’ll demonstrate how to use Qwen to generate structured data. Qwen is a good example in CAMEL of using prompt engineering for structured output. It offers powerful models like Qwen-max and Qwen-coder but does not support structured output by itself. We can leverage its ability to generate structured data. Import necessary libraries, define the Qwen agent, and define the Pydantic classes. The following function retrieves relevant information from a list of URLs based on a given query, combining web scraping with Firecrawl and CAMEL’s AutoRetriever for a seamless information retrieval process.
from pydantic import BaseModel, Field
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import QwenConfig

# Define Qwen model
qwen_model = ModelFactory.create(
    model_platform=ModelPlatformType.QWEN,
    model_type=ModelType.QWEN_CODER_TURBO,
    model_config_dict=QwenConfig().as_dict(),
)

qwen_agent = ChatAgent(
    model=qwen_model,
    message_window_size=10,
)

# Define Pydantic models
class Student(BaseModel):
    name: str
    age: str
    email: str

First, let’s try generating structured output using a prompt without specifying a format:
assistant_sys_msg = BaseMessage.make_assistant_message(
    role_name="Assistant",
    content="You are a helpful assistant in helping user to generate necessary data information.",
)

user_msg = """Help me 1 student info in JSON format, with the following format:
{
    "name": "string",
    "age": "string",
    "email": "string"
}"""

response = qwen_agent.step(user_msg)
print(response.msgs[0].content)

This approach works, but the result may include extra text, and we would need to parse it into a valid JSON object manually. A more elegant way is to use the response_format argument in the .step() function:
qwen_agent.reset()
user_msg = "Help me 1 student info in JSON format"
response = qwen_agent.step(user_msg, response_format=Student)
print(response.msgs[0].content)

You can directly extract the Pydantic object from the response.msgs[0].parsed field:
print(type(response.msgs[0].parsed))
print(response.msgs[0].parsed)

Hooray, now we’ve successfully generated one student entry! To generate multiple entries, we can define a new Pydantic model:
class StudentList(BaseModel):
    studentList: list[Student]

user_msg = "Help me 5 random student info in JSON format"
response = qwen_agent.step(user_msg, response_format=StudentList)
print(response.msgs[0].content)
print(response.msgs[0].parsed)

That’s it! We just generated five random student entries using the Qwen CAMEL agent!
🌟 Highlights
This notebook has guided you through setting up and running a Qwen chat agent to generate structured data. Key tools utilized include:

CAMEL: A powerful multi-agent framework that enables Retrieval-Augmented Generation and multi-agent role-playing scenarios, allowing for sophisticated AI-driven tasks.
Qwen Data Generation: Use the Qwen model to generate structured data for further use in other applications.

That’s everything! Got questions about 🐫 CAMEL-AI? Join us on Discord! Whether you want to share feedback, explore the latest in multi-agent systems, get support, or connect with others on exciting projects, we’d love to have you in the community! 🤝 Check out some of our other work:

🐫 Creating Your First CAMEL Agent (free Colab)
Graph RAG Cookbook (free Colab)
🧑‍⚖️ Create A Hackathon Judge Committee with Workforce (free Colab)
🔥 3 Ways to Ingest Data from Websites with Firecrawl & CAMEL (free Colab)
🦥 Agentic SFT Data Generation with CAMEL and Mistral Models, Fine-Tuned with Unsloth (free Colab)

Thanks from everyone at 🐫 CAMEL-AI!CAMEL Homepage | Join Discord | ⭐ Star us on GitHub
