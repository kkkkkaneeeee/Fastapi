from pydantic import BaseModel , RootModel
from typing import Dict, Any, List

# 批量增强请求模型
class AssessmentData(BaseModel):
    serviceOffering: Dict[str, Any]
    # 其它部分用可选字段或直接用 extra
    # 你可以用 extra = "allow" 允许其它任意字段

    class Config:
        extra = "allow"

# 批量增强响应模型
class AssessmentResponse(RootModel[Dict[str, List[Dict[str, Any]]]]):
    pass