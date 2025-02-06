from fastapi import FastAPI, UploadFile
import base64
import json
import uvicorn
from groq import Groq

app = FastAPI()

# Function to encode the image if it's not already in base64
def encode_image(image_file):
    try:
        # Attempt to decode the image as base64
        base64.b64decode(image_file)
        return image_file  # If decoding succeeds, it's already base64
    except:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Initialize the Groq client
client = Groq(api_key="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")

@app.post('/extract_text')
async def extract_text(image_file: UploadFile):
    try:
        # Encode the image if necessary
        base64_image = encode_image(image_file.file)

        # Request to extract only the raw text from the image
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract only the raw text from the image in JSON format."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Extract the response and clean up unnecessary content
        response = completion.choices[0].message.content.strip()

        # Clean up the response (removing markdown and any non-JSON related text)
        start_index = response.find("{")
        end_index = response.rfind("}") + 1

        # Extract only the valid JSON content
        json_content = response[start_index:end_index]

        # Attempt to parse the extracted JSON
        extracted_json = json.loads(json_content)

        # Format the response into the required structure
        formatted_response = {
            "status": "success",
            "extracted_lines": extracted_json
        }
        
        return formatted_response

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
