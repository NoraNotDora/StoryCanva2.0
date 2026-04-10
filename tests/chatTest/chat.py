import requests # 导入requests库用于发送HTTP请求
import os # 导入os库，用于访问环境变量

# server.py 提供的Qiaoban API地址 (用于最终生成回复)
QIAOBAN_API_URL = "http://localhost:6667/chat/"

# Flask 应用提供的图像生成 API 地址
IMAGE_GENERATION_API_URL = "http://localhost:5000/generate-image" # Flask 应用通常运行在 5000 端口

# 模拟一个意图识别函数，实际中应调用模型 API
def recognize_intent(user_input: str) -> str:
    """
    使用 Prompt A 调用模型判断用户输入是否需要生成图像。
    返回 "yes" 或 "no"。
    """
    # Prompt A: 小朋友说{input}, 判断小朋友是否需要生成图像, 如果需要输出"yes", 不需要输出"no"。
    intent_prompt = f"小朋友说{user_input}, 判断小朋友是否需要生成图像, 如果需要输出\"yes\", 不需要输出\"no\"。"

    print(f"\n[意图识别] 使用 Prompt A 进行意图判断: {intent_prompt}")

    try:
        # 调用Qiaoban API进行意图判断
        # 注意：这里的Qiaoban API (backend/Qiaoban/server.py) 是通用的聊天模型，
        # 它的设计可能不适合进行严格的 yes/no 意图判断。
        # 实际应用中，可能需要更专业的意图识别服务或微调过的模型。
        response = requests.post(QIAOBAN_API_URL, json={
            "text": intent_prompt, # Qiaoban API 接收 'text' 字段
            #"max_length": 10  # Qiaoban API 可能不支持 max_length 参数，需确认
        }, timeout=10)

        response.raise_for_status()
        result = response.json()

        # 获取模型返回的文本
        # Qiaoban API 返回的是 {"result": "..."}
        model_response = result.get("result", "").lower().strip()

        # 判断是否包含"yes"
        is_yes = "yes" in model_response

        print(f"[意图识别] 模型返回: {model_response}")
        print(f"[意图识别] 判断结果: {'yes' if is_yes else 'no'}")

        return "yes" if is_yes else "no"

    except Exception as e:
        print(f"[意图识别] API调用失败: {e}")
        return "no"  # 发生错误时默认不生成图像


# 调用图像素材生成函数，实际中调用 Flask 后端提供的 API
def generate_image_material(description: str):
    """
    调用 Flask 后端提供的 /generate-image API 生成图像素材。
    实际中，这里可能需要使用 Prompt B 重新描述输入并调用图像生成函数。
    """
    # 调用Qiaoban API进行内容检查和重新描述 (使用 Prompt B 的逻辑)
    safety_prompt = f"小朋友的描述:{description} 我需要检查一下里面是否包含有害信息, 并重新描述需要生成的图像素材, 以生成实体为主。"

    try:
        # 再次调用Qiaoban API处理描述
        # 注意：同样需要确认Qiaoban API是否适合做这种描述处理
        response = requests.post(QIAOBAN_API_URL, json={
            "text": safety_prompt, # Qiaoban API 接收 'text' 字段
            #"max_length": 200  # Qiaoban API 可能不支持 max_length 参数，需确认
        }, timeout=10)

        response.raise_for_status()
        result = response.json()
        processed_description = result.get("result", "").strip() # Qiaoban API 返回的是 {"result": "..."}

        if not processed_description:
            print("[内容处理] 模型返回为空，使用原始描述")
            processed_description = description # 如果模型没有返回有效内容，使用原始描述

        print(f"[内容处理] 处理后的描述: {processed_description}")

    except Exception as e:
        print(f"[内容处理] API调用失败: {e}。使用原始描述进行图像生成。")
        processed_description = description # 处理描述失败时使用原始描述

    # --- 开始调用图像生成 API 并添加重试 ---
    print(f"\n[图像生成] 调用 Flask API 进行图像生成，描述: {processed_description}")

    max_retries = 3  # 最大重试次数
    retry_delay_seconds = 5 # 重试间隔时间

    for attempt in range(max_retries):
        try:
            # 准备请求数据
            payload = {"prompt": processed_description} # Flask API 期望prompt字段

            # 发送POST请求到图像生成 API
            # timeout可以根据实际情况调整，图像生成可能比较耗时
            response = requests.post(IMAGE_GENERATION_API_URL, json=payload, timeout=120)

            # 检查响应状态码
            response.raise_for_status() # 如果状态码不是2xx，会抛出HTTPError异常

            # 解析JSON响应
            result = response.json()

            # 检查API是否成功并获取图片URL
            if result.get("success"):
                image_url = result.get("image_url")
                if image_url:
                    print(f"[图像生成] 生成成功，图片URL: {image_url}")
                    return image_url # 返回生成的图片URL
                else:
                    print("[图像生成] API返回成功，但未找到image_url字段。")
                    return None # 生成失败 (API成功但响应格式不对)
            else:
                error_message = result.get("error", "未知错误")
                print(f"[图像生成] API返回失败: {error_message}")
                # 如果API明确返回失败（例如 Prompt 包含违禁词），可能不适合重试
                # 这里假设API返回失败是模型内部问题，可以考虑重试，或者根据错误类型决定
                # 当前实现是遇到任何HTTPError都退出重试
                return None # 生成失败 (API明确返回失败)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"[图像生成] 请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"[图像生成] 等待 {retry_delay_seconds} 秒后重试...")
                import time
                time.sleep(retry_delay_seconds)
            else:
                print(f"[图像生成] 达到最大重试次数，放弃。")
                return None # 生成失败 (重试后仍然连接/超时错误)
        except requests.exceptions.HTTPError as e:
             # HTTP 4xx 或 5xx 错误，通常表示请求有问题或服务器内部错误，不进行重试
            print(f"[图像生成] HTTP请求失败: {e}")
            return None # 生成失败 (HTTP错误)
        except Exception as e:
            print(f"[图像生成] 发生未知错误 during image generation API call: {e}")
            return None # 生成失败 (其他未知错误)

    # 如果循环结束（即重试耗尽），返回 None
    return None

