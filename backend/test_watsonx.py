"""Test WatsonX AI integration"""
import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

def test_watsonx_connection():
    """Test basic WatsonX connection and text generation"""
    
    api_key = os.getenv("WATSONX_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    
    print("=" * 60)
    print("WATSONX AI CONNECTION TEST")
    print("=" * 60)
    print(f"API Key: {api_key[:10]}... (hidden)")
    print(f"Project ID: {project_id}")
    print(f"URL: {url}")
    print()
    
    if not api_key or not project_id:
        print("❌ ERROR: Missing WatsonX credentials!")
        print("Please set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env")
        return False
    
    try:
        # Initialize model
        print("Initializing WatsonX model...")
        
        credentials = {
            "url": url,
            "apikey": api_key
        }
        
        parameters = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 100,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.TEMPERATURE: 0.3,
        }
        
        model = Model(
            model_id="meta-llama/llama-3-3-70b-instruct",
            params=parameters,
            credentials=credentials,
            project_id=project_id
        )
        
        print("✅ Model initialized successfully!")
        print()
        
        # Test simple prompt
        print("Testing text generation...")
        prompt = "Say 'Hello from WatsonX!' in a friendly way."
        
        response = model.generate_text(prompt=prompt)
        
        print("✅ Text generation successful!")
        print()
        print("Prompt:", prompt)
        print("Response:", response)
        print()
        print("=" * 60)
        print("✅ WATSONX AI IS WORKING CORRECTLY!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR: WatsonX connection failed!")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("1. Invalid API key or Project ID")
        print("2. Wrong region URL")
        print("3. Project not properly set up in IBM Cloud")
        print()
        print("Please check your credentials and try again.")
        return False

if __name__ == "__main__":
    test_watsonx_connection()
