
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logics.script_audio import ScriptGenerator

def test_generate_script():
    print("Testing generate_script...")
    generator = ScriptGenerator()
    
    if not generator.client:
        print("Skipping test: Client not initialized (check API Key).")
        return

    description = "A spacious modern living room with large windows and hardwood floors."
    preference = "Luxury and sophisticated"
    

    result = generator.generate_script(
        property_description=description,
        preference=preference
    )
    print("\n--- Result ---")
    import json
    print(json.dumps(result, indent=2))
    
    # Validation
    if "tour_plan" in result:
            print("\nValidation: 'tour_plan' key found.")
    else:
            print("\nValidation Failed: 'tour_plan' key missing.")

if __name__ == "__main__":
    test_generate_script()
