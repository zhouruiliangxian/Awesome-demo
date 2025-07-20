import asyncio
import os
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv

load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME")


import base64
 
# Replace with your Langfuse keys.
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-fde3d9a0-4601-4914-96d8-09b8a5da4d14"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-72ad0880-d2f8-4abd-a1e4-b8ca87dab938" 
os.environ["LANGFUSE_HOST"] = "http://localhost:3000"

# Build Basic Auth header.
LANGFUSE_AUTH = base64.b64encode(
    f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()
).decode()
 
# Configure OpenTelemetry endpoint & headers
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
 

client = AsyncOpenAI(base_url=QWEN_BASE_URL, api_key=QWEN_API_KEY)

import logfire
 

logfire.configure(
    service_name='my_agent_service',
 
    send_to_logfire=False,
)

logfire.instrument_openai_agents()


async def main():
    # This agent will use the custom LLM provider
    agent = Agent(
        name="Assistant",
        instructions="你只讲中文，即使是英文问题，也只讲中文",
        model=OpenAIChatCompletionsModel(model=QWEN_MODEL_NAME, openai_client=client),
    )

    result = await Runner.run(agent, "hello, tell me about langfuse ")
    print(result.final_output)

asyncio.run(main())