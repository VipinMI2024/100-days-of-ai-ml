from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('GEMINI_API_KEY (first 6 chars):', api_key[:6] + '...' if api_key else None)

try:
    import google.generativeai as genai
except Exception as e:
    print('ERROR: could not import google.generativeai:', e)
    raise

try:
    genai.configure(api_key=api_key)
    models = genai.list_models()
    print('\nFound models:')
    for m in models:
        # Try to extract a name and available attributes
        try:
            name = getattr(m, 'name', None)
        except Exception:
            name = None
        if not name and isinstance(m, dict):
            name = m.get('name')
        print('---')
        print('raw:', m)
        print('name:', name)
        # print common attrs
        for attr in ('display_name', 'capabilities', 'methods'):
            val = None
            try:
                val = getattr(m, attr)
            except Exception:
                if isinstance(m, dict):
                    val = m.get(attr)
            if val is not None:
                print(f'{attr}:', val)
except Exception as e:
    print('ERROR calling list_models():', e)
    raise

