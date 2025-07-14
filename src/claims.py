from google import genai
from google.genai import types
import os
from sentence_transformers import SentenceTransformer, util

sys_instruct=("You are given a closed captioning transcript from a YouTube video. "
              "Extract all objective, fact-based claims that can be supported by evidence or verified through a credible source. "
              "Each claim should be a single, self-contained sentence that preserves the meaning of the original statement without requiring prior context or ambiguity. "
              "Subjective opinions, personal experiences, emotions, and sponsorship mentions should be excluded. "
              "Merge or rewrite related claims to provide full clarity and accuracy. "
              "Output only the claims, one per line, without any introductory text, explanations, or special characters. ")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def getClaims(transcript):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct),
        contents=transcript
    )

    claims = [claim.strip() for claim in response.text.split("\n") if claim.strip()]
    claim_embeddings = model.encode(claims, convert_to_tensor=True)
    cosine_similarities = util.pytorch_cos_sim(claim_embeddings, claim_embeddings)
    threshold = 0.85

    unique_claims = []
    seen_indices = set()
    similar_pairs = []

    for i in range(len(claims)):
        if i in seen_indices:
            continue

        unique_claims.append(claims[i])

        for j in range(i + 1, len(claims)):
            similarity_score = cosine_similarities[i][j].item()
            if cosine_similarities[i][j] > threshold:
                seen_indices.add(j)
                similar_pairs.append((claims[i], claims[j], similarity_score))

    return unique_claims