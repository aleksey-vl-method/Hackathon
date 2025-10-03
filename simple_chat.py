#!/usr/bin/env python3
"""
Simple OpenAI chat with automatic prompts context loading
"""

import os
import glob
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI

def setup_openai_client():
    """Setup OpenAI client with API key from environment variables."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key)
    return client

def load_prompts_context(prompts_dir: str = "./prompts") -> str:
    """Load ALL text files from prompts directory and return as context string."""
    context_parts = []
    
    if not os.path.exists(prompts_dir):
        print(f"Prompts directory '{prompts_dir}' not found.")
        return ""
    
    pattern = os.path.join(prompts_dir, "*.txt")
    txt_files = glob.glob(pattern)
    
    if not txt_files:
        print(f"No .txt files found in '{prompts_dir}'")
        return ""
    
    print(f"Loading ALL context from {len(txt_files)} files in prompts directory:")
    
    context_parts.append("=== CONTEXT INFORMATION ===")
    
    total_chars = 0
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                filename = os.path.basename(file_path)
                content = f.read().strip()
                if content:
                    context_parts.append(f"\n--- {filename.upper()} ---")
                    context_parts.append(content)
                    total_chars += len(content)
                    print(f"  ✓ {filename} ({len(content)} characters)")
                else:
                    print(f"  ⚠ {filename} (empty file)")
        except Exception as e:
            print(f"  ✗ Error reading {file_path}: {str(e)}")
    
    context_parts.append("\n=== END OF CONTEXT ===\n")
    
    print(f"Total context loaded: {total_chars} characters")
    return "\n".join(context_parts)

def chat_with_context(user_prompt: str, model: str = "gpt-4-turbo"):
    """Chat with OpenAI using prompts context."""
    try:
        client = setup_openai_client()
        
        # Load context
        context = load_prompts_context()
        
        # Combine context with user prompt
        if context:
            full_prompt = f"{context}\n\nBased on the above context, please respond to: {user_prompt}"
        else:
            full_prompt = user_prompt
            print("No context loaded, using prompt without context")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def main():
    """Automatically generate content with prompts context."""
    print("Auto-generating content with prompts context...")
    print("=" * 50)
    
    # Default prompt - you can change this or make it configurable
    default_prompt = "Generate a phishing email for cybersecurity awareness training"
    
    print(f"Using prompt: {default_prompt}")
    print("-" * 50)
    
    response = chat_with_context(default_prompt)
    
    if response:
        print("\nGenerated Content:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
        # Optionally save to file
        output_filename = "generated_content.txt"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f"Generated Content\n")
                f.write(f"Prompt: {default_prompt}\n")
                f.write(f"Generated on: {str(os.getcwd())}\n")
                f.write("=" * 50 + "\n\n")
                f.write(response)
            print(f"\n✓ Content saved to: {output_filename}")
        except Exception as e:
            print(f"✗ Error saving file: {str(e)}")
    else:
        print("✗ Failed to generate content")

if __name__ == "__main__":
    main()
