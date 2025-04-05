from openai import OpenAI
from demo_util import color, function_to_schema
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()
openai_key =os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_key)


# === Demo Loop ===

model = "gpt-4o-mini"
system_message = (
    "You are a customer support agent for ACME Inc."
    "Always answer in a sentence or less."
    "Follow the following routine with the user:"
    "1. First, ask probing questions and understand the user's problem deeper.\n"
    " - unless the user has already provided a reason.\n"
    "2. Propose a fix (make one up).\n"
    "3. ONLY if not satisfied, offer a refund.\n"
    "4. If accepted, search for the ID and then execute refund."
    ""
)


def look_up_item(search_query):
    print('look_up_item...........')
    """Use to find item ID.
    Search query can be a description or keywords."""
    item_id = "item_132612938"
    print(color("Found item:", "green"), item_id)
    return item_id


def execute_refund(item_id, reason="not provided"):
    print('execute_refund..........')
    print(color("\n\n=== Refund Summary ===", "green"))
    print(color(f"Item ID: {item_id}", "green"))
    print(color(f"Reason: {reason}", "green"))
    print("=================\n")
    print(color("Refund execution successful!", "green"))
    return "success"


tools = [execute_refund, look_up_item]


def run_full_turn(system_message, tools, messages):
    print('run_full_turn................')
    print(messages)

    num_init_messages = len(messages)
    print('num_init_messages.................')
    print(num_init_messages)
    messages = messages.copy()
    # print(messages)

    while True:

        # turn python functions into tools and save a reverse map
        tool_schemas = [function_to_schema(tool) for tool in tools]
        tools_map = {tool.__name__: tool for tool in tools}

        # === 1. get openai completion ===
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_message}] + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:  # print assistant response
            print('message.content......................')
            print(color("Assistant:", "yellow"), message.content)

        if not message.tool_calls:  # if finished handling tool calls, break
            print('breaking.........')
            print(message)

            break

        # === 2. handle tool calls ===

        for tool_call in message.tool_calls:
            print('tool_call..........')
            print(tool_call)
            result = execute_tool_call(tool_call, tools_map)

            print('result......................')
            print(result)

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    # ==== 3. return new messages =====
    return messages[num_init_messages:]


def execute_tool_call(tool_call, tools_map):
    print('execute_tool_call...................')
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(color("Assistant:", "yellow"), color(f"{name}({args})", "magenta"))

    # call corresponding function with provided arguments
    return tools_map[name](**args)


messages = []
while True:
    user = input(color("User: ", "blue") + "\033[90m")
    messages.append({"role": "user", "content": user})

    new_messages = run_full_turn(system_message, tools, messages)
    print('new_message.....................')
    print(new_messages)
    messages.extend(new_messages)
    print("messages..............")
    print(messages)