import json
import numbers
import pandas as pd
import os
import difflib
import re

def difflib_diff(str1, str2):#单行字符串求diff
    if str1 == str2:
        return str2
    diff = difflib.unified_diff(
        str1.splitlines(keepends=True),
        str2.splitlines(keepends=True),
        lineterm=""
    )
    return ''.join(diff)

def diff_call_stacks(stack1, stack2):#堆栈求diff
    """
    比较两个调用栈的差异（按 " at " 分割后逐层比较）
    """
    # 分割调用栈
    stack1_lines = stack1.split(" at ")
    stack2_lines = stack2.split(" at ")
    
    # 确保两个栈的层数一致（如果某层不存在，则用空字符串代替）
    max_len = max(len(stack1_lines), len(stack2_lines))
    stack1_lines += [""] * (max_len - len(stack1_lines))
    stack2_lines += [""] * (max_len - len(stack2_lines))
    
    # 逐层比较
    diffs = []
    for i, (line1, line2) in enumerate(zip(stack1_lines, stack2_lines)):
        if line1 != line2:
            # 计算差异（注意：unified_diff 需要列表输入）
            diff = difflib.unified_diff(
                [line1 + "\n"],  # 注意：unified_diff 要求每行以 \n 结尾
                [line2 + "\n"],
                lineterm="",  # 避免额外换行
                # fromfile=f"Stack1_Line_{i+1}",
                # tofile=f"Stack2_Line_{i+1}"
            )
            # diffs.append(f"=== Difference at layer {i+1} ===\n")
            diffs.append(''.join(diff))
            diffs.append("\n")  # 分隔不同层的差异
    
    return "".join(diffs) if diffs else stack2

def remove_junit_stack_trace(stack_trace):
    """
    从 Java 异常堆栈跟踪中移除所有包含 'junit' 的 'at' 行。

    参数:
        stack_trace (str): 包含堆栈跟踪的字符串。

    返回:
        str: 移除包含 'junit' 的 'at' 行后的堆栈跟踪。
    """
    lines = stack_trace.split(' at ')
    filtered_lines = []
    
    for line in lines:
        # print(line)
        if 'junit' in line:
            continue  # 跳过包含 'junit' 的 'at' 行
        # print(line)
        filtered_lines.append(line)
    
    return ' at '.join(filtered_lines)
    
def extract_killmap_data(file_path):
    try:
        # 读取压缩文件，跳过错误行
        df = pd.read_csv(
            file_path,
            compression='gzip',
            header=None,
            # error_bad_lines=False,  # 跳过格式错误的行
            on_bad_lines='skip',
            # warn_bad_lines=False     # 打印警告信息
        )
    except pd.errors.ParserError as e:
        # print(f"解析错误: {e}")
        # 可以选择重新抛出异常或返回空数据
        return {}, {}
    
    # 筛选第二列为0或num的行
    filtered_0 = df[(df[1] == 0) & (df[3] == 'FAIL')]
    # filtered_num = df[df[1] == num]
    
    # 提取第一列和第八列的值（如果列数不足，会报错）
    # 所以需要先确保列数足够
    if filtered_0.shape[1] < 8 :
        # print("警告：某些行的列数不足8列，已跳过")
        filtered_0 = filtered_0.iloc[:, :8]  # 只取前8列
        
    
    # 提取(第一列, 第八列)元组
    tuples_0 = list(zip(filtered_0[0], filtered_0[7]))
    
    return tuples_0


def mutant_killmap_data(file_path):
    try:
        # 读取压缩文件，跳过错误行
        df = pd.read_csv(
            file_path,
            compression='gzip',
            header=None,
            on_bad_lines='skip'
        )
    except pd.errors.ParserError:
        # 解析错误时返回空字典
        return {}, {}
    
    # 检查列数是否足够（至少8列）
    if df.shape[1] < 8:
        return {}, {}
    
    # 筛选出列数足够的行（确保每行至少有8列）
    filtered_df = df[df.apply(lambda row: len(row) >= 8, axis=1)]
    
    # 构建字典：键为(第一列, 第二列)，值为(第一列, 第八列)
    result_dict = {
        (row[0], row[1]): (row[0], row[7]) 
        for _, row in filtered_df.iterrows()
    }
    
    return result_dict # 返回两个字典，第二个字典留空（按原函数结构）
def add_space_after_parentheses(s):
    """
    如果字符串中有 ')' 并且不是字符串的最后一个字符，
    则在该 ')' 后面添加一个空格。

    :param s: 输入的字符串
    :return: 处理后的字符串
    """
    result = []
    i = 0
    n = len(s)
    
    while i < n:
        result.append(s[i])
        if s[i] == ')':
            # 检查是否不是最后一个字符
            if i + 1 < n:
                result.append(' ')
        i += 1
    
    return ''.join(result)

