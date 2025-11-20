#!/usr/bin/env python
"""
Debug script to test response extraction from Gemini API.
Tests the _extract_text_from_response() helper with actual API responses.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.gemini_client import GeminiClient, _extract_text_from_response
from dotenv import load_dotenv

load_dotenv()

def test_response_extraction():
    """Test response extraction with actual Gemini API."""
    print("=" * 60)
    print("Testing Gemini Response Extraction")
    print("=" * 60)
    
    try:
        # Initialize client
        client = GeminiClient()
        print(f"✓ GeminiClient initialized with model: {client.model_name}")
        
        # Test with a simple prompt
        test_prompt = "Enhance this vague prompt: 'Make it better'"
        print(f"\nTest prompt: {test_prompt}")
        print("-" * 60)
        
        # Call enhance_prompt and capture response
        try:
            result = client.enhance_prompt(test_prompt, mode="detailed", temperature=0.7)
            print(f"✓ Enhancement succeeded!")
            print(f"\nEnhanced prompt:\n{result}")
            print("-" * 60)
            print("Response extraction test: PASSED")
        except ValueError as e:
            if "No text in response" in str(e):
                print(f"✗ Response extraction failed: {e}")
                print("\nDEBUG: Response structure may be unexpected.")
                print("      This indicates the _extract_text_from_response() helper")
                print("      needs additional handling for your SDK/model combination.")
                return False
            raise
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_response_extraction()
    sys.exit(0 if success else 1)
