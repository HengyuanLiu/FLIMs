import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, StandardScaler
def entropy_weighted_average(input_csv, output_csv):
   
    # 加载数据
    df = pd.read_csv(input_csv)
    # 提取矩阵和行标号
    matrix = df.iloc[:, 1:].values
    row_labels = df['mutant_id'].values
    # 步骤1：归一化矩阵
    P = matrix / matrix.sum(axis=0, keepdims=True)
    # print(P)
    # 步骤2：计算熵
    P = np.where(P == 0, 1e-10, P)  # 避免log(0)
    entropy = -np.sum(P * np.log(P), axis=0) / np.log(len(matrix))
    # 步骤3：计算权重
    weights = (1 - entropy) / np.sum(1 - entropy)
    # 步骤4：计算加权平均
    weighted_avg = np.dot(matrix, weights)
    # 保存结果
    result_df = pd.DataFrame({
        'mutant_id': row_labels,
        'weighted_avg': weighted_avg
    })
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result_df.to_csv(output_csv, index=False)
    print(f"save {output_csv}")


def pca_dimensionality_reduction(input_csv, output_csv, n_components=1, normalization='minmax'):
    """
    对CSV文件进行PCA降维并归一化
    :param input_csv: 输入的CSV文件路径
    :param output_csv: 输出的CSV文件路径
    :param n_components: PCA降维的维度
    :param normalization: 归一化方法 ('minmax' 或 'zscore')
    """
    # 读取数据
    df = pd.read_csv(input_csv)
    # 提取特征矩阵（去掉行标号）
    matrix = df.iloc[:, 1:].values
    row_labels = df['mutant_id'].values
    # print(len(matrix))
    # print(row_labels)
    # PCA降维
    pca = PCA(n_components=n_components)
    # print(pca)
    pca_result = pca.fit_transform(matrix)
    # 归一化
    if normalization == 'minmax':
        scaler = MinMaxScaler()
    elif normalization == 'zscore':
        scaler = StandardScaler()
    else:
        raise ValueError("Unsupported normalization method. Use 'minmax' or 'zscore'.")

    normalized_result = scaler.fit_transform(pca_result)
    # 保存结果
    result_df = pd.DataFrame(normalized_result, columns=[f'PC{i+1}' for i in range(n_components)])
    result_df.insert(0, 'mutant_id', row_labels)
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result_df.to_csv(output_csv, index=False)
    print(f"save {output_csv}")

def weighted_average_by_importance(input_csv, output_csv, importance_weights):
    """
    使用列的重要性比例计算加权平均值
    :param input_csv: 输入的CSV文件路径
    :param output_csv: 输出的CSV文件路径
    :param importance_weights: 列的重要性权重（长度需与列数一致）
    """
    # 读取数据
    df = pd.read_csv(input_csv)

    # 提取矩阵和行标号
    matrix = df.iloc[:, 1:].values
    row_labels = df['mutant_id'].values

    # 检查权重长度是否与列数一致
    if len(importance_weights) != matrix.shape[1]:
        raise ValueError(f"权重数量 {len(importance_weights)} 与列数 {matrix.shape[1]} 不一致")

    # 归一化权重，使其和为1
    weights = np.array(importance_weights) / np.sum(importance_weights)

    # 计算加权平均
    weighted_avg = np.dot(matrix, weights)

    # 保存结果
    result_df = pd.DataFrame({
        'mutant_id': row_labels,
        'weighted_avg': weighted_avg
    })

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    result_df.to_csv(output_csv, index=False)
    print(f"save {output_csv}")

if __name__ == "__main__":
    buglist_dict = {
        'Chart': {'total': 26, 'start': 1},
       'Math': {'total': 107, 'start': 1},
     'Mockito': {'total': 38, 'start': 1},
    'Time': {'total': 26, 'start': 1},
        'Lang': {'total': 65, 'start': 1},
       'Closure': {'total': 134, 'start': 1},
    }
    
    for bug, info in buglist_dict.items():
        total = info['total']
        start = info['start']
        
        for i in range(start, 1 + total):
            try:
                print(f"{bug}_{i}")
                input_path = rf"D:\Graduate\new-experimina\result\deepseek-8b\wkill_matrix\{bug}\{bug}_{i}_wkill_matrix.csv"
                output_parent_dir = rf"D:\Graduate\new-experimina\result\deepseek-8b\p-f-pca\{bug}"
                output_path = os.path.join(output_parent_dir, rf"pf_{i}.csv")

                # 基于熵的加权平均
                # entropy_weighted_average(input_path, output_path)
                #pca降维
                pca_dimensionality_reduction(input_path, output_path, n_components=1, normalization='minmax')
                # importance_weights = [0.2, 0.2, 0.2, 0.2, 0.2]
                # weighted_average_by_importance(input_path, output_path, importance_weights)
            except:
                print(f"{bug}_{i} error")
            
            
          