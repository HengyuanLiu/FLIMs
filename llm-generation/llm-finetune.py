import json
import os
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, EarlyStoppingCallback
)
from peft import get_peft_model, LoraConfig, TaskType
from sklearn.metrics import accuracy_score

os.environ["TOKENIZERS_PARALLELISM"] = "false"

buglist_dict = {
    'Chart': 6, 
    # 'Math': 22, 
    # 'Mockito': 8,
    # 'Time': 6, 
    # 'Lang': 12, 
    # 'Closure': 26
}

texts, labels = [], []

# 数据加载
for bug, index in buglist_dict.items():
    for i in range(1, index):  # 注意 index 不包含本身
        file_path = f"/home/wangdonghua/Qwen/data/wt-dataset/{bug}/{bug}_{i}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    text = ("Please determine whether this mutant is a FLIM?" + "\n" +
                            str(item["mutant_id"]) + "\n" +
                            str(item["original_code"]) + "\n" +
                            str(item["test_error"]) + "\n" +
                            str(item["mutant_code"]) + "\n" +
                            str(item["mutant_class"]) + "\n" +
                            str(item["line_number"]) + "\n" +
                            str(item["mutation_error"]))
                    texts.append(text)
                    labels.append(0 if item["is_flim"] == "true" else 1)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

print(f"Loaded {len(texts)} samples.")

# 创建 Dataset
dataset = Dataset.from_dict({"text": texts, "label": labels})

# Tokenizer 和 模型
model_path = "/home/wangdonghua/Deepseek/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
tokenizer = AutoTokenizer.from_pretrained(model_path)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForSequenceClassification.from_pretrained(
    model_path,
    num_labels=2,
    low_cpu_mem_usage=True,
    use_safetensors=True,
    pad_token_id=tokenizer.pad_token_id
)

# 应用 LoRA
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,
    lora_alpha=32,
    lora_dropout=0.3,  # 防止过拟合
)
model = get_peft_model(model, lora_config)

# 数据预处理
def preprocess_data(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

tokenized_dataset = dataset.map(preprocess_data, batched=True)

# 划分训练和验证集
split = tokenized_dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split["train"]
eval_dataset = split["test"]

# 计算评估指标
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

# 训练参数设置
training_args = TrainingArguments(
    output_dir="./qwen2.5-14b-lora-finetuned",
    per_device_train_batch_size=1,
    num_train_epochs=10,
    learning_rate=2e-5,
    bf16=False,
    tf32=True,
    logging_steps=10,
    evaluation_strategy="epoch",   # 每个 epoch 评估
    save_strategy="epoch",         # 每个 epoch 保存一次
    save_total_limit=2,
    load_best_model_at_end=True,   # 自动加载最优模型
    metric_for_best_model="accuracy",
    greater_is_better=True,
)

# Trainer 初始化
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],  # 提前终止
)

# 开始训练
trainer.train()

# 保存模型与 tokenizer
model_save_path = "/home/wangdonghua/Qwen/deepseek-14b/saved_model"
trainer.save_model(model_save_path)
tokenizer.save_pretrained(model_save_path)

# 清理缓存
torch.cuda.empty_cache()
