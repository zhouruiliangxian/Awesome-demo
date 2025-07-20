
@[TOC](目录)

## 版本
```python
import agents
print(agents.__version__)
```

    0.0.19
    

## 模块引入
```python
from __future__ import annotations

from pydantic import BaseModel

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)


```

## 自定义LLM模型
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

## input_guardrail设置
```python
import json
import re
### 1. An agent-based guardrail that is triggered if the user is asking to do math homework
class MathHomeworkOutput(BaseModel):
    reasoning: str
    is_math_homework: bool


guardrail_agent = Agent(
    name="Guardrail check",
    instructions="""Check if the user is asking you to do their math homework. 
    Respond with a JSON object that includes:
    - 'reasoning': your analysis of why this is or isn't math homework
    - 'is_math_homework': boolean value indicating if it's math homework
    
    Example output:
    ```json
    {
        "reasoning": "The user greeted me with a simple 'hello', which does not indicate any mathematical problem or task.",
        "is_math_homework": false
    }
    ```

    """
    ,
    model=qwen_model
)

@input_guardrail
async def math_guardrail(
    context: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """This is an input guardrail function, which happens to call an agent to check if the input
    is a math homework question.
    """
    result = await Runner.run(guardrail_agent, input, context=context.context)
    print(result.final_output)
    cleaned_json_str = re.sub(r"```(json)?", "", result.final_output).strip()

    final_output =json.loads(cleaned_json_str)
    
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output["is_math_homework"],
    )
```

## main函数
```python
async def main():
    agent = Agent(
        name="Customer support agent",
        instructions="You are a customer support agent. You help customers with their questions.",
        input_guardrails=[math_guardrail],
        model = qwen_model
    )

    input_data: list[TResponseInputItem] = []

    while True:
        user_input = input("Enter a message: ")

        if user_input == "exit":
            break
        
        input_data.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            result = await Runner.run(agent, input_data)
            print(result.final_output)
            input_data = result.to_input_list()
        except InputGuardrailTripwireTriggered:
            message = "Sorry, I can't help you with your math homework."
            print(message)
            input_data.append(
                {
                    "role": "assistant",
                    "content": message,
                }
            )

await main()
```

    ```json
    {
        "reasoning": "The user asked for the capital of California, which is a geography question and not related to mathematics.",
        "is_math_homework": false
    }
    ```
    The capital of California is **Sacramento**. Let me know if you have any more questions!
    ```json
    {
        "reasoning": "The user provided an algebraic equation (2x + 5 = 11) that requires solving for the variable x. This is a typical math problem often assigned as part of homework.",
        "is_math_homework": true
    }
    ```
    Sorry, I can't help you with your math homework.
    
