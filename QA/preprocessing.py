from transformers import AutoTokenizer

def get_tokenizer(model_name: str = "vinai/phobert-base"):
    return AutoTokenizer.from_pretrained(model_name)

def create_offset_mapping(text, tokenizer):
    tokens = tokenizer.tokenize(text)
    offset_mapping = []
    current_position = 0

    for token in tokens:
        token = token.replace("▁", "") 
        start_index = text.find(token, current_position)
        end_index = start_index + len(token)
        offset_mapping.append((start_index, end_index))
        current_position = end_index

    return offset_mapping

def preprocessing(examples, model_name: str = "vinai/phobert-base"):
    tokenizer = get_tokenizer(model_name)

    questions = [q.strip() for q in examples["question"]]

    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=400,
        truncation="only_second",
        padding="max_length",
        return_offsets_mapping=True,
    )

    # offset_mappings = []
    # for context in examples["context"]:
    #     offset_mapping = create_offset_mapping(context, tokenizer)
    #     offset_mappings.append(offset_mapping)

    offset_mappings = inputs.pop("offset_mapping")
    answers = examples["extractive answer"]
    start_positions = []
    end_positions = []

    for i, offset in enumerate(offset_mappings):
        answer = answers[i]
        start_char = answer["answer_start"][0]
        end_char = answer["answer_start"][0] + len(answer["text"][0])
        sequence_ids = inputs.sequence_ids(i)

        idx = 0
        while sequence_ids[idx] != 1:
            idx += 1
        context_start = idx
        while sequence_ids[idx] == 1:
            idx += 1
        context_end = idx - 1

        if offset[context_start][0] > end_char or offset[context_end][1] < start_char:
            start_positions.append(0)
            end_positions.append(0)
        else:
            idx = context_start
            while idx <= context_end and offset[idx][0] <= start_char:
                idx += 1
            start_positions.append(idx - 1)

            idx = context_end
            while idx >= context_start and offset[idx][1] >= end_char:
                idx -= 1
            end_positions.append(idx + 1)

    inputs["start_positions"] = start_positions
    inputs["end_positions"] = end_positions
    return inputs
