import litellm
import os
from dotenv import load_dotenv
load_dotenv()
def chat_completion(provider,model, messages,stream=False,api_base=None,api_key=None,**kwargs):
    if api_key is None:
        api_key=os.environ.get(provider.upper()+"_API_KEY")
    if api_base is None:
        api_base=os.environ.get(provider.upper()+"_API_BASE")

    response=litellm.completion(
        model='openai/'+model,
        messages=messages,
        api_key=api_key,
        api_base=api_base,
        stream=stream,
        **kwargs
    )
    #print(response)
    if stream:
        result = {"content": "", "function_call": None}
        for chunk in response:
            # 处理普通文本内容
            #print(chunk.choices[0].delta)
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                result["content"] += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="", flush=True)
            
            # 处理函数调用
            if hasattr(chunk.choices[0].delta, 'function_call'):
                if result["function_call"] is None:
                    result["function_call"] = {"name": "", "arguments": ""}
                
                if hasattr(chunk.choices[0].delta.function_call, 'name'):
                    result["function_call"]["name"] = chunk.choices[0].delta.function_call.name
                
                if hasattr(chunk.choices[0].delta.function_call, 'arguments'):
                    result["function_call"]["arguments"] += chunk.choices[0].delta.function_call.arguments
                    print(chunk.choices[0].delta.function_call.arguments, end="", flush=True)
        
        #print('result:',result)
        # 如果没有函数调用，只返回内容
        if result["function_call"] is None or result["function_call"]["name"] == "":
            return result["content"]
        return result
    else:
        # 如果包含 function call，返回完整响应
        if kwargs.get("function_call",False) and hasattr(response.choices[0].message, 'function_call'):
            return {
                "content": response.choices[0].message.content,
                "function_call": {

                    "name": response.choices[0].message.function_call.name,
                    "arguments": response.choices[0].message.function_call.arguments
                }
            }
        # 否则只返回内容
        return response.choices[0].message.content


def get_doubao_endpoint(model):
    if model.startswith("doubao_"):
        doubao_model_map={
                "doubao_pro_character": "ep-20250112231511-cn92j",
                "doubao_lite_character": "ep-20250112231419-pz8kt",
                "doubao_pro_128k": "ep-20250112232114-zcdx9",
                "doubao_pro_256k": "ep-20250112231129-sjxbt",
                "doubao_pro_32k": "ep-20250112231309-8wgq7",
                "doubao_lite_128k": "ep-20250112231536-92whg",
                "doubao_lite_32k": "ep-20250112231053-mtlp9",
                "doubao_1.5_pro":"ep-20250131101753-mjj2s",
                "doubao_deepseek_v3":"ep-20250207135528-qwcz2",
                "doubao_deepseek_r1":"ep-20250207135505-9smcv"
            }
        if model not in doubao_model_map:
            raise ValueError(f"Unknown model: {model}")
        return doubao_model_map[model]
    else:
        return model


def get_spark_key(model):
    if model=="Lite":
        return os.environ.get("SPARK_LITE_API_KEY")
    elif model=="Pro":
        return os.environ.get("SPARK_PRO_API_KEY")
    elif model=="Pro-128k":
        return os.environ.get("SPARK_PRO_128K_API_KEY")
    elif model=="generalv3.5":
        return os.environ.get("SPARK_GENERALV3_5_API_KEY")
    elif model=="Max-32k":
        return os.environ.get("SPARK_MAX_32K_API_KEY")
    elif model=="4.0Ultra":
        return os.environ.get("SPARK_4_0_ULTRA_API_KEY")
    else:
        raise ValueError(f"Unknown model: {model}")

## 根据模型名称猜测提供商
def guess_provider(model):
    if "doubao" in model or model in ["deepseek-r1-distill-qwen-32b-250120","doubao-1-5-lite-32k-250115",
                                      "doubao-1-5-pro-32k-250115","doubao-1-5-pro-256k-250115",
                                      "deepseek-r1-distill-qwen-7b-250120","deepseek-v3-241226",
                                      "deepseek-r1-250120"]:
        return "doubao"
    elif model in ["Lite","Pro","Pro-128k","generalv3.5","Max-32k","4.0Ultra"]:
        return "spark"
    elif model in ["deepseek-chat","deepseek-coder","deepseek-reasoner"]:
        return "deepseek"
    elif model in ["gpt-4o","gpt-4o-mini","Meta-Llama-3.1-8B-Instruct","Llama-3.3-70B-Instruct","Mistral-large-2407","Mistral-Nemo","Phi-3.5-MoE-instruct","Codestral-2501","Meta-Llama-3.1-405B-Instruct","Phi-4"]:
        return "github"
    elif model in ["open-codestral-mamba","open-mistral-nemo","pixtral-12b-2409","mistral-small-latest","ministral-8b-latest","pixtral-large-latest","mistral-large-latest","codestral-latest"]:
        return "mistral"
    elif "glm" in model:
        return "zhipu"
    elif "hunyuan" in model:
        return "hunyuan"
    elif "gpt" in model or "o1" in model or "o3" in model:
        return "openai"
    elif "claude" in model:
        return "anthropic"
    elif "/" in model:
        return "openrouter"
    elif "qwen" in model:
        return "qwen"
    elif model in["MiniMax-Text-01","abab6.5s-chat"]:
        return "minimax"
    elif "moonshot" in model:
        return "kimi"
    elif "gemini" in model:
        return "google"
    else:
        raise ValueError(f"Unknown model: {model}")

