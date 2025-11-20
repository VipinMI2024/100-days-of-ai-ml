"""
Google Gemini API client wrapper for prompt enhancement.
"""
import os
from typing import Optional, List
import time
import re
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    from google.generativeai import types as genai_types
except Exception:
    genai = None
    genai_types = None


class GeminiClient:
    """Wrapper for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env or environment variables.")

        if genai is None:
            raise ValueError("google-generativeai package not available. Install from requirements.txt")

        try:
            genai.configure(api_key=self.api_key)

            # Allow user to pin a model via environment variable
            self.model_name = os.getenv("GEMINI_MODEL_NAME") or os.getenv("GEMINI_MODEL")

            # Discover available models and pick a suitable text-generation model if not pinned.
            try:
                listed = genai.list_models()
            except Exception:
                listed = None

            if not self.model_name and listed:
                # `listed` may be an iterable of model objects or dicts; extract names robustly
                names = []
                for item in listed:
                    name = None
                    if hasattr(item, "name"):
                        name = getattr(item, "name")
                    elif isinstance(item, dict) and "name" in item:
                        name = item.get("name")
                    if name:
                        names.append(name)

                # store available models for possible rotation/fallback
                self.available_models = names

                # prefer models that contain known generation families
                preferred_keywords = ("gemini", "bison", "text", "flash", "pro")
                for n in names:
                    if any(k in n.lower() for k in preferred_keywords):
                        # pick the full model id as returned by list_models (e.g., 'models/gemini-2.5-pro')
                        self.model_name = n
                        break

                # fallback to first available model name
                if not self.model_name and names:
                    self.model_name = names[0]

            else:
                # ensure available_models is defined even if list_models() failed
                self.available_models = []

            # If still not set, leave it as None; downstream code will raise a clear error
            # Try to get a model object if possible; otherwise rely on top-level helpers that accept model name
            try:
                if self.model_name:
                    self.model = genai.GenerativeModel(self.model_name)
                else:
                    self.model = None
            except Exception:
                self.model = None
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")

    def enhance_prompt(self, prompt: str, mode: str = "detailed", temperature: float = 0.7, max_tokens: int = 1000000) -> str:
        """Enhance a prompt using Gemini AI and return the enhanced text."""
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        mode_instructions = {
            "basic": "Improve clarity, add key details, keep concise.",
            "detailed": "Add comprehensive context, examples, and specific requirements.",
            "creative": "Expand with vivid descriptions and storytelling elements.",
            "technical": "Optimize for technical accuracy and developer clarity.",
        }

        instruction = mode_instructions.get(mode, mode_instructions["detailed"])

        system_message = (
            f"You are a prompt engineer. Enhance this prompt.\n"
            f"Mode: {mode} - {instruction}\n\n" + prompt
        )

        # Use a helper that implements retry/backoff and model fallback
        try:
            return self._generate_with_retries(system_message, temperature, max_tokens)
        except Exception as e:
            raise ValueError(f"Gemini API error: {e}")

    def _generate_with_retries(self, system_message: str, temperature: float, max_tokens: int) -> str:
        """Attempt generation with retry on 429 (respecting retry_delay) and rotate models on repeated failures."""
        tried_models: List[str] = []
        # build candidate model list: pinned first, then available_models
        candidates = []
        if self.model_name:
            candidates.append(self.model_name)
        candidates.extend([m for m in getattr(self, 'available_models', []) if m not in candidates])

        last_exc = None
        for model in candidates:
            tried_models.append(model)
            try:
                # try top-level helper if available
                if hasattr(genai, "generate_text"):
                    resp = genai.generate_text(
                        model=model,
                        prompt=system_message,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        top_p=0.9,
                    )
                else:
                    # try model object path
                    try:
                        model_obj = genai.GenerativeModel(model)
                        resp = model_obj.generate_content(
                            system_message,
                            generation_config=genai_types.GenerationConfig(
                                temperature=temperature,
                                max_output_tokens=max_tokens,
                                top_p=0.9,
                            ) if genai_types else None,
                        )
                    except Exception as e:
                        raise

                text = _extract_text_from_response(resp)
                if not text or text.startswith("GenerateContentResponse") or text.startswith("response:"):
                    raise ValueError(f"Gemini returned empty or invalid response. Raw: {resp}")
                # update pinned model to successful one
                self.model_name = model
                return text.strip()

            except Exception as e:
                last_exc = e
                msg = str(e)
                # try to parse retry_delay seconds from message
                m = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', msg)
                if m:
                    wait = int(m.group(1)) + 1
                    time.sleep(wait)
                    # retry once with same model
                    try:
                        if hasattr(genai, "generate_text"):
                            resp = genai.generate_text(
                                model=model,
                                prompt=system_message,
                                temperature=temperature,
                                max_output_tokens=max_tokens,
                                top_p=0.9,
                            )
                        else:
                            model_obj = genai.GenerativeModel(model)
                            resp = model_obj.generate_content(
                                system_message,
                                generation_config=genai_types.GenerationConfig(
                                    temperature=temperature,
                                    max_output_tokens=max_tokens,
                                    top_p=0.9,
                                ) if genai_types else None,
                            )
                        text = _extract_text_from_response(resp)
                        if text and not text.startswith("GenerateContentResponse") and not text.startswith("response:"):
                            self.model_name = model
                            return text.strip()
                    except Exception as e2:
                        last_exc = e2
                        # continue to next model
                        continue
                # not a retryable message or retry failed — try next candidate
                continue

        # if we get here, all candidates failed
        if last_exc:
            raise last_exc
        raise ValueError("No generation could be completed with available models.")

    def is_available(self) -> bool:
        try:
            if genai is None:
                return False
            genai.list_models()
            return True
        except Exception:
            return False


def get_gemini_client(api_key: Optional[str] = None) -> Optional[GeminiClient]:
    try:
        return GeminiClient(api_key=api_key)
    except Exception as e:
        print(f"Warning: Could not initialize Gemini client: {e}")
        return None


def _extract_text_from_response(resp) -> str:
    """Robustly extract text from various google.generativeai response shapes.
    
    The SDK and API return different structures depending on version and method.
    This tries several common access patterns and returns a best-effort string.
    """
    # 1) object with .text attribute
    try:
        if hasattr(resp, "text"):
            text = getattr(resp, "text", None)
            if text and isinstance(text, str):
                return text.strip()
    except Exception:
        pass

    # 2) object with .candidates and look for text in parts
    try:
        if hasattr(resp, "candidates"):
            candidates = getattr(resp, "candidates", None)
            if candidates and len(candidates) > 0:
                first = candidates[0]
                # Try to get content from first candidate
                if hasattr(first, "content"):
                    content = getattr(first, "content", None)
                    if hasattr(content, "parts"):
                        parts = getattr(content, "parts", None)
                        if parts and len(parts) > 0:
                            text_parts = []
                            for part in parts:
                                if hasattr(part, "text"):
                                    t = getattr(part, "text", None)
                                    if t:
                                        text_parts.append(t)
                            if text_parts:
                                return " ".join(text_parts).strip()
                # Also try dict-style access
                try:
                    if hasattr(first, "get"):
                        content_dict = first.get("content", {})
                        if isinstance(content_dict, dict) and "text" in content_dict:
                            return content_dict["text"].strip()
                except Exception:
                    pass
    except Exception:
        pass

    # 3) dict with 'candidates' list
    try:
        if isinstance(resp, dict) and "candidates" in resp:
            candidates = resp.get("candidates", [])
            if isinstance(candidates, list) and len(candidates) > 0:
                first = candidates[0]
                if isinstance(first, dict):
                    content = first.get("content", {})
                    if isinstance(content, dict):
                        # Look for text in content
                        if "text" in content:
                            return content["text"].strip()
                        # Look for parts in content
                        if "parts" in content:
                            parts = content["parts"]
                            if isinstance(parts, list):
                                text_parts = []
                                for part in parts:
                                    if isinstance(part, dict) and "text" in part:
                                        text_parts.append(part["text"])
                                if text_parts:
                                    return " ".join(text_parts).strip()
    except Exception:
        pass

    # 4) dict with 'output' (list or string)
    try:
        if isinstance(resp, dict) and "output" in resp:
            out = resp.get("output")
            if isinstance(out, list) and len(out) > 0:
                part = out[0]
                if isinstance(part, dict):
                    text = part.get("content") or part.get("text")
                    if text:
                        return text if isinstance(text, str) else str(text)
                return str(part)
            if isinstance(out, str):
                return out
    except Exception:
        pass

    # 5) Fallback: stringify response (as last resort)
    try:
        return str(resp)
    except Exception:
        return ""
