import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient # need to work with mcp with langgraph
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

async def main():
    groq_api_key = os.getenv("GROQ_API_KEY")

    llm = ChatGroq(temperature=0, model="openai/gpt-oss-20b", api_key=groq_api_key)

    client = MultiServerMCPClient( # allow to connect with multiple MCP servers
        {
            "math":{
                "command": "python",
                "args": ["/workspaces/mcp-openweather-testing/custom_mcp_server.py"], #absolute path for custom mcp server
                "transport": "stdio" # stdio will work only when both client and server are in same machine 
            },
            # "math":{
            #     "url": "http://127.0.0.1:8000/mcp", # custom mcp server url
            #     "transport": "streamable-http" # streamable-http should be used when the server in remote machine 
            # }
        }
    )

    tools = await client.get_tools()
    print(tools)

    llm_with_tools = llm.bind_tools(tools=tools)

    tool_node = ToolNode(tools=tools)

    def should_continue(state): # tools_condition 
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        else:
            return END

    async def call_model(state):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages" : response}

    workflow = StateGraph(state_schema=MessagesState)
    workflow.add_node(node="call_model", action=call_model)
    workflow.add_node(node="tool_node",action=tool_node)

    workflow.add_edge(start_key=START, end_key="call_model")
    workflow.add_conditional_edges(source="call_model", path=should_continue, path_map={"tools":"tool_node", END:END})
    workflow.add_edge(start_key="tool_node",end_key="call_model")

    graph = workflow.compile()

    result = await graph.ainvoke(input={"messages":"What is sum of 100 and 50 and they divide the anser by 5 and then multiply by 35 and provide the answer as words use required tools"})
    # result returns the whole state schema as output

    print("----------------------------")
    print(result["messages"][-1].content)
    print("****************************")
    print(result)
    print("****************************")

if __name__ == "__main__":
    asyncio.run(main()) 
    # Creates a new asyncio event loop.
    # Runs the coroutine main() inside that loop until it completes.
    # Closes the loop automatically

