import random
import gradio as gr
import requests

url = "http://0.0.0.0:6667/chat/"

def respond(message, history):
    """
    参数：
    message: 用户此次输入的消息
    history: 历史聊天记录，比如 [["use input 1", "assistant output 1"],["user input 2", "assistant output 2"]]
    返回值：输出的内容
    """
    query = {"text": message}
    response = requests.post(url, json=query)
    if response.status_code == 200:
        result = response.json()
        print("BOT:", result["result"])
        return result["result"]
    else:
        print("Error:", response.status_code, response.text)
        return "ERROR"

gr.ChatInterface(respond).launch()