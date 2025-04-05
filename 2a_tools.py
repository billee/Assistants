from openai import OpenAI
from demo_util import color
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)
MODEL='gpt-4o-mini'

# === Tool Schemas ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_refund",
            "description": "Execute a refund for an item",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["item_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "look_up_item",
            "description": "Find item ID using search terms",
            "parameters": {
                "type": "object",
                "properties": {"search_query": {"type": "string"}},
                "required": ["search_query"],
            },
        },
    },
]


# === Python Function Implementations ===
def look_up_item(search_query):
    """Use to find item ID.
    Search query can be a description or keywords."""
    # In real implementation, this would search a database
    item_id = "item_132612938"
    print(color(f"\n[System] Found item for '{search_query}': {item_id}", "green"))
    return item_id


def execute_refund(item_id, reason="not provided"):
    # In real implementation, this would interface with payment system
    print(color("\n\n=== Refund Summary ===", "green"))
    print(color(f"Item ID: {item_id}", "green"))
    print(color(f"Reason: {reason}", "green"))
    print("========================")
    print(color("[System] Refund executed successfully!", "green"))
    return "success"


# === Execution Handling ===
def run_full_turn(system_message, tools, messages):
    while True:
        # Get AI response
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_message}] + messages,
            tools=tools,
        )
        message = response.choices[0].message
        messages.append(message.to_dict())  # Convert to dict for easier handling

        # Handle content response
        if message.content:
            print(color("Assistant:", "yellow"), message.content)
            return

        # Handle tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(color(f"\n[System] Executing {func_name}(", "magenta") +
                      color(f"{args})", "cyan") + color(")", "magenta"))

                # Execute corresponding Python function
                result = globals()[func_name](**args)

                # Add result to conversation history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": str(result),
                })


# === Main Loop ===
system_message = (
    "You are a customer support agent for ACME Inc. "
    "Follow this workflow:\n"
    "1. Ask clarifying questions if needed\n"
    "2. Look up item IDs when necessary\n"
    "3. Process refunds only after confirmation\n"
    "Keep responses concise and professional."
)

messages = []
while True:
    try:
        user_input = input(color("User: ", "blue"))
        messages.append({"role": "user", "content": user_input})
        run_full_turn(system_message, tools, messages)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break