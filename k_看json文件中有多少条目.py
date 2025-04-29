import json

def count_json_entries(file_path):
    try:
        # 打开并读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 检查数据是否为列表
        if isinstance(data, list):
            return len(data)
        else:
            return "JSON文件内容不是一个数组"
    
    except FileNotFoundError:
        return "文件未找到"
    except json.JSONDecodeError:
        return "文件不是有效的JSON格式"

# 使用示例
file_path = 'stocks/DrMattDrMike.json'  # 替换为你的JSON文件路径
entry_count = count_json_entries(file_path)
print(f"JSON文件中的条目数量: {entry_count}")
