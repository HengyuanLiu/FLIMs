import os
import json
import re
def extract_json_blocks(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 正则匹配所有 {} 包裹的内容（包括嵌套的 {}）
        json_blocks = re.findall(r'\{[^{}]*\}', content)
        
        # 如果需要更精确的匹配（避免嵌套 {} 的问题），可以用更复杂的正则
        # 但简单场景下，上面的正则已经足够
        return json_blocks
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def write_noise_mutants_to_file(numbers_set, output_file_path):
    """
    将编号集合写入txt文件，编号用英文逗号隔开。

    Args:
        numbers_set (set): 包含编号的集合。
        output_file_path (str): 输出txt文件的路径。
    """
    try:
        # 将集合转换为排序后的列表并用逗号连接成字符串
        numbers_string = ", ".join(map(str, sorted(numbers_set)))
        
        # 将结果写入文件
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(numbers_string)
       # print(f"结果已写入文件: {output_file_path}")
    except Exception as e:
        print(f"error: {e}")


buggy = {
         'Chart': 26,
        'Math': 107,
        'Lang': 66,               
        'Mockito': 38,
         'Time': 26,
        #  'Closure':134
    }
for bug, bugnumber in buggy.items():
    for num in range(1,6):
        for idex in range(1, bugnumber + 1):
            print(f"{bug}_{idex}")
            try:
                file_path = rf'results/llm_output/output{num}/{bug}/{bug}_{idex}_mutants.json'
            out_file=rf'results/flim_recognition/output{num}/{bug}/{bug}_{idex}.txt'  # Output file path for FLIM recognition results
                directory = os.path.dirname(out_file)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                result = extract_json_blocks(file_path)
                flrm=[]
                for line in result:
                    try:
                        kk=json.loads(line)
                        # print(kk['mutant_id'])
                        # print(kk['is_flim'])
                        if kk['is_flim']==True:
                            flrm.append(kk['mutant_id'])
                    except:
                        pass
                # print(flrm)
                write_noise_mutants_to_file(flrm, out_file)
                print(f"{bug}-{idex}b complete")


            except:
                pass


