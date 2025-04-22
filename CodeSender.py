
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

# Configure API key from environment variable for security
API_KEY = os.getenv("GEMINI_API_KEY")

 
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
    """Extracts PlantUML code block from the response and removes incorrect formatting."""
    match = re.search(r"```plantuml(.*?)```", text, re.DOTALL)
    if match:
        plantuml_code = match.group(1).strip()
        # Remove incorrect markdown artifacts
        plantuml_code = plantuml_code.replace("```", "").strip()
        return plantuml_code
    else:
        print("No UML diagram found in the response.")
        return None
def generate_flowchart(uml_code):
    """Generates a flowchart from the extracted UML code correctly."""
    try:
        # Ensure PlantUML is installed
        subprocess.run(["java", "-jar", "C:\\Mermaid\\plantuml-1.2025.1.jar", "-version"], check=True)
    except FileNotFoundError:
        print("❌ Error: PlantUML is not installed or not in the system path.")
        return None

    uml_file = "answer.uml"
    output_image = "output.png"
    # uml_file = "temp.uml"
    # output_image = "flowchart.png"

    try:
        # Ensure UML code is valid
        if not uml_code.strip():
            print("❌ Error: UML code is empty!")
            return None

        # ✅ Remove duplicate @startuml and @enduml if present
        uml_code = re.sub(r'@startuml', '', uml_code).strip()  # Remove extra @startuml
        uml_code = re.sub(r'@enduml', '', uml_code).strip()  # Remove extra @enduml

        # ✅ Ensure exactly one @startuml and @enduml
        clean_uml_code = f"@startuml\n{uml_code}\n@enduml"

        # ✅ Create and write cleaned UML code to temp.uml
        with open(uml_file, "w") as f:
            f.write(clean_uml_code)

        print("\n📜 Cleaned UML Code (temp.uml):")
        print("=" * 40)
        print(clean_uml_code)
        print("=" * 40, "\n")

        # Confirm that the file was created
        if not os.path.exists(uml_file):
            print("❌ Error: temp.uml was not created!")
            return None

        print("🔄 Generating flowchart using PlantUML...")

        # Generate PNG using PlantUML
        result = subprocess.run(
            ["java", "-jar", "C:\\Mermaid\\plantuml-1.2025.1.jar", "-tpng", uml_file, "-o", "."],
            capture_output=True, text=True
        )

        # Check if the command executed successfully
        if result.returncode != 0:
            print("❌ PlantUML Error:", result.stderr)
            return None

        # Verify if PNG was generated
        if not os.path.exists(output_image):
            print(".")
            return None

        print(f"✅ Flowchart generated: {output_image}")

        # Automatically open the generated image
        os.startfile(output_image)  # Windows
        return output_image
    except Exception as e:
        print(f"Not Error: {e}")
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
        **Example response format:**
        ```
        ```plantuml
        start
        :Read input;
        :Process Data;
        :Generate output;
        stop
        ```
        ```
        Ensure the response contains **only** the PlantUML code inside ```plantuml``` fenced blocks.
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
    file_path = "hello.py"  # Change this to the actual file path
    code = read_code(file_path)
    if code:
        send_to_gemini(code)

if __name__ == "__main__":
    main()
