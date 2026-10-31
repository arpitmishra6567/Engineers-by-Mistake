# RepairForge AI — Kaggle Model Evaluation

This directory contains resources and documentation for running model evaluation experiments on Kaggle using open-weight coding models.

## Planned Evaluation Notebook

**Notebook Title:** `RepairForge_AI_OpenWeight_Model_Evaluation`  
**Target Platform:** Kaggle (GPU P100 or T4 x2)  
**Primary Model ID:** `Qwen/Qwen2.5-Coder-1.5B-Instruct` (Hugging Face)

---

### Objective

The purpose of this notebook experiment is to demonstrate real, reproducible inference with an open-weight code LLM inside a controlled environment, evaluating its ability to:
1. Ingest a structured bug report and buggy Python code snippet.
2. Formulate a technical root-cause analysis without hallucinating false evidence.
3. Generate a minimal, valid unified diff patch.
4. Execute test suites against the patched code inside Kaggle's container.
5. Record verifiable pass/fail metrics and export structured JSON reports.

> **Note on Scientific Integrity:**  
> RepairForge strictly prohibits fabricating benchmark metrics or simulated model traces. Metrics reported from this notebook reflect actual executions on Kaggle compute runtimes.

---

### Environment Setup Instructions

To execute this evaluation on Kaggle:

1. **Create Kaggle Notebook:**
   - In Kaggle, create a new Python Notebook.
   - Set **Accelerator** to **GPU P100** or **GPU T4 x2**.
   - Enable **Internet** access in the Notebook Settings panel (required to download Hugging Face model weights).

2. **Install Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install torch transformers accelerate vllm pytest
   ```

3. **Load Model & Tokenizer:**
   ```python
   import torch
   from transformers import AutoModelForCausalLM, AutoTokenizer

   model_id = "Qwen/Qwen2.5-Coder-1.5B-Instruct"

   tokenizer = AutoTokenizer.from_pretrained(model_id)
   model = AutoModelForCausalLM.from_pretrained(
       model_id,
       torch_dtype="auto",
       device_map="auto"
   )
   ```

4. **Define Prompt Template:**
   Use RepairForge's minimal unified diff prompt template:
   ```python
   prompt = """You are an automated code repair generator.
   Target file: average.py
   Bug: ZeroDivisionError occurs when calculating average of an empty list.
   Expected: Raise ValueError("Cannot calculate average of an empty list") when numbers is empty.

   Original Code:
   def calculate_average(numbers):
       return sum(numbers) / len(numbers)

   Generate a minimal code patch in unified diff format. Return ONLY the unified diff."""

   messages = [
       {"role": "system", "content": "You are a code repair assistant. Output only a unified diff."},
       {"role": "user", "content": prompt}
   ]
   text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
   model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

   generated_ids = model.generate(**model_inputs, max_new_tokens=512, temperature=0.1)
   response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
   ```

5. **Execute Verification in Kaggle:**
   ```python
   import subprocess
   # Apply patch, then run pytest
   result = subprocess.run(["pytest", "test_average.py"], capture_output=True, text=True)
   print("Test Exit Code:", result.returncode)
   print("Stdout:", result.stdout)
   ```

6. **Export JSON Evaluation Record:**
   ```python
   import json

   evaluation_record = {
       "platform": "Kaggle",
       "accelerator": "NVIDIA T4",
       "model_id": model_id,
       "task_id": "eval-average-empty-list",
       "test_exit_code": result.returncode,
       "verified": (result.returncode == 0)
   }

   with open("kaggle_eval_result.json", "w") as f:
       json.dump(evaluation_record, f, indent=2)
   ```