def parse_log_file(log_file_path):
    # 定义正则表达式模式来匹配你需要的部分
    # pattern = r'(\d+):.*?:.*?:.*?:(.*?):(\d+):'
    
    # 初始化结果字典
    result_dict = {}
    
    # 打开并读取日志文件
    with open(log_file_path, 'r') as file:
        # print(len(file))
        for line in file:
            line=line.split(':')
            # 使用正则表达式匹配
            # match = re.search(pattern, line)
            # if match:
                # 提取匹配的组
                # print(line)
            line_number = line[0]
            class_name = line[4].split('@')[0] + '.java'  # 提取类名并加上.java后缀
            method_line_number = line[5]
            # print()
            mutant_move=line[6].rstrip('\n')
            
            # mutant_move=add_space_after_parentheses(mutant_move)
            # print(mutant_move)
            
            # 将结果存入字典
            result_dict[line_number] = (class_name, method_line_number,mutant_move)
    
    return result_dict


def remove_before_at(input_str):
    at_index = input_str.find(" at ")  # 查找 "at" 的位置
    if at_index != -1:  # 如果找到 "at"
        return input_str[at_index:]  # 返回 "at" 及其后的部分
    return input_str

def mutant_fault(filepath):
    with open(filepath, 'r') as file:
    # 读取所有行并去除换行符
        numbers = [line.strip() for line in file]

    # 将字符串列表转换为整数列表（如果需要）
        numbers = [int(num) for num in numbers]
    return numbers



buggy = {
         'Chart': 26,
         'Math': 107,
        'Lang': 66,               
        'Mockito': 39,
        'Time': 26,
        'Closure':134
    }
for bug, bugnumber in buggy.items():
    for idex in range(1, bugnumber + 1):
        print(f"{bug}_{idex}")
        try:
            file_path1=rf'data/mbfl_data/{bug}/{idex}/killmaps/{bug}/{idex}/killmap.csv.gz'
            file_path2=rf"results/dataset-512/{bug}/{idex}/{bug}_{idex}.json"
            file_path3=rf"data/mbfl_data/{bug}/{idex}/killmaps/{bug}/{idex}/mutants.log"
            file_path4=rf"results/bug-mutant/{bug}/{bug}-{idex}.keys.txt"
            output_dir = rf"results/wt-dataset-new/{bug}"
            if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f'{bug}_{idex}.json')
            mutant_class_line=parse_log_file(file_path3)
            # print(len(mutant_class_line))
            with open(file_path2, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            result = extract_killmap_data(file_path1)
            mutanterror_dict=mutant_killmap_data(file_path1)
            numberlist=mutant_fault(file_path4)
            # print(numberlist)
            formatted_data = []
            for record in raw_data:
              try:
                record=record['input'].split('\n')
                # print(len(record))
                mutant_id=record[0].split(': ')[1]
                if int(mutant_id) in numberlist:
                    irfl='false'
                else:
                    irfl='true'

                # print(mutant_id)
                code=record[1].split(': ')[1]
                # mutant_code=record[3].split(': ')[1].split(' |==> ')
                # print(mutant_class_line[mutant_id][2])
                mutant_code=mutant_class_line[mutant_id][2].split(' |==> ')
                # print(mutant_code)
                mutant_code=difflib_diff(code,code.replace(add_space_after_parentheses(mutant_code[0]),mutant_code[1]))
                mutant_class=mutant_class_line[mutant_id][0]
                mutant_line=mutant_class_line[mutant_id][1]
                
                # print(result)
                mutant_error_message_list=[]
                new_error_message_list=[]
                for error_message in result:
                    try:
                        original_error_message=error_message[1].split(' at ')[0]  #源代码报错信息
                        original_strace=remove_before_at(error_message[1])#源代码堆栈信息
                        original_strace=remove_junit_stack_trace(original_strace)#去除junit的堆栈
            
                        new_error_message_list.append({'failtest':error_message[0],'original_error_message':original_error_message,'original_error_strace_message':original_strace})#源代码列表

                        mutanterror=mutanterror_dict[(error_message[0],int(mutant_id))]
       
                        mutant_error_message=mutanterror[1].split(' at ')[0] #变异体报错信息
                        mutant_error_message_diff=difflib_diff(original_error_message,mutant_error_message)#变异体报错信息diff
              
                        mutant_strace=remove_before_at(mutanterror[1])#变异体堆栈信息
              
                        mutant_strace=remove_junit_stack_trace(mutant_strace)#去除junit的堆栈  
                      
                        mutant_strace_diff=diff_call_stacks(original_strace,mutant_strace)#变异体报错堆栈信息diff
                        
                        mutant_error_message_list.append({'failtest':error_message[0],'mutant_error_message':mutant_error_message_diff,'mutant_error_strace_message':mutant_strace_diff})
                    except:
                        pass
                formatted_data.append({"mutant_id": mutant_id,
                                "original_code": code,
                                "test_error": new_error_message_list,
                                "mutant_code": mutant_code,
                                "mutant_class": mutant_class,
                                "line_number": mutant_line,
                                "mutation_error": mutant_error_message_list,
                                "is_flim": irfl
                                })

              except:
                  pass 
            with open(output_path, "w", encoding="utf-8") as f:
            
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            with open(r"logs/dataset-wt.log", "a") as f:
                f.write(f"{bug}_{idex} success\n")
                f.flush()
        except Exception as e:
            with open(r"logs/dataset-wt.log", "a") as f:
                f.write(f"{bug}_{idex} error: {str(e)}\n")
                f.flush()
            

       