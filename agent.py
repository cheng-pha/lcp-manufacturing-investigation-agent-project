import os
import json
from openai import OpenAI
from tools.manufacturing import (
    get_device,
    get_device_history,
    get_assembly_status,
    get_hold_status,
    get_devices_on_hold,
    get_devices_by_lot,
)
from tools.quality import (
    get_quality_events,
    get_scrap_events,
    get_scrap_summary,
    get_quality_summary,
)
from tools.procedures import search_procedures
# -------------------------
# Debugger
# -------------------------
DEBUG=False

# -------------------------
# OpenAI client
# -------------------------
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

# -------------------------
# Agent Instructions/Info
# -------------------------
agent_instructions="""
    You are an Assembly Part Tracking and Manufacturing Investigation Agent.

    Your responsibility is to investigate the status, history, and processing of manufacturing parts and assemblies.

    Scope:
    This agent is limited to manufacturing investigation and assembly tracking.

    Only assist with questions related to:
    - Device and assembly status
    - Manufacturing process history
    - Quality events
    - Scrap events and reasons
    - Production holds and waiting periods
    - Manufacturing procedures and policies
    - Lots and related manufacturing records

    If a request is unrelated to manufacturing investigation, do not answer the unrelated question or provide general-purpose assistance. Briefly state that the request is outside the scope of the manufacturing investigation agent.

    You can retrieve:
    - Part and assembly information
    - Assembly process history
    - Quality and inspection events
    - Scrap events and reasons
    - Production holds and waiting periods
    - Manufacturing procedures and policies

    When investigating a part:
    1. Identify the part and current assembly state.
    2. Review its relevant process history.
    3. Check for quality events, holds, and scrap events.
    4. Use manufacturing procedures to determine whether actions were required.
    5. Explain the current state or reason for scrap using the available data.
    6. Do not invent information that is not present in the available data.
    7. If the procedure doesn't explicitly say it, don't claim it does. Do not substitute general manufacturing, medical-device, industry, or domain knowledge for information that is absent from the procedure search results.
    8. Only claim that an action was performed if a tool actually performed that action.
    9. Never offer, suggest, or imply that you can take an action unless an explicit tool exists to perform that action. This includes releasing holds, updating records, moving devices, creating tickets, sending alerts, or modifying manufacturing data. Do not ask the user whether they want you to perform an unsupported action. If no tool exists for the requested action, state that the agent can only report the current recorded state.
    10. When a question asks whether a process, hold, inspection, or requirement is completed, distinguish between elapsed time and recorded completion status. Do not treat an elapsed duration as proof of completion when the record shows IN_PROGRESS, OPEN, or another incomplete status.
    11. Do not infer a failure, defect, rejection, or other negative outcome from an event type, status, or description unless the source explicitly states that the outcome occurred. Report the source terminology as written when possible.
    12. When a user asks whether a procedure, policy, or documented requirement supports, permits, requires, or prohibits an action, you must call search_procedures before answering. Do not answer from general knowledge. The procedure search results are the source of truth for procedural claims.

    When possible, provide a chronological explanation of the part's journey through the assembly process.
"""


# -------------------------
# Tool definitions
# -------------------------
tools = [
    {
        "type": "function",
        "name": "get_device",
        "description": "Retrieve basic information about a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The unique device identifier in the format LCP-XXXXX."
                }
            },
            "required": ["device_id"]
        }
    },

    {
        "type": "function",
        "name": "get_device_history",
        "description": "Retrieve the manufacturing process history for a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The unique device identifier in the format LCP-XXXXX."
                }
            },
            "required": ["device_id"]
        }
    },

    {
        "type": "function",
        "name": "get_assembly_status",
        "description": "Retrieve the current assembly status and process step for a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The unique device identifier in the format LCP-XXXXX."
                }
            },
            "required": ["device_id"]
        }
    },

    {
        "type": "function",
        "name": "get_quality_events",
        "description": "Retrieve quality and inspection events associated with a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The unique device identifier in the format LCP-XXXXX."
                }
            },
            "required": ["device_id"]
        }
    },

    {
        "type": "function",
        "name": "get_scrap_events",
        "description": "Retrieve scrap events and scrap reasons associated with a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The unique device identifier in the format LCP-XXXXX."
                }
            },
            "required": ["device_id"]
        }
    },

    {
        "type": "function",
        "name": "get_hold_status",
        "description": "Retrieve production hold information for a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "string",
                    "description": "The unique device identifier in the format LCP-XXXXX."
                }
            },
            "required": ["device_id"]
        }
    },
    {
        "type": "function",
        "name": "get_devices_on_hold",
        "description": "Find all devices that currently have an active manufacturing hold.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_scrap_summary",
        "description": "Summarize scrap events by reason code across all devices.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_devices_by_lot",
        "description": "Find all devices associated with a specific manufacturing lot.",
        "parameters": {
            "type": "object",
            "properties": {
                "lot": {
                    "type": "string",
                    "description": "The manufacturing lot identifier, such as LOT-2026-042."
                }
            },
            "required": ["lot"]
        }
    },
    {
        "type": "function",
        "name": "get_quality_summary",
        "description": "Summarize quality events across all devices by event type, severity, and status.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "search_procedures",
        "description": "Search documented manufacturing procedures, policies, requirements, and rules when answering questions about whether an action or disposition is supported, permitted, required, or prohibited. Use this tool as the source of truth for procedural claims rather than relying on general knowledge.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Describe the procedure, policy, requirement, or rule needed to answer the question."
                }
            },
            "required": ["query"]
        }
    }
]

