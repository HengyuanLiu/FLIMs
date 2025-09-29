import pandas as pd
import os

if __name__ == "__main__":
    buglist_dict = {
         'Chart': {'total': 26, 'start': 1},
       'Math': {'total': 107, 'start': 1},
     'Mockito': {'total': 38, 'start': 1},
    'Time': {'total': 26, 'start': 1},
        'Lang': {'total': 65, 'start': 1},
    #  'Closure': {'total': 134, 'start': 1},
    }
    # modelslist=['deepseek-14b']
    # # modelslist=['deepseek-7b','deepseek-14b','deepseek-llama-8b','llama-8b','qwen-7b-nowt','qwen-14b','qwen-coder-7b','qwen-coder-14b']
    # # modelslist=['deepseek-7b','deepseek-14b','deepseek-llama-8b','qwen-7b','qwen-14b','qwen-coder-7b','qwen-coder-14b']
    # for models in modelslist:
    for bug, info in buglist_dict.items():
        total = info['total']
        start = info['start']

        for i in range(start, total + 1):
            try:
                print(f"{bug}_{i}")

                # 文件路径拼接
                file_csv = os.path.join(rf"D:\Graduate\new-experimina\result\deepseek-8b\p-f-pca", bug, f"pf_{i}.csv")
                file_xlsx = os.path.join(fr"D:\Graduate\code\result\error1", bug, str(i), f"pf_{i}.xlsx")
                outpath = os.path.join(rf"D:\Graduate\new-experimina\result\deepseek-8b\pf-pca", bug)

                # 创建输出目录（如果不存在）
                os.makedirs(outpath, exist_ok=True)
                output_file = os.path.join(outpath, f"{bug}_{i}_pf.xlsx")

                # 加载数据
                csv_df = pd.read_csv(file_csv, usecols=[0, 1], names=['id', 'weight'], header=0)
                excel_df = pd.read_excel(file_xlsx, usecols=[0, 6], names=['id', 'pf'], header=0)

                # 构建权重字典
                weight = dict(zip(csv_df['id'].astype(int), csv_df['weight']))
                
                # 获取最小权重，默认值为1
                min_weight = csv_df['weight'].min() if not csv_df.empty else 1

                # 对 pf 值应用权重
                pf_result = {}
                for index, row in excel_df.iterrows():
                    mutant_id = int(row['id'])
                    if mutant_id in weight:
                        pf_result[mutant_id] = row['pf'] * weight[mutant_id]
                    else:
                        pf_result[mutant_id] = row['pf'] * min_weight

                # 将结果按权重排序
                sorted_pf = sorted(pf_result.items(), key=lambda x: x[1], reverse=True)

                # 将结果转换为 DataFrame
                result_df = pd.DataFrame(sorted_pf, columns=['mutant_id', 'weighted_pf'])

                # 保存到 Excel 文件
                result_df.to_excel(output_file, index=False)
                print(f"save {output_file}")
            except:
              pass
