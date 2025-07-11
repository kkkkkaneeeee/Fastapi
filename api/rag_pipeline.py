from typing import List

class RAGPipeline:
    def __init__(self):
        pass

    def retrieve(self, question: str) -> List[str]:
        """
        模拟检索模块，返回与问题相关的文档片段列表。
        """
        # 这里简单模拟，实际可替换为真实检索逻辑
        return [f"相关文档片段1: 关于{question}", f"相关文档片段2: 关于{question}"]

    def prompt(self, question: str, answer: str, contexts: List[str]) -> str:
        """
        模拟Prompt输入，返回增强后的答案。
        """
        # 这里简单拼接，实际可替换为LLM调用
        context_str = " ".join(contexts)
        return f"原答案: {answer} | 参考: {context_str}"

    def enhance_answer(self, question: str, answer: str) -> str:
        """
        编排逻辑：先检索，再用Prompt增强答案。
        """
        contexts = self.retrieve(question)
        enhanced = self.prompt(question, answer, contexts)
        return enhanced 