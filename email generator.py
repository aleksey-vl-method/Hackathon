#!/usr/bin/env python3
"""
Basic OpenAI API integration
"""

import os
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

def basic_chat_completion(prompt: str, model: str = "gpt-3.5-turbo"):
    """
    Make a basic chat completion request to OpenAI.
    
    Args:
        prompt: The user prompt/question
        model: OpenAI model to use (default: gpt-3.5-turbo)
    
    Returns:
        The AI response text
    """
    try:
        client = setup_openai_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def generate_text(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000, temperature: float = 0.7):
    """
    Generate text using OpenAI with customizable parameters.
    
    Args:
        prompt: The input prompt
        model: OpenAI model to use
        max_tokens: Maximum tokens to generate
        temperature: Creativity level (0.0-1.0)
    
    Returns:
        Generated text or None if error
    """
    return basic_chat_completion(prompt, model)

def chat_with_system_message(user_prompt: str, system_message: str, model: str = "gpt-3.5-turbo"):
    """
    Chat with a system message to set context/behavior.
    
    Args:
        user_prompt: User's message
        system_message: System message to set AI behavior
        model: OpenAI model to use
    
    Returns:
        AI response or None if error
    """
    try:
        client = setup_openai_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None

def main():
    """Main function to test OpenAI API call."""
    print("OpenAI API Integration Test")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Basic chat")
        print("2. Chat with system message")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            user_prompt = input("Enter your prompt: ").strip()
            if user_prompt:
                print(f"\nSending: {user_prompt}")
                print("-" * 50)
                response = basic_chat_completion(user_prompt)
                if response:
                    print("Response:", response)
                else:
                    print("Failed to get response")
        
        elif choice == "2":
            system_msg = input("Enter system message (sets AI behavior): ").strip()
            user_prompt = input("Enter your prompt: ").strip()
            
            if system_msg and user_prompt:
                print(f"\nSystem: {system_msg}")
                print(f"User: {user_prompt}")
                print("-" * 50)
                response = chat_with_system_message(user_prompt, system_msg)
                if response:
                    print("Response:", response)
                else:
                    print("Failed to get response")
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
