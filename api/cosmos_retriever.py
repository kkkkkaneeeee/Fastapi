import os
import logging
from typing import Optional
from dotenv import load_dotenv
from azure.cosmos import CosmosClient

# --- 配置 ---
load_dotenv()
ENDPOINT = os.getenv("COSMOS_ENDPOINT")
KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "PromptEngineeringDB"
CONTAINER_NAME = "answers"

# --- 全局客户端实例 ---
# 在生产环境（如FastAPI应用）中，CosmosClient实例应该在应用启动时创建一次并全局复用，
# 以避免在每个请求中都建立新连接的开销。
try:
    client = CosmosClient(url=ENDPOINT, credential=KEY)
    database_client = client.get_database_client(DATABASE_NAME)
    container_client = database_client.get_container_client(CONTAINER_NAME)
    logging.info("Cosmos DB client initialized successfully for cosmos_retriever module.")
except Exception as e:
    client = None
    container_client = None
    logging.error(f"Failed to initialize Cosmos DB client: {e}")
    # 在应用无法连接数据库时，应该有更健壮的处理，这里仅作记录

def get_answer_text(question_id: str, category: str) -> Optional[str]:
    """
    根据 question_id 和 category 从 Cosmos DB 检索唯一的泛化回答文本。

    Args:
        question_id (str): 问题ID，例如 'question_00'。
        category (str): 回答类别，例如 'Start_Doing'。

    Returns:
        Optional[str]: 如果找到，返回回答文本；否则返回 None。
    """
    if not container_client:
        logging.error("数据库客户端未初始化，无法执行查询。")
        return None

    # 1. 构造参数化SQL查询以防止SQL注入
    query = (
        "SELECT c.text FROM c "
        "WHERE c.question_id = @question_id AND c.category = @category"
    )
    
    parameters = [
        {"name": "@question_id", "value": question_id},
        {"name": "@category", "value": category},
    ]

    logging.info(f"执行查询: {query} with params: {parameters}")

    try:
        # 2. 执行查询
        # enable_cross_partition_query 设为 True 是一个好习惯，尽管此查询会命中特定分区
        items = list(container_client.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        # 3. 处理查询结果
        if not items:
            logging.warning(f"未找到匹配项: question_id='{question_id}', category='{category}'")
            return None
        
        if len(items) > 1:
            logging.warning(
                f"找到 {len(items)} 条匹配项，预期为1条。将返回第一条。 "
                f"Query: question_id='{question_id}', category='{category}'"
            )
        
        # 返回第一条记录中的 'text' 字段
        return items[0].get("text")

    except Exception as e:
        logging.error(f"查询数据库时发生错误: {e}")
        return None