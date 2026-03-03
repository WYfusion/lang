# 建立模型
## ChatOpenAI
是一个已经采用OpenAI接口的类
'''python
from langchain_openai import ChatOpenAI
model = ChatOpenAI(
    model="qwen3-30b-a3b",
    api_key=ALIBABA_API_KEY,
    base_url=ALIBABA_BASE_URL,
    temperature=0.7,
    extra_body={
        "enable_thinking": False
    }
)
'''


## init_chat_model
统一的类，需要提供模型提供商
'''python
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
'''

# test_use/1.py 调用 config/env_utils.py
'''python
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
'''
