# 简介
项目名称：“易速鲜花”内部员工知识库问答系统。<br>
项目介绍：“易速鲜花”作为一个大型在线鲜花销售平台，有自己的业务流程和规范，也拥有针对员工的SOP手册。新员工入职培训时，会分享相关的信息。但是，这些信息分散于内部网和HR部门目录各处，有时不便查询；有时因为文档过于冗长，员工无法第一时间找到想要的内容；有时公司政策已更新，但是员工手头的文档还是旧版内容。<br>
基于上述需求，我们将开发一套基于各种内部知识手册的 “Doc-QA” 系统。这个系统将充分利用LangChain框架，处理从员工手册中产生的各种问题。这个问答系统能够理解员工的问题，并基于最新的员工手册，给出精准的答案。
# 原理
![image](https://github.com/user-attachments/assets/0d85efe7-0bcb-46da-abfd-77d30196e8c3)
如图，先把本地知识切片后做Embedding，存储到向量数据库中，然后把用户的输入和从向量数据库中检索到的本地知识传递给大模型，最终生成所想要的回答
# 运行效果
![image](https://github.com/user-attachments/assets/15710cb6-c23d-4108-a82d-e05e9d2bf7f3)



