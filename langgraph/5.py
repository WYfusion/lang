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

agent = create_agent(llm, tools=[get_current_date], system_prompt="你是我的人工智能助手，协助我获取信息并完成任务。")

# 询问⼤模型。⼤模型会判断需要调⽤⼯具，并返回⼀个⼯具调用请求
response = agent.invoke({"messages":[{"role":"user","content":"今天是⼏⽉⼏号？"}]})
print(response["messages"][-1].content)
response = agent.invoke({"messages":[{"role":"user","content":"明天呢？"}]})
print(response["messages"][-1].content)


# # 打印响应内容，安全处理特殊字符
# try:
#     print(response)
# except UnicodeError:
#     print(response.encode('utf-8', errors='ignore').decode('utf-8'))

