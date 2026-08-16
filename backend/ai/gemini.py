import os
import json

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "gemini-3.1-flash-lite"


# ============================================================
# CLIENT
# ============================================================

def get_gemini_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to the .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# CLEAN GEMINI JSON
# ============================================================

def clean_json_response(text):

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences if Gemini adds them
    # --------------------------------------------------------

    if text.startswith("```"):

        lines = text.splitlines()

        cleaned_lines = []

        for line in lines:

            if line.strip().startswith("```"):
                continue

            cleaned_lines.append(line)

        text = "\n".join(
            cleaned_lines
        ).strip()

    # --------------------------------------------------------
    # Try normal JSON parsing
    # --------------------------------------------------------

    try:

        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Try extracting the JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        json_text = text[
            start:end + 1
        ]

        try:

            return json.loads(
                json_text
            )

        except json.JSONDecodeError:
            pass

    # --------------------------------------------------------
    # Gemini didn't return valid JSON
    # --------------------------------------------------------

    raise RuntimeError(
        "Gemini returned an invalid analysis format."
    )


# ============================================================
# GPU COMPARISON ANALYSIS
# ============================================================

def analyze_gpu_comparison(
    comparison
):

    client = get_gemini_client()


    # ========================================================
    # CONVERT BENCHMARK DATA TO JSON
    # ========================================================

    benchmark_json = json.dumps(
        comparison,
        indent=2,
        default=str
    )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are ComputeBench AI, an expert GPU
benchmark analyst.

Analyze the REAL benchmark comparison below.

IMPORTANT RULES:

1. Use ONLY the supplied benchmark data.
2. Never invent benchmark numbers.
3. Never change benchmark values.
4. Never invent GPU specifications.
5. Clearly distinguish measured results from
   possible explanations.
6. Keep the analysis technically accurate.
7. Do not mention information that is not
   present in the benchmark data.
8. Keep the answer concise and useful.

YOUR RESPONSE MUST BE VALID JSON.

Return ONLY the JSON object.

DO NOT return:
- Markdown
- HTML
- code fences
- ```json
- headings outside JSON
- text before the JSON
- text after the JSON
- bullet points outside the JSON

Use EXACTLY this JSON structure:

{{
    "overview": "A concise overview of the comparison.",

    "key_findings": [
        "Important finding 1.",
        "Important finding 2.",
        "Important finding 3.",
        "Important finding 4."
    ],

    "scaling_analysis": "Explain how GPU performance changes as matrix size increases.",

    "stability_analysis": "Explain standard deviation, consistency and execution-time stability.",

    "performance_interpretation": "Explain what the benchmark results mean in practical compute terms.",

    "recommendation": "State which GPU is better for the tested compute workload and explain why.",

    "caveat": "Mention important limitations of interpreting this benchmark."
}}

IMPORTANT:

Do not put Markdown formatting inside the strings.

Bad:
"### The RTX 4090 is faster"

Good:
"The RTX 4090 is faster across the tested workloads."

Benchmark comparison:

{benchmark_json}
"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        interaction = client.interactions.create(

            model=MODEL_NAME,

            input=prompt

        )

    except Exception as error:

        print(
            "Gemini API error:",
            error
        )

        raise RuntimeError(
            f"Gemini API request failed: {error}"
        )


    # ========================================================
    # GET OUTPUT TEXT
    # ========================================================

    try:

        output_text = (
            interaction.output_text
        )

    except Exception:

        output_text = None


    if not output_text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        analysis = clean_json_response(
            output_text
        )

    except Exception as error:

        print(
            "Gemini raw response:"
        )

        print(
            output_text
        )

        raise RuntimeError(
            str(error)
        )


    # ========================================================
    # VALIDATE STRUCTURE
    # ========================================================

    required_fields = [

        "overview",

        "key_findings",

        "scaling_analysis",

        "stability_analysis",

        "performance_interpretation",

        "recommendation",

        "caveat",

    ]


    for field in required_fields:

        if field not in analysis:

            raise RuntimeError(
                f"Gemini response is missing "
                f"'{field}'."
            )


    # ========================================================
    # NORMALIZE KEY FINDINGS
    # ========================================================

    if not isinstance(
        analysis["key_findings"],
        list
    ):

        analysis["key_findings"] = [
            str(
                analysis["key_findings"]
            )
        ]


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "model":
            MODEL_NAME,

        "analysis":
            analysis,

    }