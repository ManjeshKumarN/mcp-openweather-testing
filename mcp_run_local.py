import asyncio
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# as tools are async we need to use async main
# as tools are async and graph uses tools, need to define the graph inside async main only as when the 
# graph is compiled the tools amy not be available
async def main():
    groq_api_key = os.getenv("GROQ_API_KEY")
    owm_key = os.getenv("OWM_API_KEY")

    client = MultiServerMCPClient( # creating the mcp client and start the servers provided
        {
            "weather":{ # defining the mcp server for weather
                "transport": "stdio",
                "command": "/workspaces/mcp-openweather-testing/mcp-weather.exe", # MCP server 
                "args": [],
                "env": {"OWM_API_KEY": owm_key}
                    },
            "calculator": { # defining the mcp server for calculator
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "mcp_server_calculator"]
                    }
        }
    )

    tools = await client.get_tools() # getting the tools from the mcp server

    print(tools)

    llm = ChatGroq(temperature=0, model="openai/gpt-oss-20b", api_key=groq_api_key)

    async def call_model(state):
        response = llm.bind_tools(tools = tools).invoke(state["messages"])
        return {"messages": response}

    # building the graph
    graph = StateGraph(state_schema=MessagesState)

    graph.add_node(node="call_model",action=call_model)
    graph.add_node(node="tools", action=ToolNode(tools=tools))

    graph.add_edge(START, "call_model")
    graph.add_conditional_edges(source="call_model", path=tools_condition)
    graph.add_edge("tools", "call_model")

    graph_mcp = graph.compile()

    while True:
        user_input = input("Ask me anything on weather or calculations (press enter to continue)-->")
        if user_input.lower().strip() in ["exit", "quit"]:
            break
        else:
            result = await graph_mcp.ainvoke({"messages":user_input})
            print(result["messages"][-1].content)
            print("-------------------------")    
            print(result)
            print("-------------------------")

if __name__ == "__main__":
    asyncio.run(main())