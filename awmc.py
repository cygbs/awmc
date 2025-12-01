print("开始导入所需库……")
import os
import time
import requests
from urllib.parse import unquote
from 库 import PSNR方法计算差异 as PSNR
print("完成导入。")

群号= 737461713

def is_image_message(message):
    """
    检查消息是否为图片消息
    """
    if not isinstance(message, dict):
        return False
    
    # 方法1: 检查message字段中的类型
    if 'message' in message and isinstance(message['message'], list):
        for msg_part in message['message']:
            if msg_part.get('type') == 'image':
                return True
    
    # 方法2: 检查raw_message字段中是否包含图片CQ码
    if 'raw_message' in message and isinstance(message['raw_message'], str):
        if '[CQ:image' in message['raw_message']:
            return True
    
    return False

def get_last_group_message():
    url = "http://192.168.31.248:3000/get_group_msg_history"
    params = {
        "group_id": 群号
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # 解析JSON响应
        data = response.json()
        
        # 获取消息列表
        messages = data.get('data', {}).get('messages', [])
        
        if messages:
            last_message = messages[-1]  # 获取最后一条消息
            print("最后一条消息:", last_message)
            
            # 检查是否为图片消息
            if is_image_message(last_message):
                print("这是一条图片消息")
                # 提取图片信息
                image_info = extract_image_info(last_message)
                if image_info:
                    print("图片信息:", image_info)
            else:
                print("这不是图片消息")
                
            return last_message
        else:
            print("消息列表为空")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return None
    except KeyError as e:
        print(f"数据格式错误，未找到对应字段: {e}")
        return None

def send_reply_message(group_id, reply_message_id, message_content):
    """
    发送回复消息到指定群组
    
    参数:
        group_id: 群组ID
        reply_message_id: 要回复的消息ID
        message_content: 消息内容
    
    返回:
        bool: 发送成功返回True，失败返回False
    """
    url = "http://192.168.31.248:3000/send_group_msg"
    
    # 构建回复消息格式
    message = f"[CQ:reply,id={reply_message_id}]{message_content}"
    
    params = {
        "group_id": group_id,
        "message": message
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, params=params)
        response.raise_for_status()  # 如果请求失败则抛出异常
        
        # 解析JSON响应
        result = response.json()
        
        # 检查返回状态
        if result.get("status") == "ok" and result.get("retcode") == 0:
            print(f"消息发送成功! 消息ID: {result.get('data', {}).get('message_id')}")
            return True
        else:
            print(f"消息发送失败: {result.get('message', '未知错误')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return False
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"发送消息时出现未知错误: {e}")
        return False

def extract_image_info(message):
    """
    从图片消息中提取图片信息
    """
    if not is_image_message(message):
        return None
    
    image_info = {}
    
    # 从message字段提取
    if 'message' in message and isinstance(message['message'], list):
        for msg_part in message['message']:
            if msg_part.get('type') == 'image':
                image_info.update(msg_part.get('data', {}))
                break
    
    # 如果message字段没有，尝试从raw_message解析
    if not image_info and 'raw_message' in message:
        raw_msg = message['raw_message']
        if '[CQ:image' in raw_msg:
            # 简单解析CQ码
            import re
            cq_match = re.search(r'\[CQ:image,(.*?)\]', raw_msg)
            if cq_match:
                params_str = cq_match.group(1)
                params = {}
                for param in params_str.split(','):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value
                image_info.update(params)
    
    # 添加发送者信息
    if 'sender' in message:
        image_info['sender'] = {
            'user_id': message['sender'].get('user_id'),
            'nickname': message['sender'].get('nickname'),
            'card': message['sender'].get('card')
        }
    
    return image_info

def get_average_confidence(model_path, image_path):
    """
    计算图片中所有检测对象的平均置信度
    
    参数:
        model_path: 训练好的模型路径
        image_path: 要检测的图片路径
    
    返回:
        float: 所有检测对象的平均置信度，如果没有检测到对象则返回0.0
    """
    # 加载模型
    model = YOLO(model_path)
    
    # 进行推理
    results = model(image_path)
    
    # 获取所有检测框的置信度
    all_confidences = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            # 提取所有置信度
            confidences = boxes.conf.tolist()
            all_confidences.extend(confidences)
    
    # 计算平均置信度
    if all_confidences:
        avg_confidence = sum(all_confidences) / len(all_confidences)
        print(f"检测到 {len(all_confidences)} 个对象，平均置信度: {avg_confidence:.4f}")
        return avg_confidence
    else:
        print("未检测到任何对象")
        return 0.0

def download_image(url, filename):
    """
    下载图片到指定目录
    
    参数:
        url: 图片URL
        filename: 保存的文件名
    
    返回:
        str: 下载的图片路径，如果下载失败则返回None
    """
    try:
        # 创建下载目录
        os.makedirs('./downloads', exist_ok=True)
        
        # 下载图片
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 保存图片
        filepath = os.path.join('./downloads', filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"图片已下载: {filepath}")
        return filepath
    except Exception as e:
        print(f"下载图片失败: {e}")
        return None

def extract_image_url(message):
    """
    从消息中提取图片URL
    
    参数:
        message: 消息字典
    
    返回:
        tuple: (图片URL, 文件名) 或 (None, None)
    """
    try:
        # 从message字段提取
        if 'message' in message and isinstance(message['message'], list):
            for msg_part in message['message']:
                if msg_part.get('type') == 'image':
                    data = msg_part.get('data', {})
                    url = data.get('url')
                    filename = data.get('file', 'unknown.jpg')
                    return url, filename
        
        # 从raw_message中解析
        if 'raw_message' in message:
            raw_msg = message['raw_message']
            if '[CQ:image' in raw_msg:
                import re
                cq_match = re.search(r'\[CQ:image,(.*?)\]', raw_msg)
                if cq_match:
                    params_str = cq_match.group(1)
                    params = {}
                    for param in params_str.split(','):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            params[key] = value
                    
                    url = params.get('url')
                    filename = params.get('file', 'unknown.jpg')
                    return url, filename
        
        return None, None
    except Exception as e:
        print(f"提取图片URL失败: {e}")
        return None, None

if __name__ == "__main__":
    # 记录已处理的消息ID，避免重复处理
    processed_messages = set()
    
    # 模型路径 - 请根据实际情况修改
    model_path = "/home/ygbs/文档/YOLO/runs/detect/wmc/weights/best.pt"  # 替换为实际的模型路径
    
    print("开始监控群消息...")
    
    while True:
        try:
            # 获取历史消息
            last_msg = get_last_group_message()
            
            if last_msg and last_msg.get('message_id') not in processed_messages:
                message_id = last_msg.get('message_id')
                processed_messages.add(message_id)
                
                # 检查是否为图片消息
                if is_image_message(last_msg):
                    print("检测到新图片消息，开始处理...")
                    
                    # 提取图片URL和文件名
                    image_url, filename = extract_image_url(last_msg)
                    
                    if image_url:
                        # 解码URL（如果有编码）
                        image_url = unquote(image_url)
                        
                        # 下载图片
                        local_path = download_image(image_url, filename)

                        图片1, 图片2 = PSNR.加载并统一尺寸("test.jpeg", local_path)
                        
                        if local_path and os.path.exists(local_path):
                            # 相似度
                            avg_confidence = PSNR.计算峰值信噪比(图片1, 图片2)
                            
                            print(f"图片检测完成，相似度: {avg_confidence}")
                            
                            # 如果相似度超过11，打印信息
                            if avg_confidence > 11:
                                sender_name = last_msg.get('sender', {}).get('nickname', '未知用户')
                                print(f"🚨 高置信度检测! 置信度: {avg_confidence}")
                                print(f"   发送者: {sender_name}")
                                print(f"   图片文件: {filename}")
                                print(f"    ID: {message_id}")
                                success = send_reply_message(
                                    group_id=群号,
                                    reply_message_id=message_id,
                                    message_content="awmc! "+str(avg_confidence)
                                )
                                if success:
                                    print("回复消息发送成功!")
                                else:
                                    print("回复消息发送失败!")
                        else:
                            print("图片下载失败，跳过处理")
                    else:
                        print("无法提取图片URL，跳过处理")
                else:
                    print("最新消息不是图片，跳过处理")
            else:
                print("没有新消息或消息已处理")
            
            # 等待一段时间后再次检查（例如1秒）
            print("等待1秒后继续检查...")
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"处理过程中出现错误: {e}")
            print("等待10秒后重试...")
            time.sleep(10)
