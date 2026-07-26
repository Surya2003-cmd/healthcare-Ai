import os
from pathlib import Path

from openai import OpenAI


def _candidate_env_paths():
    project_root = Path(__file__).resolve().parents[1]

    return [
        project_root / ".env",
        Path.cwd() / ".env",
        project_root / ".env.txt",
        Path.cwd() / ".env.txt",
    ]


def _load_env_files():
    checked_paths = []

    for env_path in _candidate_env_paths():
        checked_paths.append(str(env_path))

        if not env_path.exists():
            continue

        for line in env_path.read_text(encoding="utf-8").splitlines():
            clean_line = line.strip()

            if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
                continue

            key, value = clean_line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")

    return checked_paths


_load_env_files()


def ask_openai(question, context="general healthcare guidance"):
    checked_paths = _load_env_files()
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        checked_text = ", ".join(checked_paths)
        return (
            "OpenAI API key is missing. Add OPENAI_API_KEY to your .env file "
            "or set it as a system environment variable. "
            f"Checked: {checked_text}"
        )

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a healthcare assistant inside a student healthcare AI project.
Give concise, helpful, non-diagnostic guidance.
Context: {context}
User question: {question}

Rules:
- Do not claim to be a doctor.
- Do not provide a final diagnosis.
- Mention urgent medical care for severe, emergency, or worsening symptoms.
- Keep the answer practical and easy to understand.
"""

    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=350,
    )

    return response.output_text.strip()
