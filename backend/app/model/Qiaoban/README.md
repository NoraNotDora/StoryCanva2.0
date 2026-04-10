# 儿童对话模型Qiaoban的部署

## 启动api服务

`python server.py`即可在`http://0.0.0.0:6667/chat`启动服务，原来的开源项目没有提供api，我们自己封装了一个

`python client.py`测试api是否能够正常运行

## 界面ui测试

`python chat-ui.py`可以测试gradio界面能否接入对话api进行互动

*其中一个界面版本同时加载了太乙diffusion模型的图像生成，但是由于autodl的实例释放把最新的版本清除了，我们暂时只能找到这个版本的代码*

## 其他文件

`collect.py`处理对话数据集

`topic.txt`对话模型可以和小朋友谈起的话题
