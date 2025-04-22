import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

# Configure API key from environment variable for security
API_KEY = os.getenv("GEMINI_API_KEY")

print("Loaded API Key:", API_KEY) 
 
if not API_KEY:
    raise ValueError("Error: GEMINI_API_KEY not found. Set it as an environment variable.")

genai.configure(api_key=API_KEY)

def read_code(file_path):
    """Reads the content of a given file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print("Error: File not found.")
        return None

def extract_plantuml(text):
    """Extracts PlantUML code block from the response."""
    match = re.search(r"```plantuml(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        print("No UML diagram found in the response.")
        return None

def generate_flowchart(uml_code):
    """Generates a flowchart from the extracted UML code without saving it."""
    try:
        # Check if PlantUML is installed
        subprocess.run(["plantuml", "-version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("❌ Error: PlantUML is not installed or not in the system path.")
        return None

    output_image = "flowchart.png"

    try:
        # Call PlantUML directly using echo input
        subprocess.run(
            ["plantuml", "-pipe", "-tpng"], 
            input=f"@startuml\n{uml_code}\n@enduml".encode(),
            stdout=open(output_image, "wb"),
            check=True
        )
        print(f"✅ Flowchart generated: {output_image}")

        # Automatically open the generated image
        subprocess.run(["start", output_image], shell=True)  # Windows
        return output_image
    except Exception as e:
        print(f"❌ Error generating flowchart: {e}")
        return None


def send_to_gemini(code):
    """Sends the code to Google Gemini API and extracts the UML diagram in PlantUML syntax."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = f"""
        Here is a Python script:
        ```
        {code}
        ```
        Please generate a **UML flowchart** for this code and provide it in **PlantUML** syntax.
        The response should contain **only** the PlantUML code inside ```plantuml``` fenced blocks.
        """
        response = model.generate_content([prompt])  
        if hasattr(response, "text"):
            plantuml_code = extract_plantuml(response.text)
            if plantuml_code:
                generate_flowchart(plantuml_code)
            else:
                print("❌ No UML diagram found.")
        else:
            print("❌ Error: No valid response received from Gemini.")
    except Exception as e:
        print(f"❌ Error communicating with Gemini: {e}")


def main():
    file_path = "temp.py"  # Change this to the actual file path
    code = read_code(file_path)
    if code:
        send_to_gemini(code)

if __name__ == "__main__":
    main()

