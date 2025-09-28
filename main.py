#!/usr/bin/env python3
"""
CV Sorting System using Free-Tier LLMs
Main entry point for the application
"""

import streamlit as st
import sys
import os
from pathlib import Path


import os
import yaml
from dotenv import load_dotenv # Need to install: pip install python-dotenv

# --- CRITICAL STEP 1: Load environment variables from .env file ---
# This makes the variables accessible via os.environ
load_dotenv() 

def load_config(config_path='config.yaml'):
    """
    Loads the YAML configuration and substitutes API key environment variable names
    with their actual values from the environment.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        return None

    # --- CRITICAL STEP 2: Securely inject API keys ---
    providers = config.get('llm', {}).get('providers', [])
    for provider in providers:
        # Get the name of the environment variable defined in the config
        env_var_name = provider.pop('api_key_env_var', None)

        if env_var_name:
            # Look up the actual key value from the environment (loaded from .env)
            actual_api_key = os.getenv(env_var_name)
            
            if not actual_api_key:
                print(f"Warning: API Key for {provider['name']} not found in environment variable '{env_var_name}'.")

            # Add the actual key back to the dictionary under the expected field name
            # You might need to adjust 'api_key' depending on how your LLM wrapper expects it.
            provider['api_key'] = actual_api_key
        
    return config

# Example Usage:
app_config = load_config()

if app_config:
    # Example: Check the Hugging Face provider entry
    hf_provider = app_config['llm']['providers'][1] 
    
    # This will now contain the loaded token (or None if not found)
    # The original 'api_key_env_var' is gone, replaced by 'api_key'
    print(f"HuggingFace API Key status: {'Loaded' if hf_provider['api_key'] else 'Missing'}")
    
    # Now you can use app_config securely in the rest of your application.

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.streamlit_app import main as streamlit_main


def main():
    """Main entry point"""
    try:
        # Set up environment
        setup_environment()
        
        # Run Streamlit app
        streamlit_main()
        
    except Exception as e:
        st.error(f"Application startup error: {e}")
        st.stop()

def setup_environment():
    """Setup required directories and check dependencies"""
    
    # Create required directories
    directories = ['data/sample_resumes', 'data/sample_jobs', 'outputs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Check for required environment variables
    required_env_vars = ['OPENROUTER_API_KEY', 'HUGGINGFACE_API_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        st.warning(f"Missing environment variables: {', '.join(missing_vars)}. Please configure in Settings page.")

if __name__ == "__main__":
    main()