## 对doubao等模型进行特殊处理
def chat(model, messages,stream=False,api_base=None,api_key=None,**kwargs):
    provider=guess_provider(model)
    #print(f"provider: {provider}")
    if provider=="doubao":
        endpoint=get_doubao_endpoint(model)
        return chat_completion(provider,endpoint,messages,stream,api_base,api_key,**kwargs)
    
    elif provider=="spark":
        api_key=get_spark_key(model)
        api_base=os.environ.get("SPARK_API_BASE")
        #print(f"api_key: {api_key}")
        #print(f"api_base: {api_base}")
        return chat_completion(provider,model,messages,stream,api_base,api_key,**kwargs)
    else:
        return chat_completion(provider,model,messages,stream,api_base,api_key,**kwargs)

def chat_stream(model, messages,stream=True,api_base=None,api_key=None,**kwargs):
    from openai import OpenAI
    provider=guess_provider(model)
    if provider=="doubao":
        model=get_doubao_endpoint(model)

    if provider=="spark":
        api_key=get_spark_key(model)
        api_base=os.environ.get("SPARK_API_BASE")
    else:
        api_key=os.environ.get(provider.upper()+"_API_KEY")
        api_base=os.environ.get(provider.upper()+"_API_BASE")

    print(f"api_base: {api_base}")
    print(f"api_key: {api_key}")
    client = OpenAI(
        base_url=api_base,
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        extra_body={},
        model=model,
        messages=messages,
        stream=stream,
        **kwargs
    )
    

    for chunk in completion:
        if (len(chunk.choices)>0 and
            hasattr(chunk.choices[0].delta, 'content') and 
            chunk.choices[0].delta.content is not None):
            print(chunk.choices[0].delta.content)
            yield chunk.choices[0].delta.content

async def chat_async(model, messages,api_base=None,api_key=None,**kwargs):
    from openai import AsyncOpenAI
    import time
    provider=guess_provider(model)
    if provider=="doubao":
        model=get_doubao_endpoint(model)

    if provider=="spark":
        api_key=get_spark_key(model)
        api_base=os.environ.get("SPARK_API_BASE")
    else:
        api_key=os.environ.get(provider.upper()+"_API_KEY")
        api_base=os.environ.get(provider.upper()+"_API_BASE")

    client = AsyncOpenAI(
        base_url=api_base,
        api_key=api_key,
    )
    
    start_time = time.time()
    try:
        completion = await client.chat.completions.create(
            extra_body={},
            model=model,
            messages=messages,
            stream=False,
            **kwargs
        )
        content=completion.choices[0].message.content
    except Exception as e:
        return {
            "latency":0,
            "tokens":0,
            "tokens_per_second":0,
            "response":"error",
            "usage":{
                "prompt_tokens":0,
                "completion_tokens":0,
                "total_tokens":0
            },
            "status":str(e)
        }
    try:
        output_token=completion.usage.completion_tokens
        latency=time.time()-start_time
        usage=completion.usage
        
    except Exception as e:
        output_token=0
        latency=0
        usage={
            "prompt_tokens":0,
            "completion_tokens":0,
            "total_tokens":0
        }

    return {
        "latency":latency,
        "tokens":output_token,
        "tokens_per_second":output_token / latency,
        "response":content,
        "usage":usage,
        "status":"success"
    }


def set_multimodal_messages(image_path,instruction,system_prompt=""):
    import base64
    with open(image_path, 'rb') as img_file:
        img_base = base64.b64encode(img_file.read()).decode('utf-8')
    messages=[
        {"role":"system","content":system_prompt},
        {"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"{img_base}"}},
            {"type":"text","text":instruction}
        ]}
    ]
    return messages

def describe_image(model,image_path,stream=False,api_base=None,api_key=None,**kwargs):
    system_prompt="你是一个专业的图像描述师，请尽可能细致地描述这张图片的内容。"
    instruction="描述这张图片"
    messages=set_multimodal_messages(image_path,instruction,system_prompt)
    return chat(model,messages,stream,api_base,api_key,**kwargs)


def chat_reasoner(model,messages,stream=False,api_base=None,api_key=None,**kwargs):
    from openai import OpenAI
    provider=guess_provider(model)
    if provider=="doubao":
        model=get_doubao_endpoint(model)

    if provider=="spark":
        api_key=get_spark_key(model)
        api_base=os.environ.get("SPARK_API_BASE")
    else:
        api_key=os.environ.get(provider.upper()+"_API_KEY")
        api_base=os.environ.get(provider.upper()+"_API_BASE")


    client = OpenAI(
        base_url=api_base,
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        extra_body={},
        model=model,
        messages=messages,
        stream=stream,
        **kwargs
    )
    if stream:
        yield "<think>\n"
        print('----思考中----')
        flag='thinking'
        for chunk in completion:
            #print(chunk.choices[0].delta)
            if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content is not None:
                #reason+=chunk.choices[0].delta.reasoning_content
                yield chunk.choices[0].delta.reasoning_content
                print(chunk.choices[0].delta.reasoning_content,end="",flush=True)
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                if flag=='thinking':
                    yield "\n</think>"
                    print('----思考结束----')
                    flag='response'
                #response += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content,end="",flush=True)
        #return reason+response
    else:
        if hasattr(completion.choices[0].message, 'reasoning_content') and completion.choices[0].message.reasoning_content is not None:
            return "<think>\n"+completion.choices[0].message.reasoning_content+"</think>"+completion.choices[0].message.content
        else:
            return completion.choices[0].message.content

__all__=["chat","describe_image","set_multimodal_messages","chat_reasoner","guess_provider","chat_async"]

if __name__ == '__main__':
    for x in chat_stream("gpt-4o-mini", [{"role": "user", "content": "你好"}]):
        print(x)