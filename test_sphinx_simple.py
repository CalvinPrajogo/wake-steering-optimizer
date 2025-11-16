"""
test_sphinx_simple.py

Simple test to verify Sphinx AI API is working with API key authentication.
"""

import os
from dotenv import load_dotenv
from sphinx_integration import SphinxPredictor

# Load environment variables
load_dotenv()

def test_simple_prompt():
    """Test a simple prompt to Sphinx AI"""
    print("="*60)
    print("TESTING SPHINX AI WITH API KEY")
    print("="*60)
    
    # Check if API key is set
    api_key = os.getenv('SPHINX_API_KEY')
    if not api_key:
        print("❌ ERROR: SPHINX_API_KEY not found in .env file")
        return False
    
    print(f"✓ API key loaded: {api_key[:15]}...")
    
    # Initialize predictor with API key
    print("\n1. Initializing SphinxPredictor...")
    try:
        predictor = SphinxPredictor(
            notebook_path='data_preprocessing.ipynb',
            api_key=api_key
        )
        print("   ✓ Predictor initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Send simple test prompt
    print("\n2. Sending test prompt to Sphinx AI...")
    print("   (This may take 30-60 seconds...)")
    
    test_prompt = """
    This is a simple connectivity test.
    Please respond with: "Sphinx AI is working correctly!"
    Then add the current calculation: 2 + 2 = ?
    """
    
    try:
        response = predictor._run_sphinx_cli(test_prompt, timeout=120)
        
        if response:
            print("\n✅ SUCCESS! Received response from Sphinx AI")
            print("\n" + "="*60)
            print("RESPONSE:")
            print("="*60)
            print(response)
            print("="*60)
            return True
        else:
            print("\n❌ FAIL: Empty response")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaw_prediction():
    """Test yaw angle prediction with actual forecast data"""
    print("\n\n" + "="*60)
    print("TESTING YAW ANGLE PREDICTION")
    print("="*60)
    
    api_key = os.getenv('SPHINX_API_KEY')
    if not api_key:
        print("❌ ERROR: SPHINX_API_KEY not found")
        return False
    
    print("\n1. Initializing predictor...")
    try:
        predictor = SphinxPredictor(
            notebook_path='data_preprocessing.ipynb',
            api_key=api_key
        )
        print("   ✓ Predictor initialized")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test forecast
    forecast = {
        'wind_speed': 8.5,
        'wind_direction': 270,
        'turbulence_intensity': 0.07,
        'temperature': 15
    }
    
    print(f"\n2. Testing with forecast conditions:")
    print(f"   Wind: {forecast['wind_direction']}° @ {forecast['wind_speed']} m/s")
    print(f"   Turbulence: {forecast['turbulence_intensity']*100:.0f}%")
    print(f"   Temperature: {forecast['temperature']}°C")
    
    print("\n3. Asking Sphinx AI to predict optimal yaw angles...")
    print("   (This may take 1-2 minutes...)")
    
    try:
        prediction = predictor.predict_yaw_angles(forecast)
        
        print("\n✅ SUCCESS! Prediction received")
        print("\n" + "="*60)
        print("PREDICTION RESULTS:")
        print("="*60)
        print(f"Predicted Yaw Angles: {prediction['predicted_yaws']}")
        print(f"  T0 (upstream left):  {prediction['predicted_yaws'][0]:+.0f}°")
        print(f"  T1 (upstream right): {prediction['predicted_yaws'][1]:+.0f}°")
        print(f"  T2 (downstream left): {prediction['predicted_yaws'][2]:+.0f}°")
        print(f"  T3 (downstream right): {prediction['predicted_yaws'][3]:+.0f}°")
        
        print(f"\nConfidence Levels: {prediction['confidence']}")
        print(f"Recommended Search Range: ±{prediction['search_range']}°")
        
        if prediction['reasoning']:
            print(f"\nReasoning:")
            print(f"  {prediction['reasoning'][:300]}...")
        
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🔬 SPHINX AI SIMPLE TEST\n")
    
    # Test 1: Simple prompt
    success1 = test_simple_prompt()
    
    # Test 2: Yaw prediction (only if test 1 passed)
    if success1:
        success2 = test_yaw_prediction()
    else:
        print("\n⏭️  Skipping yaw prediction test (simple prompt failed)")
        success2 = False
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if success1:
        print("✅ Simple Prompt: PASS")
    else:
        print("❌ Simple Prompt: FAIL")
    
    if success2:
        print("✅ Yaw Prediction: PASS")
    elif success1:
        print("❌ Yaw Prediction: FAIL")
    else:
        print("⏭️  Yaw Prediction: SKIPPED")
    
    print("="*60)
    
    if success1 and success2:
        print("\n🎉 All tests passed! Sphinx AI integration is working!")
    elif success1:
        print("\n⚠️  Basic connectivity works but yaw prediction failed")
    else:
        print("\n❌ Tests failed. Check your SPHINX_API_KEY in .env file")
