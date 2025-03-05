import time
import requests
from collections import defaultdict
import concurrent.futures

API_URL = "http://localhost:80/v1/completions"
PROMPT = "结合给定的材料，介绍下黑洞：\n黑洞是一种类星体，就像一个理想的黑体，它不反光，且有着极大的引力，以致形成所有的粒子与光等电磁辐射都不能逃逸的区域。\n\n广义相对论预测，足够紧密的质量可以扭曲时空形成黑洞[9][10]；不可能从该区域逃离的边界称为事件视界。虽然事件视界对穿越它的物体的命运和情况有巨大影响，但对该地区的观测似乎未能探测到任何特征[11]。此外，弯曲时空中的量子场论预测，事件视界发出的霍金辐射，如同黑体的光谱一样，可以用来测量与质量反比的温度。恒星质量的黑洞，温度往往在数十亿分之一K，因此基本上无法观测到。\n\n最早在18世纪，约翰·米歇尔和皮耶-西蒙·拉普拉斯就考虑过引力场强大到光线都无法逃逸的物体[12]。1916年，卡尔·史瓦西发现了第一个能用来表征黑洞的广义相对论精确解（也就是史瓦西黑洞），然而大卫·芬克尔斯坦在1958年才首次发表史瓦西解做为一个无法逃脱空间区域的解释。长期以来，黑洞一直被认为仅仅来自数学上的好奇。在20世纪60年代，理论工作显示这是广义相对论的一般预测。约瑟琳·贝尔·伯奈尔在1967年发现中子星，激发了人们引力坍缩形成的致密天体可能是天体物理中的实体的兴趣。\n\n预期恒星质量的黑洞会在恒星的生命周期结束的坍塌时形成。黑洞形成后，它可以经由吸收周边的物质来继续生长。透过吸收其它恒星并与其它黑洞合并，可能形成数百万太阳质量（M☉）的超大质量黑洞。人们一致认为，大多数星系的中心都存在着超大质量黑洞。\n\n黑洞的存在可以透过它与其它物质和电磁辐射（如可见光）的相互作用推断出来。落在黑洞上的物质会因为摩擦加热而在黑洞的两极产生明亮的X射线喷流。吸积物质在落入黑洞前围绕黑洞以接近光速的速度旋转，并形成包裹黑洞的扁平吸积盘，成为宇宙中最亮的一些天体。如果有其它恒星围绕着黑洞运行，它们的轨道可以用来确定黑洞的质量和位置。这种观测可以排除其它可能的天体，例如中子星。经由这种方法，天文学家在许多联星系统确认了黑洞候选者，并确定银河系核心被称为人马座A*的电波源包含一个超大质量黑洞，其质量大约是430万太阳质量。\n\n2016年2月11日，LIGO科学合作组织和Virgo合作组宣布第一次直接观测到引力波，这也代表第一次观测到黑洞合并[14]。迄2018年12月，已经观测到11件引力波事件，其中10件是源自黑洞合并，只有1件是中子星碰撞。"  # 测试Prompt
CONCURRENCY = 10  # 并发请求数量
OUTPUT_TOKENS = 100  # 每次输出多少token
REQUEST_COUNT = 200  # 发起的请求数

def send_request():
    try:
        payload = {
            "model": "your_model_name",
            "prompt": PROMPT,
            "max_tokens": OUTPUT_TOKENS,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        start_time = time.time()
        response = requests.post(API_URL, json=payload)
        end_time = time.time()
        
        latency = end_time - start_time
        result = response.json()
        if "error" in result:
            return {"error": result["error"]}
        
        # 统计tokens相关数据
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        if completion_tokens == 0:
            return None  # 说明生成有问题，丢弃
        
        tokens_per_second = completion_tokens / latency
        
        return {
            "tokens_per_second": tokens_per_second,
            "total_latency": latency,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    start_time = time.time()
    results = []
    success_count = 0
    error_count = 0
    error_types = defaultdict(int)

    # 创建固定数量的请求
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        # 提交固定数量的请求
        futures = [executor.submit(send_request) for _ in range(REQUEST_COUNT)]
        
        # 等待所有请求完成
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if not result:
                error_count +=1
                continue
                
            if "error" in result:
                error_count +=1
                error_types[result["error"]] +=1
            else:
                success_count +=1
                results.append(result)
                
    total_duration = time.time() - start_time

    # 汇总统计
    total_prompt_tokens = sum(r["prompt_tokens"] for r in results)
    total_completion_tokens = sum(r["completion_tokens"] for r in results)
    total_tokens = total_prompt_tokens + total_completion_tokens
    if results:
        avg_latency = sum(r["total_latency"] for r in results) / len(results)
    else:
        avg_latency = 0
    avg_token_latency = sum(r["total_latency"] for r in results) / total_completion_tokens

    tokens_per_second = total_completion_tokens / total_duration 
    qpm = len(results) / total_duration * 60

    # 输出结果
    print(f"总共处理请求数: {REQUEST_COUNT}")
    print(f"成功请求: {success_count}/{REQUEST_COUNT} ({success_count/REQUEST_COUNT:.2%})")
    print(f"并发数: {CONCURRENCY}")
    print(f"总耗时: {total_duration:.2f} s")
    print(f"总Prompt Tokens: {total_prompt_tokens}")
    print(f"总Output Tokens: {total_completion_tokens}")
    print(f"QPM: {qpm}")
    print(f"请求平均耗时: {avg_latency * 1000:.2f} ms")
    print(f"生成Tokens 平均时延: {avg_token_latency * 1000:.2f} ms")
    print(f"生成Tokens 总吞吐: {tokens_per_second:.2f} tokens/s")
    print(f"错误类型分布: {dict(error_types)}")

if __name__ == "__main__":
    main()
