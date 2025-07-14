from google import genai
from google.genai import types
from groq import Groq
import anthropic
import os
import re

sys_instruct=("You are given a list of claims from a closed captioning transcript from a YouTube video. "
              "Analyze each claim from the provided list and determine whether it is true or false based on factual information. "
              "For each claim, return one of the following labels: "
              "True - if the claim is factually accurate "
              "False - if the claim is incorrect or misleading. "
              "Do not modify the input claim in any way; just provide the original claim and the label next to it. "
              "Output only the claims and label, one per line, without any introductory text or explanations")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client_Claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
LLM1 = "gemini-2.0-flash"
LLM2 = "llama-3.3-70b-versatile"
LLM3 = "claude-3-haiku-20240307"

def factCheck(claims):
    client_gemini = genai.Client(api_key=GEMINI_API_KEY)
    contents = claims
    contents_string = " ".join(contents)

    response = client_gemini.models.generate_content(
            model=LLM1,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct),
            contents= contents
    )

    client_Groq1 = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion1 = client_Groq1.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": contents_string,
            },
            {
                "role": "system",
                "content": sys_instruct
            },
        ],
        model=LLM2,
    )

    message = client_Claude.messages.create(
        model=LLM3,
        max_tokens=4096,
        temperature=1,
        system=sys_instruct,
        messages=[
            {
                "role": "user",
                "content": contents_string
            }
        ]
    )

    labeled_list1 = re.split(r"(True|False)", response.text)
    labeled_list2 = re.split(r"(True|False)", chat_completion1.choices[0].message.content)
    labeled_list3 = re.split(r"(True|False)", message.content[0].text)

    votes = {key: [val1, val2, val3] for key, val1, val2, val3 in zip(contents, labeled_list1[1::2], labeled_list2[1::2], labeled_list3[1::2])}

    return votes, LLM1, LLM2, LLM3
