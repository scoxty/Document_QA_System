# 1.Load 导入Document Loaders
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from typing import Dict, List, Any
from langchain.embeddings.base import Embeddings
from pydantic import BaseModel
from volcenginesdkarkruntime import Ark

# 加载Documents
base_dir = "./OneFlower"
documents = []
for file in os.listdir(base_dir):
    # 构建完整的文件路径
    file_path = os.path.join(base_dir, file)
    if file.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
        documents.extend(loader.load())
    elif file.endswith(".txt"):
        loader = TextLoader(file_path)
        documents.extend(loader.load())

# 2.Split 将Documents切分成块以便后续进行嵌入和向量存储
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
chunked_documents = text_splitter.split_documents(documents)

# 3.Store 将分割嵌入并存储在矢量数据库Qdrant中
from langchain_community.vectorstores import Qdrant

class DoubaoEmbeddings(BaseModel, Embeddings):
    client: Ark = None
    api_key: str = ""
    model: str
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.api_key == "":
            self.api_key = os.environ["OPENAI_API_KEY"]
        self.client = Ark(
            base_url=os.environ["OPENAI_BASE_URL"],
            api_key=self.api_key,
        )

    def embed_query(self, text: str) -> List[float]:
        """
        生成输入文本的 embedding.
        Args:
            texts (str): 要生成 embedding 的文本.
        Return:
            embeddings (List[float]): 输入文本的 embedding，一个浮点数值列表.
        """
        embeddings = self.client.embeddings.create(model=self.model, input=text)
        return embeddings.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]


vectorstore = Qdrant.from_documents(
    documents=chunked_documents,
    embedding=DoubaoEmbeddings(
        model=os.environ["EMBEDDING_MODELEND"]
    ), # 用豆包的Embedding model做嵌入
    location=":memory:", # in-memory存储
    collection_name="my_documents", # 指定collection_name
)

# 4. Retrieval 准备模型和Retrieval链
import logging  # 导入Logging工具
from langchain_openai import ChatOpenAI  # ChatOpenAI模型
from langchain.retrievers.multi_query import (
    MultiQueryRetriever,
)  # MultiQueryRetriever工具
from langchain.chains import RetrievalQA  # RetrievalQA链

# 设置Logging
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

# 实例化一个大模型工具 - Doubao-pro-32k
llm = ChatOpenAI(model=os.environ["LLM_MODELEND"], temperature=0)

# 实例化一个MultiQueryRetriever
retriever_from_llm = MultiQueryRetriever.from_llm(retriever=vectorstore.as_retriever(), llm=llm)

# 实例化一个RetrievalQA链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever_from_llm,   # 你的 MultiQueryRetriever
    chain_type="stuff",            # 默认即可，也可选 refine, map_reduce…
)

# 5. Output 问答系统的UI实现
from flask import Flask, request, render_template

app = Flask(__name__) # Flask APP

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # 接收用户输入作为问题
        question = request.form.get("question")

        # RetrievalQA链 - 读入问题，生成答案
        result = qa_chain({"query": question})

        # 把大模型的回答结果返回网页进行渲染
        return render_template("index.html", result=result)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=3000)