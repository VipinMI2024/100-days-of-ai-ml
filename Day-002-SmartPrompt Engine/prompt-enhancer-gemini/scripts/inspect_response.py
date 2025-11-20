#!/usr/bin/env python
"""
Debug script to inspect actual Gemini API response structure.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def inspect_response_structure():
    """Inspect the actual response structure from Gemini API."""
    print("=" * 60)
    print("Inspecting Gemini Response Structure")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL_NAME") or "models/gemini-2.5-pro"
    
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        return False
    
    genai.configure(api_key=api_key)
    print(f"Model: {model_name}\n")
    
    # Test with a simple text generation request
    prompt = "Say hello and introduce yourself in one sentence."
    
    try:
        # Use generate_text if available
        if hasattr(genai, "generate_text"):
            print("Using: genai.generate_text()")
            response = genai.generate_text(
                model=model_name,
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=512,
            )
        else:
            print("Using: model.generate_content()")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
        
        print(f"\nResponse type: {type(response)}")
        print(f"Response: {response}")
        print("\n" + "-" * 60)
        print("Response attributes:")
        for attr in dir(response):
            if not attr.startswith("_"):
                try:
                    val = getattr(response, attr)
                    if not callable(val):
                        print(f"  {attr}: {type(val).__name__}")
                except Exception:
                    pass
        
        print("\n" + "-" * 60)
        if hasattr(response, "text"):
            try:
                print(f"response.text: {response.text[:100]}...")
            except Exception as e:
                print(f"Error accessing response.text: {e}")
        
        if hasattr(response, "candidates"):
            print(f"\nCandidates: {len(response.candidates)} candidates")
            for i, cand in enumerate(response.candidates):
                print(f"  Candidate {i}:")
                if hasattr(cand, "finish_reason"):
                    print(f"    finish_reason: {cand.finish_reason}")
                if hasattr(cand, "content"):
                    content = cand.content
                    print(f"    content type: {type(content).__name__}")
                    if hasattr(content, "parts"):
                        print(f"    content.parts: {len(content.parts)} parts")
                        for j, part in enumerate(content.parts):
                            print(f"      Part {j} type: {type(part).__name__}")
                            if hasattr(part, "text"):
                                print(f"        text: {part.text[:100]}..." if len(part.text) > 100 else f"        text: {part.text}")
        
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = inspect_response_structure()
    sys.exit(0 if success else 1)
