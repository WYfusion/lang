import io
import datetime
from langchain.tools import tool
from langchain_community.chat_models import ChatTongyi
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from env_utils import ALIBABA_API_KEY
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
# 设置stdout为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 构建阿⾥云百炼⼤模型客户端
llm = ChatTongyi(
    model="qwen-plus",
    DASHSCOPE_API_KEY=ALIBABA_API_KEY,
    checkpointer=InMemorySaver()
)
# 定义⼯具 注意要添加注释
@tool
def get_current_date():
    """获取今天⽇期"""
    return datetime.datetime.today().strftime("%Y-%m-%d")

client = MultiServerMCPClient(
    {
        "amap-maps": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
            ],
            "env": {
                "AMAP_MAPS_API_KEY": "dd4cac7c5632aa22af453ad2af88ea3b"
            }
            }
    }
)
async def main():
    tools = await client.get_tools()
    agent = create_agent(llm, tools=[get_current_date, *tools], system_prompt="你是我的人工智能助手，协助我获取信息并完成任务。")

    # 询问⼤模型。⼤模型会判断需要调⽤⼯具，并返回⼀个⼯具调用请求
    response = await agent.ainvoke({"messages":[{"role":"user","content":"从北京大学到广州大学城的驾车路线怎么走？"}]})
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())


# # 打印响应内容，安全处理特殊字符
# try:
#     print(response)
# except UnicodeError:
#     print(response.encode('utf-8', errors='ignore').decode('utf-8'))

