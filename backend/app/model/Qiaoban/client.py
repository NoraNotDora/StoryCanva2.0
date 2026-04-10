import requests

url = "http://0.0.0.0:6667/chat/"

while True:
    usr_inp = input(">> 用户: ")
    query = {"text": usr_inp}
    response = requests.post(url, json=query)
    if response.status_code == 200:
        result = response.json()
        print("BOT:", result["result"])
    else:
        print("Error:", response.status_code, response.text)
