import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


def build_prompts() -> list[list[dict[str, str]]]:
    questions = [
        "什么是市盈率？请用一句话回答。",
        "股票和债券的主要区别是什么？",
        "金融数据接口为什么需要记录数据截止日期？",
    ]

    return [
        [
            {
                "role": "system",
                "content": "你是一名金融知识助手，只进行知识解释，不提供投资建议。",
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        for question in questions
    ]


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if device.type == "cuda" else torch.float32

    print(f"device: {device}")
    print(f"dtype: {dtype}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=dtype,
    ).to(device)

    model.eval()

    conversations = build_prompts()

    prompt_texts = [
        tokenizer.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=True,
        )
        for conversation in conversations
    ]

    # 批量输入长度不同，需要进行 padding。
    tokenizer.padding_side = "left"

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    model_inputs = tokenizer(
        prompt_texts,
        return_tensors="pt",
        padding=True,
    ).to(device)

    started_at = time.perf_counter()

    with torch.inference_mode():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=100,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )

    elapsed = time.perf_counter() - started_at

    # 删除输入部分，只保留模型新生成的 token。
    new_token_ids = generated_ids[:, model_inputs.input_ids.shape[1] :]

    answers = tokenizer.batch_decode(
        new_token_ids,
        skip_special_tokens=True,
    )

    for index, answer in enumerate(answers, start=1):
        print(f"\n回答 {index}：")
        print(answer.strip())

    print(f"\n批量大小：{len(answers)}")
    print(f"总耗时：{elapsed:.2f} 秒")
    print(f"平均耗时：{elapsed / len(answers):.2f} 秒/条")


if __name__ == "__main__":
    main()
