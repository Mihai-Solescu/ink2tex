#!/usr/bin/env python3
"""Test available Gemini models"""

# Read API key first
try:
    with open('.api', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and 'GOOGLE_API_KEY' in line:
                api_key = line.split('=', 1)[1].strip()
                break
    
    print(f"API key: {api_key[:10]}...")
    
    # Test API
    import google.generativeai as genai
    print("Configuring API...")
    genai.configure(api_key=api_key)
    
    print("Listing available models...")
    models = list(genai.list_models())
    for model in models[:10]:  # Show first 10
        print(f"  - {model.name}")
    
    print("Testing model creation...")
    # Try different models
    model_names = [
        'gemini-2.0-flash-exp',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'models/gemini-2.0-flash-exp',
        'models/gemini-1.5-flash'
    ]
    
    for model_name in model_names:
        try:
            print(f"Trying {model_name}...")
            model = genai.GenerativeModel(model_name)
            print(f"  ✓ Success with {model_name}")
            break
        except Exception as e:
            print(f"  ❌ Failed with {model_name}: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