def chat_stream(model, messages, stream=False, api_base=None, api_key=None, **kwargs):
    # 从messages列表中提取最新的用户消息
    # 假设messages列表的最后一个元素是当前用户的输入
    user_message = ""
    if messages and isinstance(messages[-1], dict) and messages[-1].get("role") == "user":
         # 处理content可能是字符串或列表的情况
         content = messages[-1].get("content")
         if isinstance(content, str):
             user_message = content
         elif isinstance(content, list):
             # 如果content是列表，找到type为"text"的内容
             for item in content:
                 if isinstance(item, dict) and item.get("type") == "text":
                     user_message = item.get("text", "")
                     break # 找到第一个文本内容就足够了

    if not user_message:
        print("警告: chat_stream 未收到有效的用户输入。")
        return "无法处理您的请求，请提供有效的文本输入。"

    is_img_gen = kwargs.get("is_img_gen", False)
    # 将历史记录转换为适合Prompt C的格式（例如简单拼接）
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in kwargs.get("history", [])])
    is_story_end = kwargs.get("is_story_end", False)

    response_prompt = f"""图像是否生成:{is_img_gen}
历史聊天记录:
{history_text}
故事是否结束:{is_story_end}
继续引导小朋友进行故事创作。
用户输入: {user_message}"""

    # --------------------------------------------------------------
    # 调用 Qiaoban API 生成回复 (添加重试机制)
    print(f"\n[生成回复] 调用本地 Qiaoban API 生成回复，用户输入: {user_message}")

    max_retries = 3  # 最大重试次数
    retry_delay_seconds = 5 # 重试间隔时间

    for attempt in range(max_retries):
        try:
            # 准备请求数据 (只发送当前用户输入给Qiaoban API)
            payload = {"text": user_message}

            # 发送POST请求到Qiaoban API
            # timeout参数可以防止请求无限期等待
            response = requests.post(QIAOBAN_API_URL, json=payload, timeout=60)

            # 检查响应状态码
            response.raise_for_status() # 如果状态码不是2xx，会抛出HTTPError异常

            # 解析JSON响应
            result = response.json()

            # 返回result字段的内容
            response_text = result.get("result", "API响应格式错误")
            print(f"[生成回复] API返回结果 (尝试 {attempt + 1}/{max_retries}): {response_text}")
            return response_text # 成功获取回复，退出循环并返回

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"[生成回复] 请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"[生成回复] 等待 {retry_delay_seconds} 秒后重试...")
                import time
                time.sleep(retry_delay_seconds)
            else:
                print(f"[生成回复] 达到最大重试次数，放弃。")
                # 返回重试失败的提示
                return "服务器连接失败，请确认 Qiaoban server 是否正在运行，并稍后再试。"
        except requests.exceptions.HTTPError as e:
             # HTTP 4xx 或 5xx 错误，通常表示请求有问题或服务器内部错误，不进行重试
            print(f"[生成回复] HTTP请求失败: {e}")
            return f"API请求失败: {e}" # 返回HTTP错误信息
        except Exception as e:
            print(f"[生成回复] 发生未知错误 during Qiaoban API call: {e}")
            return f"发生未知错误: {e}" # 返回未知错误信息


