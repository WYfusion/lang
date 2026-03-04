import io
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# 设置stdout为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from env_utils import ALIBABA_API_KEY, ALIBABA_BASE_URL
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="qwen3-30b-a3b",
    model_provider="openai",  # 显式指定模型提供商为openai
    api_key=ALIBABA_API_KEY,
    base_url=ALIBABA_BASE_URL,
    temperature=0.7,
    extra_body={
        "enable_thinking": False
    }
)

response = model.invoke([{"role": "user", "content":"你是谁？能帮我解决什么问题？"}])

# 打印响应内容，安全处理特殊字符
try:
    print(response.content)
except UnicodeError:
    print(response.content.encode('utf-8', errors='ignore').decode('utf-8'))