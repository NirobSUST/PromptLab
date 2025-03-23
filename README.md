
# 📘 PromptLab Essay Feedback Comparison Project (Human-Friendly Guide)

This guide explains the PromptLab comparison project in a simple and intuitive way so that anyone — whether technical or not — can understand what it does, why it matters, and how it works.

---

## 🎯 What’s the Purpose?

Imagine you're designing a tool to help students improve their essays using AI. But here’s the twist: you want to make sure the AI gives good advice. The big question is — **what’s the best way to ask the AI for feedback?**

That’s where PromptLab comes in.

PromptLab lets you test different ways of asking the AI to do a task (called "prompts") and then compare how well each one performs. You write different versions of the prompt, run them on real student essays, and then see which one gives the most useful and accurate feedback.

In short: **You test different prompt ideas → Let AI generate responses → Compare which version performs best.**

---

## 🧠 What is PromptLab Really Doing?

Here’s a simplified breakdown:

1. You provide a bunch of essays written by students.
2. You write different styles of prompts (ways of asking the AI to give feedback).
3. PromptLab feeds each essay into each prompt.
4. It sends the prompt + essay to an AI model (like ChatGPT or LLaMA).
5. The AI writes feedback.
6. PromptLab compares the AI’s feedback to human-written feedback (included in your dataset).
7. It scores how close, helpful, or accurate the AI’s feedback is.
8. You get a visual dashboard to see which prompt worked best.

---

## 🧾 What Does the Dataset Contain?

Each entry in the dataset includes:

- An essay topic
- The essay text
- A sample feedback (from a human or gold-standard source)

PromptLab uses this feedback to check how well the AI did.

---

## ✍️ The Prompt Templates We’re Testing

In the `compare_prompts.py` implementation, we test and compare three distinct prompt styles:

### 1. **Simple Prompt**
A direct and basic prompt:
> **System Prompt:** You are a helpful assistant who gives feedback on essays.
>
> **User Prompt:** The essay topic is - <essay_topic>
> The submitted essay is - <essay>
> Now write feedback on this essay.

### 2. **Structured Criteria Prompt**
Provides clear evaluation categories:
> **System Prompt:** You are a helpful assistant who provides essay feedback. Use these criteria:
> - Grammar & Spelling
> - Clarity & Fluency
> - Content & Relevance
> - Structure & Organization
>
> **User Prompt:** The essay topic is - <essay_topic>
> The submitted essay is - <essay>
> Provide feedback based on the criteria above.

### 3. **Encouraging Coach Prompt**
Promotes supportive and constructive tone:
> **System Prompt:** You are a supportive writing coach giving kind but constructive feedback.
>
> **User Prompt:** The student wrote an essay on: <essay_topic>
> Here is the essay: <essay>
> Give helpful feedback that encourages improvement.

These three styles explore different tones, levels of specificity, and types of AI guidance. PromptLab evaluates which performs best against human-written feedback.

---

## 📊 How Are Results Compared?

Once the AI writes its feedback, PromptLab compares it to the reference human-written feedback. It uses automated tools (called evaluation metrics) to measure things like:

- **Meaning similarity** (Did the AI understand the essay?)
- **Word overlap** (Do they talk about the same things?)
- **Text similarity** (Are they written in a similar way?)

These metrics are like grading rubrics for the AI's response.

---

## 💡 What Do You See in the End?

Once everything is done, you get a web-based dashboard where you can:

- See each prompt version side-by-side
- View the AI's feedback
- Check the scores from the comparison
- Decide which prompt version is the most effective

This makes it really easy to test ideas and improve your system without guesswork.

---

## 🧾 Sample Input and Output

### Sample Input from the Dataset

```json
{
  "id": "essay_001",
  "essay_topic": "The impact of social media on mental health",
  "essay": "Social media has transformed the way we communicate. However, excessive use can lead to anxiety, poor sleep, and lowered self-esteem among young people.",
  "feedback": "The essay presents valid concerns, but it lacks supporting evidence and a clear conclusion."
}
```

### Structured Prompt Template Used

```
System:
You are a helpful assistant who provides feedback on essays. You follow these criteria:
- Grammar
- Clarity
- Content
- Structure

User:
The essay topic is - <essay_topic>
The submitted essay is - <essay>
Now write feedback on this essay.
```

### Final Prompt Sent to AI

```
System:
You are a helpful assistant who provides feedback on essays. You follow these criteria:
- Grammar
- Clarity
- Content
- Structure

User:
The essay topic is - The impact of social media on mental health
The submitted essay is - Social media has transformed the way we communicate. However, excessive use can lead to anxiety, poor sleep, and lowered self-esteem among young people.
Now write feedback on this essay.
```

### AI-Generated Output

> The essay addresses an important issue and is generally well-written. There are no major grammar issues. However, it lacks depth in content—examples or references would improve its persuasiveness. The essay structure is adequate, but a stronger conclusion could help tie everything together.

### Evaluation by PromptLab

- Semantic Similarity: ✅ High
- Rouge Score: ⚠️ Moderate
- String Match: ❌ Low (phrasing differs but ideas match)

This helps you pick the most informative and effective prompt, based on actual feedback behavior.

---

## 🔧 Code Implementation Example

The `compare_prompts.py` file automates the full evaluation workflow — from dataset loading to prompt registration, experiment execution, and launching the dashboard. Below is an overview of the script structure and what each part does.

### 🧱 1. Setup and Paths
```python
import os
from promptlab import PromptLab
from promptlab.types import Dataset, PromptTemplate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "..", "test", "dataset", "essay_feedback.jsonl")
DB_FILE_PATH = os.path.join(BASE_DIR, "promptlab_compare.db")
DEPLOY_DIR = os.path.join(BASE_DIR, "deployment")
os.makedirs(DEPLOY_DIR, exist_ok=True)
```

### 📄 2. Define Prompt Variants
```python
prompt_variants = [
    {...},
    {...},
    {...}
]
```

### 🚀 3. Initialize PromptLab
```python
prompt_lab = PromptLab({"type": "sqlite", "db_file": DB_FILE_PATH})
```

### 🧾 4. Register Dataset
```python
dataset = Dataset(
    name="essay_feedback_dataset",
    description="Dataset for prompt comparison.",
    file_path=DATASET_PATH
)
dataset = prompt_lab.asset.create_or_update(dataset)
```

### 📝 5. Register Prompts
```python
for p in prompt_variants:
    template = PromptTemplate(...)
    prompt_lab.asset.create_or_update(template)
```

### ⚗️ 6. Run Experiments
```python
for each prompt version:
    run prompt_lab.experiment.run({
        "model": {...},
        "prompt_template": {...},
        "dataset": {...},
        "evaluation": [...]
    })
```

### 🌐 7. Launch Studio
```python
prompt_lab.studio.start(8000)
```

---

## 👀 Why Is This Project Valuable?

If you're building an educational tool, chatbot, or any AI assistant that interacts with people — **the way you phrase prompts makes a huge difference**. This project gives you a repeatable and visual way to:

- Test ideas
- Measure performance
- Avoid assumptions
- Build better AI systems

---

## ✅ In Summary

- You want to give students feedback on essays using AI.
- You’re trying different ways to ask the AI.
- PromptLab helps you test which prompt works best.
- You get results scored and visualized automatically.
- You can confidently choose the best prompt and use it in your final product.

**PromptLab turns guesswork into evidence.** It’s your experiment lab for prompt design — intuitive, hands-on, and built for real-world feedback improvement.
