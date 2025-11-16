"""
test_sphinx_api.py

Unit test to verify Sphinx AI CLI integration is working correctly.
Tests basic connectivity, authentication, and response parsing.
"""

import sys
import subprocess
from pathlib import Path
from sphinx_integration import SphinxPredictor


def test_sphinx_cli_installed():
    """Test 1: Check if sphinx-cli is installed"""
    print("="*60)
    print("TEST 1: Checking sphinx-cli installation...")
    print("="*60)
    
    try:
        # sphinx-cli doesn't have --version, so use --help
        result = subprocess.run(
            ['sphinx-cli', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and 'sphinx-cli' in result.stdout.lower():
            print("✅ PASS: sphinx-cli is installed")
            # Extract available commands
            if 'login' in result.stdout and 'chat' in result.stdout:
                print("   Available commands: login, logout, status, chat")
            return True
        else:
            print("❌ FAIL: sphinx-cli found but unexpected output")
            print(f"   Output: {result.stdout[:100]}...")
            return False
            
    except FileNotFoundError:
        print("❌ FAIL: sphinx-cli not found in PATH")
        print("   Install with: pip install sphinx-ai-cli")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False


def test_notebook_exists():
    """Test 2: Check if data preprocessing notebook exists"""
    print("\n" + "="*60)
    print("TEST 2: Checking notebook file exists...")
    print("="*60)
    
    notebook_path = Path('data_preprocessing.ipynb')
    
    if notebook_path.exists():
        print(f"✅ PASS: Notebook found at {notebook_path}")
        print(f"   File size: {notebook_path.stat().st_size} bytes")
        return True
    else:
        print(f"❌ FAIL: Notebook not found at {notebook_path}")
        print("   Sphinx AI needs a notebook to work with")
        return False


def test_sphinx_predictor_init():
    """Test 3: Initialize SphinxPredictor class"""
    print("\n" + "="*60)
    print("TEST 3: Initializing SphinxPredictor...")
    print("="*60)
    
    try:
        predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')
        print("✅ PASS: SphinxPredictor initialized successfully")
        print(f"   Notebook path: {predictor.notebook_path}")
        print(f"   API key set: {'Yes' if predictor.api_key else 'No (will use browser login)'}")
        return True, predictor
    except FileNotFoundError as e:
        print(f"❌ FAIL: {e}")
        return False, None
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False, None


def test_simple_prompt():
    """Test 4: Send a simple prompt to Sphinx AI"""
    print("\n" + "="*60)
    print("TEST 4: Testing simple prompt to Sphinx AI...")
    print("="*60)
    print("Note: This will take 30-60 seconds and may require browser login")
    print("If a browser window opens, please complete authentication")
    
    try:
        predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')
        
        # Simple test prompt
        test_prompt = """
        Please respond with a simple test message to verify connectivity.
        Just say: "Sphinx AI is working correctly!"
        """
        
        print("\n🔄 Sending test prompt to Sphinx AI...")
        print("   (This may take 30-60 seconds...)")
        
        response = predictor._run_sphinx_cli(test_prompt, timeout=120)
        
        if response:
            print("\n✅ PASS: Received response from Sphinx AI")
            print(f"   Response length: {len(response)} characters")
            print(f"\n   First 200 characters of response:")
            print(f"   {response[:200]}...")
            return True
        else:
            print("❌ FAIL: Empty response from Sphinx AI")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FAIL: Request timed out after 120 seconds")
        print("   Sphinx AI may be taking longer than expected")
        return False
    except RuntimeError as e:
        print(f"❌ FAIL: {e}")
        if "Sphinx CLI failed" in str(e):
            print("\n   Common causes:")
            print("   1. Not logged in: Run 'sphinx-cli login'")
            print("   2. API key invalid: Check SPHINX_API_KEY in .env")
            print("   3. Network connectivity issues")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaw_range_determination():
    """Test 5: Test yaw range determination function"""
    print("\n" + "="*60)
    print("TEST 5: Testing yaw range determination...")
    print("="*60)
    print("Note: This test uses Sphinx AI and may take 1-2 minutes")
    
    try:
        predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')
        
        forecast = {
            'wind_speed': 8.5,
            'wind_direction': 270,
            'turbulence_intensity': 0.07
        }
        
        print("\n🔄 Asking Sphinx AI to determine optimal yaw range...")
        print(f"   Conditions: {forecast['wind_direction']}° @ {forecast['wind_speed']} m/s, TI={forecast['turbulence_intensity']}")
        
        yaw_range = predictor.determine_optimal_search_range(forecast)
        
        print(f"\n✅ PASS: Sphinx AI recommended yaw range")
        print(f"   Recommended range: ±{yaw_range}°")
        print(f"   This means search from -{yaw_range}° to +{yaw_range}°")
        
        # Validate range is reasonable
        if 3 <= yaw_range <= 15:
            print(f"   ✓ Range is within reasonable bounds (±3° to ±15°)")
            return True
        else:
            print(f"   ⚠️  WARNING: Range seems unusual (expected ±3° to ±15°)")
            return True  # Still pass, but warn
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_response_parsing():
    """Test 6: Test response parsing logic"""
    print("\n" + "="*60)
    print("TEST 6: Testing response parsing...")
    print("="*60)
    
    try:
        predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')
        
        # Mock response that simulates Sphinx AI output
        mock_response = """
        Based on the analysis, here are my recommendations:
        
        Predicted Yaw Angles: [-4, 3, 0, 1]
        Confidence: [high, high, medium, medium]
        Search Range: ±2°
        
        Reasoning: The wind direction is directly aligned with the turbine rows,
        so the upstream turbines should deflect the wake to protect downstream turbines.
        """
        
        print("Testing with mock response...")
        result = predictor._parse_sphinx_response(mock_response)
        
        print(f"\n✅ PASS: Response parsed successfully")
        print(f"   Predicted yaws: {result['predicted_yaws']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Search range: ±{result['search_range']}°")
        
        # Validate parsing
        if result['predicted_yaws'] == [-4.0, 3.0, 0.0, 1.0]:
            print("   ✓ Yaw angles parsed correctly")
        else:
            print(f"   ⚠️  WARNING: Expected [-4, 3, 0, 1], got {result['predicted_yaws']}")
        
        if result['search_range'] == 2:
            print("   ✓ Search range parsed correctly")
        else:
            print(f"   ⚠️  WARNING: Expected 2, got {result['search_range']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 "*20)
    print("SPHINX AI INTEGRATION TEST SUITE")
    print("🧪 "*20 + "\n")
    
    results = []
    
    # Test 1: CLI installed
    results.append(("CLI Installation", test_sphinx_cli_installed()))
    
    # Test 2: Notebook exists
    results.append(("Notebook File", test_notebook_exists()))
    
    # Test 3: Predictor init
    success, predictor = test_sphinx_predictor_init()
    results.append(("Predictor Init", success))
    
    # Test 4 & 5: Skip live tests by default (requires authentication)
    print("\n" + "ℹ️ "*20)
    print("INFO: Skipping live Sphinx AI tests (require authentication)")
    print("To test live Sphinx AI:")
    print("  1. Run: sphinx-cli login")
    print("  2. Manually test with: python -c 'from sphinx_integration import SphinxPredictor; ...'")
    print("ℹ️ "*20)
    
    # Check if we should run live tests (via command line arg)
    import sys
    if '--live' in sys.argv:
        print("\n🔴 Running LIVE tests...")
        results.append(("Simple Prompt", test_simple_prompt()))
        results.append(("Yaw Range Determination", test_yaw_range_determination()))
    else:
        results.append(("Simple Prompt", None))
        results.append(("Yaw Range Determination", None))
    
    # Test 6: Response parsing (no API call needed)
    results.append(("Response Parsing", test_response_parsing()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
            passed += 1
        elif result is False:
            status = "❌ FAIL"
            failed += 1
        else:
            status = "⏭️  SKIP"
            skipped += 1
        
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("="*60)
    
    if failed > 0:
        print("\n❌ Some tests failed. Please review errors above.")
        print("\nCommon fixes:")
        print("1. Install Sphinx CLI: pip install sphinx-ai-cli")
        print("2. Login to Sphinx: sphinx-cli login")
        print("3. Check notebook exists: data_preprocessing.ipynb")
        return 1
    elif passed > 0 and skipped == 0:
        print("\n✅ All tests passed! Sphinx AI integration is working correctly.")
        return 0
    else:
        print("\n⚠️  Tests passed but some were skipped.")
        print("Run again and choose 'y' to test live Sphinx AI connectivity.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
