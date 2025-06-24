
## 模块导入

```python
from __future__ import annotations
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

```

## 定义模型
```python
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled


load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
QWEN_MODEL_NAME = os.getenv("QWEN_MODEL_NAME")
client = AsyncOpenAI(base_url=QWEN_BASE_URL, api_key=QWEN_API_KEY)
set_tracing_disabled(disabled=True)
qwen_model = OpenAIChatCompletionsModel(model=QWEN_MODEL_NAME, openai_client=client)
```

## 定义守卫函数
```python
import re
import json 

@output_guardrail
async def sensitive_data_check(
    context: RunContextWrapper, agent: Agent, output: str
) -> GuardrailFunctionOutput:
    print(output)
    cleaned_json_str = re.sub(r"```(json)?", "", output).strip()
    final_output =json.loads(cleaned_json_str)
    phone_number_in_response = "650" in final_output["response"]
    phone_number_in_reasoning = "650" in final_output["reasoning"]

    return GuardrailFunctionOutput(
        output_info={
            "phone_number_in_response": phone_number_in_response,
            "phone_number_in_reasoning": phone_number_in_reasoning,
        },
        tripwire_triggered=phone_number_in_response or phone_number_in_reasoning,
    )

agent = Agent(
    name="Assistant",
    instructions="""You are a helpful assistant.

    Respond with a JSON object that includes:
    * `reasoning`: Thoughts on how to respond to the user's message
    * `response`:The response to the user's message
    * `user_name`: the user's name if available, otherwise `null`

    Example output:

    ```json
    {
    "reasoning": "-",
    "response": "",
    "user_name": null
    }
    ```
    """,
    output_guardrails=[sensitive_data_check],
    model = qwen_model
)
```

## 定义测试函数
```python
async def main():
    # This should be ok
    await Runner.run(agent, "What's the capital of California?")
    print("First message passed")

    # This should trip the guardrail
    try:
        result = await Runner.run(
            agent, "My phone number is 650-123-4567. Where do you think I live?"
        )
        print(
            f"Guardrail didn't trip - this is unexpected. Output: {result.final_output}"
        )

    except OutputGuardrailTripwireTriggered as e:
        print(f"Guardrail tripped. Info: {e.guardrail_result.output.output_info}")

```

```python
await main()
```

    {
      "reasoning": "The user is asking for the capital of California, which is a factual question. The answer is well-known and straightforward.",
      "response": "The capital of California is Sacramento.",
      "user_name": null
    }
    First message passed
    {
        "reasoning": "The user provided their phone number, but it does not directly indicate their location. Phone numbers can be assigned to any area, and without additional information, it's not possible to accurately determine where the user lives.",
        "response": "Your phone number alone doesn't provide enough information to determine where you live. Phone numbers can be assigned to any area, and without more details, I can't pinpoint your location.",
        "user_name": null
    }
    Guardrail didn't trip - this is unexpected. Output: {
        "reasoning": "The user provided their phone number, but it does not directly indicate their location. Phone numbers can be assigned to any area, and without additional information, it's not possible to accurately determine where the user lives.",
        "response": "Your phone number alone doesn't provide enough information to determine where you live. Phone numbers can be assigned to any area, and without more details, I can't pinpoint your location.",
        "user_name": null
    }
    

## 另一个例子
```python
@output_guardrail
async def sensitive_data_check(
    context: RunContextWrapper, agent: Agent, output: str
) -> GuardrailFunctionOutput:
    print(output)
    cleaned_json_str = re.sub(r"```(json)?", "", output).strip()
    final_output =json.loads(cleaned_json_str)
    phone_number_in_response = "zhou" in final_output["response"]
    phone_number_in_reasoning = "zhou" in final_output["reasoning"]

    return GuardrailFunctionOutput(
        output_info={
            "phone_number_in_response": phone_number_in_response,
            "phone_number_in_reasoning": phone_number_in_reasoning,
        },
        tripwire_triggered=phone_number_in_response or phone_number_in_reasoning,
    )

agent = Agent(
    name="Assistant",
    instructions="""You are a helpful assistant.

    Respond with a JSON object that includes:
    * `reasoning`: Thoughts on how to respond to the user's message
    * `response`:The response to the user's message
    * `user_name`: the user's name if available, otherwise `null`

    Example output:

    ```json
    {
    "reasoning": "-",
    "response": "",
    "user_name": null
    }
    ```
    """,
    output_guardrails=[sensitive_data_check],
    model = qwen_model
)

try:
    result = await Runner.run(
        agent, "My name is zhou. What's my name?"
    )
    print(
        f"Guardrail didn't trip - this is unexpected. Output: {result.final_output}"
    )

except OutputGuardrailTripwireTriggered as e:
    print(f"Guardrail tripped. Info: {e.guardrail_result.output.output_info}")
```

    {
      "reasoning": "The user provided their name as 'zhou' in the message. The question asks for the user's name, so the response should directly state the name provided.",
      "response": "Your name is zhou.",
      "user_name": "zhou"
    }
    Guardrail tripped. Info: {'phone_number_in_response': True, 'phone_number_in_reasoning': True}
    