# -------------------------
# Tool Registry
# -------------------------
available_tools = {
    "get_device": get_device,
    "get_device_history": get_device_history,
    "get_assembly_status": get_assembly_status,
    "get_quality_events": get_quality_events,
    "get_scrap_events": get_scrap_events,
    "get_hold_status": get_hold_status,
    "get_scrap_summary": get_scrap_summary,
    "get_devices_on_hold": get_devices_on_hold,
    "get_devices_by_lot": get_devices_by_lot,
    "get_quality_summary": get_quality_summary,
    "search_procedures": search_procedures
}

# -------------------------
# Agent runner
# -------------------------
def run_agent(prompt, previous_response_id=None):
    request_args = {
        "model": deployment_name,
        "instructions": agent_instructions,
        "input": prompt,
        "tools": tools,
        "tool_choice": "auto",
    }

    if previous_response_id:
        request_args["previous_response_id"] = previous_response_id

    response = client.responses.create(**request_args)
    yield {
    "type": "status",
    "message": "Analyzing your question...",
    }

    # Execute tools until the model is ready to produce its final answer.
    while True:
        function_calls = [
            item for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            break

        tool_outputs = []

        for item in function_calls:
            tool_function = available_tools.get(item.name)
            yield {
                "type": "status",
                "message": {
                    "get_device": "Retrieving device records...",
                    "get_device_history": "Reviewing device history...",
                    "get_assembly_status": "Checking assembly status...",
                    "get_hold_status": "Checking hold status...",
                    "get_devices_on_hold": "Checking devices on hold...",
                    "get_devices_by_lot": "Reviewing lot records...",
                    "get_quality_events": "Reviewing quality events...",
                    "get_scrap_events": "Reviewing scrap records...",
                    "get_scrap_summary": "Summarizing scrap records...",
                    "get_quality_summary": "Summarizing quality events...",
                    "search_procedures": "Searching documented procedures...",
                }.get(item.name, "Investigating manufacturing records..."),
            }

            if not tool_function:
                result = {"error": f"Unknown tool: {item.name}"}
            else:
                try:
                    arguments = json.loads(item.arguments)

                    if DEBUG:
                        print(f"TOOL CALL: {item.name}")
                        print(f"ARGUMENTS: {arguments}")

                    result = tool_function(**arguments)

                    if DEBUG:
                        print(f"TOOL RESULT: {result}")

                except Exception as exc:
                    if DEBUG:
                        print(f"TOOL ERROR: {item.name}: {exc}")

                    result = {
                        "error": f"Tool {item.name} failed: {str(exc)}"
                    }

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result, default=str),
            })

        response = client.responses.create(
            model=deployment_name,
            instructions=agent_instructions,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools,
            tool_choice="auto",
        )

    # Stream the final answer after tool execution is complete.
    yield {
        "type": "status",
        "message": "Preparing investigation findings...",
    }
    stream = client.responses.create(
        model=deployment_name,
        instructions=agent_instructions,
        previous_response_id=response.id,
        input="Provide your final answer based on the investigation results above.",
        tools=tools,
        tool_choice="none",
        stream=True,
    )

    response_id = None

    for event in stream:
        if event.type == "response.output_text.delta":
            yield {
                "type": "text",
                "text": event.delta,
            }

        elif event.type == "response.completed":
            response_id = event.response.id

    yield {
        "type": "done",
        "response_id": response_id,
    }