import pandas as pd
from pathlib import Path
from datasets import Dataset, DatasetDict

def find_answer_index(row):
    answer_text = row["extractive answer"]  
    context = row["context"] 

    try:
        start_idx = context.index(answer_text) 
    except ValueError:
        start_idx = -1  

    return {"text": [answer_text], "answer_start": [start_idx]}

def load_dataset(path: str):
    path = Path(path)
    datasets = {}

    for file_path in path.iterdir():
        if file_path.suffix != '.csv': 
            continue

        df = pd.read_csv(file_path)
        
        columns = ["index", "context", "article", "document", "question", "extractive answer"]

        df["extractive answer"] = df.apply(find_answer_index, axis=1)

        invalid_answers = df[df["extractive answer"].apply(lambda x: x["answer_start"][0] == -1)]
        if not invalid_answers.empty:
            print(f"Warning: Some answers in {file_path.name} were not found in the context!")
            print(invalid_answers[["index", "context", "question", "extractive answer"]])

        dataset_type = file_path.stem  
        datasets[dataset_type] = Dataset.from_pandas(df[columns])

    return DatasetDict(datasets)

if __name__ == "__main__":
    try:
        dataset = load_dataset(r"..\EducationRegulation-QA\data")  
        
        all_combined_contexts = []
        for dataset_name, data in dataset.items():
            for record in data:
                all_combined_contexts.append([record["document"], record["article"], record["context"]])


        combined_df = pd.DataFrame(all_combined_contexts, columns=["document", "article", "context"])

        combined_df.to_csv(r"..\EducationRegulation-QA\app\context.csv", index=False)

        print("Context saved to '/app/context.csv'")
    except Exception as e:
        print(f"Error: {e}")
