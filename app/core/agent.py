import asyncio
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langgraph.checkpoint.memory import InMemorySaver

from app.core.prompts import SYSTEM_PROMPT

checkpointer = InMemorySaver()

async def chat_agent():
    
    llm = ChatOllama(model="lfm2.5-thinking:latest")

    McpConfig={}
    
    client = MultiServerMCPClient(McpConfig)
    tools = await client.get_tools()

    agent = create_agent(
        llm,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        checkpointer=checkpointer

    )
 
    return agent

async def main():

        user_input = "What are the available products in the dairy category?"
        config = {"configurable": {"thread_id": "1"}}
        agent = await chat_agent()
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config
        )

        print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())