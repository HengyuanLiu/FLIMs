import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import warnings
warnings.filterwarnings("ignore", message="Setting `pad_token_id` to `eos_token_id`:None for open-end generation.")
# 使用微调后的模型路径
model_name = "/home/wangdonghua/Qwen/deepseek-14b/deepseek-14B/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"

# 加载微调过的模型和 tokenizer，显式指定 float16 精度以启用 bitsandbytes
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="float16",  # 启用 bitsandbytes 的低精度计算
    device_map="auto"  # 自动选择设备
)

tokenizer = AutoTokenizer.from_pretrained(model_name)




buglist_dict = {
         'Chart': {'total': 26, 'start': 1},
        'Math': {'total': 107, 'start': 1},
        'Mockito': {'total': 38, 'start': 1},
        'Lang': {'total': 66, 'start': 1},
        'Time': {'total': 27, 'start': 1},
      'Closure': {'total': 134, 'start': 1},
}

for bug, info in buglist_dict.items():
    total = info['total']
    start = info['start']
    
    for i in range(start, 1 + total):
        print(f"Processing {bug}_{i}")
        # 单个文件路径
        file_path = f"/home/wangdonghua/Qwen/data/wt-dataset/{bug}/{bug}_{i}.json"

        # 用于保存噪声变异体编号的文件路径
        output_file1 = f"/home/wangdonghua/nowt/llama-8b/output1/{bug}/{bug}_{i}_mutants.json"
        output_file2 = f"/home/wangdonghua/nowt/llama-8b/output2/{bug}/{bug}_{i}_mutants.json"
        output_file3 = f"/home/wangdonghua/nowt/llama-8b/output3/{bug}/{bug}_{i}_mutants.json"
        output_file4 = f"/home/wangdonghua/nowt/llama-8b/output4/{bug}/{bug}_{i}_mutants.json"
        output_file5 = f"/home/wangdonghua/nowt/llama-8b/output5/{bug}/{bug}_{i}_mutants.json"


        # 确保输出文件的目录存在
        os.makedirs(os.path.dirname(output_file1), exist_ok=True)
        os.makedirs(os.path.dirname(output_file2), exist_ok=True) 
        os.makedirs(os.path.dirname(output_file3), exist_ok=True) 
        os.makedirs(os.path.dirname(output_file4), exist_ok=True) 
        os.makedirs(os.path.dirname(output_file5), exist_ok=True) 

        # 初始化文件写入
        with open(output_file1, "w", encoding="utf-8") as out_file1:
            with open(output_file2, "w", encoding="utf-8") as out_file2:
                with open(output_file3, "w", encoding="utf-8") as out_file3:
                    with open(output_file4, "w", encoding="utf-8") as out_file4:
                        with open(output_file5, "w", encoding="utf-8") as out_file5:
                            try:
                                # 尝试读取文件内容
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                            except (FileNotFoundError, json.JSONDecodeError):
                                continue
                            num=0
                            # 如果 data 是列表，逐条处理
                            if isinstance(data, list):
                                for entry in data:
                                    mutant_id=entry['mutant_id']
                                   
                                    Mutation_location=(entry["mutant_class"],entry["line_number"])
                                    Original_program=entry["original_code"]
                                    Original_failing_test_information=[]
                                    for Original_fail in entry["test_error"]:
                                        Original_failing_test_information.append({f"{Original_fail['failtest']}":{ "error message": Original_fail['original_error_message'], "stack trace":Original_fail['original_error_strace_message']}})
                                    #[ {testcase name}: { “error message”: error message, “stack trace”:source related stack trace, }, ... 
                                    Mutant_code_diff=entry["mutant_code"]
                                    Mutant_failing_test_information=[]
                                    for Mutant_failing in entry["mutation_error"]:
                                        Mutant_failing_test_information.append({f"{Mutant_failing['failtest']}":{ "error message diff": Mutant_failing['mutant_error_message'], "stack trace diff":Mutant_failing['mutant_error_strace_message']}})
                                        # Mutant_failing_test_information.append(r'\n')
                                    #[ {testcase name}: { “error message diff”: error message diff, “stack trace diff”: source related stack trace diff, },
                                    prompt = f'''You specialize in identifying Fault Localization-Interfering Mutants (FLIM), which deliberately avoid fixing actual faults while misleading fault localization efforts by altering test behavior or error messages. Based on the RIPR model, FLIMs primarily interfere through four key mechanisms: manipulating execution paths to bypass faults, generating derivative errors to mask primary defects, redirecting error outputs to hidden channels, and exploiting incomplete assertions to achieve false test passage. Effective analysis requires examining interference in paths, states, outputs, or assertions, verifying that test cases are killed while the underlying fault persists, and confirming that fault suspicion metrics are distorted.
                                ## Input Format
The analysis requires the following input structure:
- mutant_id (A unique identifier for the mutant): {mutant_id}
- Mutation_location(his mutant modify the class of original program at line):{Mutation_location}
- Original_program (source code element before mutation):{Original_program}
- Original_failing_test_information (An array containing test failure information for the original code):
  [testcase name (The name of the failed test case),error message (The error message from the failed test),stack trace (The full stack trace of the test failure)]
  {Original_failing_test_information}
- Mutant_code_diff (source code element diff before and after mutation):{Mutant_code_diff}
- Mutant_failing_test_information (An array containing test failure information for the mutated code):
  [testcase name (The name of the failed test case),error message diff (The error message from the failed test on the mutated code diff),stack trace diff (The full stack trace of the test failure on the mutated code diff)]
  {Mutant_failing_test_information}
## Output Format
Only return a response that can be parsed by JSON, without any other content. The format is as follows:
json
{{
    "mutant_id": {mutant_id}
    "is_flim": bool
}}
'''

                                    # 构建模型输入
                                    messages = [
                                        
                                        {"role": "user", "content": prompt}
                                    ]

                                    text = messages[1]["content"]
                                    model_inputs = tokenizer([text], return_tensors="pt", truncation=True, max_length=40960).to(model.device)

                                    # 生成文本
                                    try:
                                        generated_ids = model.generate(**model_inputs, max_new_tokens=512,do_sample=True, top_p=0.9, temperature=0.7)
                                        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
                                        response1 = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                                    except Exception:
                                        continue

                                    # 写入当前条目结果
                                  
                                    out_file1.write(f"Result: {response1}\n")
                                    out_file1.write("-" * 50 + "\n")

                                    try:
                                        generated_ids = model.generate(**model_inputs, max_new_tokens=512,do_sample=True, top_p=0.9, temperature=0.7)
                                        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
                                        response2 = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                                    except Exception:
                                        continue

                                    # 写入当前条目结果
                                    
                                    out_file2.write(f"Result: {response2}\n")
                                    out_file2.write("-" * 50 + "\n")
                                    try:
                                        generated_ids = model.generate(**model_inputs, max_new_tokens=512,do_sample=True, top_p=0.9, temperature=0.7)
                                        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
                                        response3 = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                                    except Exception:
                                        continue

                                    # 写入当前条目结果
                                    
                                    out_file3.write(f"Result: {response3}\n")
                                    out_file3.write("-" * 50 + "\n")
                                    
                                    try:
                                        generated_ids = model.generate(**model_inputs, max_new_tokens=512,do_sample=True, top_p=0.9, temperature=0.7)
                                        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
                                        response4 = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                                    except Exception:
                                        continue

                                    # 写入当前条目结果
                                    
                                    out_file4.write(f"Result: {response4}\n")
                                    out_file4.write("-" * 50 + "\n")
                                    
                                    try:
                                        generated_ids = model.generate(**model_inputs, max_new_tokens=512,do_sample=True, top_p=0.9, temperature=0.7)
                                        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
                                        response5 = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                                    except Exception:
                                        continue

                                    # 写入当前条目结果
                                    
                                    out_file5.write(f"Result: {response5}\n")
                                    out_file5.write("-" * 50 + "\n")

                        print(f"{bug}_{i} results saved to {output_file1}")
                        print(f"{bug}_{i} results saved to {output_file2}")
                        print(f"{bug}_{i} results saved to {output_file3}")
                        print(f"{bug}_{i} results saved to {output_file4}")
                        print(f"{bug}_{i} results saved to {output_file5}")