# 新增的处理用户输入并根据意图决定流程的函数
def process_user_input_with_intent(user_input: str, chat_history: list):
    """
    处理用户输入，进行意图识别，并根据意图生成回复或图像。
    """
    print(f"\n[主流程] 接收到用户输入: {user_input}")

    # 1. 意图识别
    intent = recognize_intent(user_input)
    is_img_gen = False
    generated_image_info = None # 用于存储生成的图片信息

    # 2. 根据意图决定下一步
    if intent == "yes":
        print("[主流程] 意图为生成图像。")
        is_img_gen = True
        # 调用图像素材生成函数
        generated_image_info = generate_image_material(user_input)
        if generated_image_info:
             print("[主流程] 图像素材生成完成。")
        else:
             print("[主流程] 图像素材生成失败。")


    # 3. 生成回复 (使用 chat_stream 函数)
    # 理论上这里需要将历史记录、is_img_gen 和 is_story_end 传递给 chat_stream
    # 但由于调用的 Qiaoban API 不支持，这里只传递当前用户输入
    print("[主流程] 生成回复。")
    # 并且 chat_stream 应该使用 Prompt C 的逻辑生成回复。
    messages = chat_history + [{"role": "user", "content": user_input}] # 构建包含当前输入的完整消息列表
    # 调用 chat_stream 获取回复，并传递状态信息
    response_text = chat_stream("dummy_model", messages, is_img_gen=is_img_gen, history=chat_history, is_story_end=False) # is_story_end 需要根据故事进展判断

    print(f"[主流程] 回复生成完成: {response_text}")

    # 4. 返回结果，包括回复文本和可能的图像信息
    return {
        "response_text": response_text,
        "image_info": generated_image_info,
        "intent": intent,
        "is_img_gen_successful": is_img_gen and generated_image_info is not None # 只有意图是yes且生成成功才为True
    }


# 意图识别和图像生成相关的函数不再需要单独导出
# __all__=["chat_stream"] # 不再直接导出 chat_stream
__all__=["process_user_input_with_intent"]


# 主程序入口，用于测试
if __name__ == '__main__':
    print("测试包含意图识别的流程:")

    # 模拟对话历史
    chat_history = []

    # 测试第一次输入 (不触发图像生成)
    user_input_1 = "你好，可以给我讲个故事吗？"
    result_1 = process_user_input_with_intent(user_input_1, chat_history)
    print("\n--- 第一次交互结果 ---")
    print("回复:", result_1["response_text"])
    print("意图:", result_1["intent"])
    print("图像信息:", result_1["image_info"])
    print("是否成功生成图像:", result_1["is_img_gen_successful"])
    # 更新历史 (实际应用中，需要将用户输入和模型回复都加入历史)
    chat_history.append({"role": "user", "content": user_input_1})
    chat_history.append({"role": "assistant", "content": result_1["response_text"]})


    print("\n" + "="*20 + "\n")

    # 测试第二次输入 (触发图像生成 - 模拟的，因为输入包含"画")
    user_input_2 = "我想画一只可爱的小猫。"
    result_2 = process_user_input_with_intent(user_input_2, chat_history)
    print("\n--- 第二次交互结果 ---")
    print("回复:", result_2["response_text"])
    print("意图:", result_2["intent"])
    print("图像信息:", result_2["image_info"])
    print("是否成功生成图像:", result_2["is_img_gen_successful"])
    # 更新历史
    chat_history.append({"role": "user", "content": user_input_2})
    chat_history.append({"role": "assistant", "content": result_2["response_text"]}) # 注意：这里的回复可能没有提及图像生成


    print("\n" + "="*20 + "\n")

    # 测试第三次输入 (不触发图像生成)
    user_input_3 = "然后呢？"
    result_3 = process_user_input_with_intent(user_input_3, chat_history)
    print("\n--- 第三次交互结果 ---")
    print("回复:", result_3["response_text"])
    print("意图:", result_3["intent"])
    print("图像信息:", result_3["image_info"])
    print("是否成功生成图像:", result_3["is_img_gen_successful"])
    # 更新历史
    chat_history.append({"role": "user", "content": user_input_3})
    chat_history.append({"role": "assistant", "content": result_3["response_text"]})