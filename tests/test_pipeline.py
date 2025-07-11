import unittest
from api.rag_pipeline import RAGPipeline

class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = RAGPipeline()

    def test_retrieve(self):
        question = "什么是RAG?"
        contexts = self.pipeline.retrieve(question)
        self.assertIsInstance(contexts, list)
        self.assertTrue(any(question in ctx for ctx in contexts))

    def test_prompt(self):
        question = "什么是RAG?"
        answer = "RAG是一种检索增强生成方法。"
        contexts = ["相关文档片段1: 关于RAG"]
        enhanced = self.pipeline.prompt(question, answer, contexts)
        self.assertIn(answer, enhanced)
        self.assertIn(contexts[0], enhanced)

    def test_enhance_answer(self):
        question = "什么是RAG?"
        answer = "RAG是一种检索增强生成方法。"
        enhanced = self.pipeline.enhance_answer(question, answer)
        self.assertIn(answer, enhanced)
        self.assertIn(question, enhanced)

if __name__ == "__main__":
    unittest.main() 