
import os
from promptlab import PromptLab
from promptlab.types import Dataset, PromptTemplate

# File paths (update these if needed)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "..", "test", "dataset", "essay_feedback.jsonl")
DB_FILE_PATH = os.path.join(BASE_DIR, "promptlab_compare.db")
DEPLOY_DIR = os.path.join(BASE_DIR, "deployment")

# Ensure paths exist
os.makedirs(DEPLOY_DIR, exist_ok=True)

prompt_variants = [
    {
        "system": "You are a helpful assistant who gives feedback on essays.",
        "user": """
        The essay topic is - <essay_topic>
        The submitted essay is - <essay>
        Now write feedback on this essay.
        """,
        "name": "Simple Prompt"
    },
    {
        "system": "You are a helpful assistant who provides essay feedback. Use these criteria:\n- Grammar & Spelling\n- Clarity & Fluency\n- Content & Relevance\n- Structure & Organization",
        "user": """
        The essay topic is - <essay_topic>
        The submitted essay is - <essay>
        Provide feedback based on the criteria above.
        """,
        "name": "Structured Criteria"
    },
    {
        "system": "You are a supportive writing coach giving kind but constructive feedback.",
        "user": """
        The student wrote an essay on: <essay_topic>
        Here is the essay: <essay>
        Give helpful feedback that encourages improvement.
        """,
        "name": "Encouraging Coach"
    },
]

def init_promptlab():
    tracer_config = {
        "type": "sqlite",
        "db_file": DB_FILE_PATH
    }
    return PromptLab(tracer_config)

def register_dataset(prompt_lab: PromptLab):
    dataset = Dataset(
        name="essay_feedback_dataset",
        description="Dataset for prompt comparison.",
        file_path=DATASET_PATH
    )
    dataset = prompt_lab.asset.create_or_update(dataset)
    return dataset.id, dataset.version

def register_prompts(prompt_lab: PromptLab):
    ids = []
    for i, p in enumerate(prompt_variants):
        template = PromptTemplate(
            id=None,
            name=f"essay_prompt_variant_{i+1}",
            description=p["name"],
            system_prompt=p["system"].strip(),
            user_prompt=p["user"].strip(),
        )
        created = prompt_lab.asset.create_or_update(template)
        ids.append((created.id, created.version))
    return ids

def run_experiments(prompt_lab: PromptLab, prompt_ids, dataset_id, dataset_version):
    for (pid, version), variant in zip(prompt_ids, prompt_variants):
        experiment = {
            "model": {
                "type": "ollama",
                "inference_model_deployment": "llama3:latest",
                "embedding_model_deployment": "nomic-embed-text:latest"
            },
            "prompt_template": {
                "id": pid,
                "version": version
            },
            "dataset": {
                "id": dataset_id,
                "version": dataset_version
            },
            "evaluation": [
                {
                    "type": "ragas",
                    "metric": "SemanticSimilarity",
                    "column_mapping": {
                        "response": "$inference",
                        "reference": "feedback"
                    }
                },
                {
                    "type": "ragas",
                    "metric": "RougeScore",
                    "column_mapping": {
                        "response": "$inference",
                        "reference": "feedback"
                    }
                },
            ]
        }
        prompt_lab.experiment.run(experiment)

def main():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    prompt_lab = init_promptlab()
    dataset_id, dataset_version = register_dataset(prompt_lab)
    prompt_ids = register_prompts(prompt_lab)
    run_experiments(prompt_lab, prompt_ids, dataset_id, dataset_version)

    print("✅ Experiments completed. Launch Studio with:")
    print("prompt_lab.studio.start(8000)")
    prompt_lab.studio.start(8000)

if __name__ == "__main__":
    main()
