from promptlab import PromptLab
from promptlab.types import Dataset, PromptTemplate

import os

# Define correct dataset and database file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "..", "test", "dataset", "essay_feedback.jsonl")
DB_FILE_PATH = os.path.join(BASE_DIR, "..", "..", "test", "trace_target", "promptlab.db")

def create_prompt_lab(tracer_type: str, tracer_db_file_path: str) -> PromptLab:
    tracer_config = {
        "type": tracer_type,
        "db_file": tracer_db_file_path
    }
    return PromptLab(tracer_config)

def create_prompt_template(prompt_lab: PromptLab, prompt_template_id, system_prompt, user_prompt) -> str:
    prompt_template = PromptTemplate(
        id=prompt_template_id,
        name="essay_feedback_prompt",
        description="A prompt designed to generate feedback for essays.",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
    prompt_template = prompt_lab.asset.create_or_update(prompt_template)
    return (prompt_template.id, prompt_template.version)

def create_dataset(prompt_lab: PromptLab, file_path: str) -> str:
    dataset = Dataset(
        name="essay_feedback_dataset",
        description="Dataset for evaluating the essay_feedback_prompt.",
        file_path=file_path,
    )
    dataset = prompt_lab.asset.create_or_update(dataset)
    return (dataset.id, dataset.version)

def create_experiment(prompt_lab: PromptLab, prompt_template_id: str, prompt_template_version: int, dataset_id: str, dataset_version: int):
    experiment = {
        "model": {
            "type": "ollama",
            "inference_model_deployment": "llama3:latest",
            "embedding_model_deployment": "nomic-embed-text:latest",
        },
        "prompt_template": {
            "id": prompt_template_id,
            "version": prompt_template_version
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
                },
            },
            {
                "type": "ragas",
                "metric": "NonLLMStringSimilarity",
                "column_mapping": {
                    "response": "$inference",
                    "reference": "feedback",
                },
            },
            {
                "type": "ragas",
                "metric": "RougeScore",
                "column_mapping": {
                    "response": "$inference",
                    "reference": "feedback",
                },
            },
        ],
    }
    prompt_lab.experiment.run(experiment)

def deploy_prompt_template(prompt_lab: PromptLab, deployment_dir: str, prompt_template_id: str, prompt_template_version: int):
    prompt = PromptTemplate(
        id=prompt_template_id,
        version=prompt_template_version,
    )
    prompt_lab.asset.deploy(prompt, deployment_dir)

if __name__ == "__main__":

    # ✅ Ensure dataset file exists before running
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"❌ Dataset file not found: {DATASET_PATH}")

    # ✅ Ensure database file exists before running
    if not os.path.exists(DB_FILE_PATH):
        raise FileNotFoundError(f"❌ Database file not found: {DB_FILE_PATH}")

    # Create prompt_lab object
    tracer_type = "sqlite"
    prompt_lab = create_prompt_lab(tracer_type, DB_FILE_PATH)

    # Create a dataset
    dataset_id, dataset_version = create_dataset(prompt_lab, DATASET_PATH)

    # Create first version of the prompt template
    system_prompt_v1 = "You are a helpful assistant who can provide feedback on essays."
    user_prompt_v1 = """The essay topic is - <essay_topic>.

    The submitted essay is - <essay>
    Now write feedback on this essay.
    """
    prompt_template_id, prompt_template_version_v1 = create_prompt_template(prompt_lab, None, system_prompt_v1, user_prompt_v1)

    # Create second version of the prompt template
    system_prompt_v2 = """You are a helpful assistant who provides essay feedback. You follow these criteria:
    - Grammar & Spelling: Check for correct grammar, punctuation, and spelling.
    - Clarity & Fluency: Ensure ideas are expressed smoothly.
    - Content & Relevance: Ensure the essay stays on topic and answers the prompt effectively.
    - Structure & Organization: Ensure clear introduction, body paragraphs, and conclusion.
    """
    user_prompt_v2 = """The essay topic is - <essay_topic>.

    The submitted essay is - <essay>
    Now write feedback on this essay.
    """
    prompt_template_id, prompt_template_version_v2 = create_prompt_template(prompt_lab, prompt_template_id, system_prompt_v2, user_prompt_v2)

    # Run experiments with both prompt template versions
    create_experiment(prompt_lab, prompt_template_id, prompt_template_version_v1, dataset_id, dataset_version)
    create_experiment(prompt_lab, prompt_template_id, prompt_template_version_v2, dataset_id, dataset_version)

    # Launch PromptLab Studio
    prompt_lab.studio.start(8000)

    # Deploy the best prompt version
    deployment_dir = os.path.join(BASE_DIR, "..", "..", "prompt_templates")
    deploy_prompt_template(prompt_lab, deployment_dir, prompt_template_id, prompt_template_version_v2)
