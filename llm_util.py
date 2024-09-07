import boto3
import json

def generate_conversation(bedrock_client,
                          model_id,
                          system_prompts,
                          inference_config,
                          input_image):

    print(f"Generating message with model {model_id}")
    # 1) Read the image bytes
    with open(input_image, "rb") as f:
        image_bytes = f.read()
    img_extension = input_image.split(".")[-1]
    if img_extension == "jpg":
        img_extension = "jpeg"

    # 2) Create a message(s) with text or image
    message = {
        "role": "user",
        "content": [
            {
                "image": {
                    "format": img_extension,
                    "source": {
                        "bytes": image_bytes
                    }
                }
            }
        ]
    }

    # 3) Send the message using Converse API (same exact API for different model vendors + naitive tools support)
    response = bedrock_client.converse(
        modelId = model_id,
        messages = [messages,],
        system = system_prompts,
        inferenceConfig = inference_config,
        #additionalModelRequestFields = additional_model_fields
    )

    return response


def get_ocr(test):
    model_id : str = test['model_id']
    input_image : str = test['input_image']
    instructions_filename : str = test['instructions_filename']
    temperature : float = test['temperature']
    
    inference_config = {"temperature": temperature}
    instructions = open(f"./prompts/{instructions_filename}", "r").read()
    system_prompts = [{"text": instructions}]

    bedrock_client = boto3.client('bedrock-runtime',region_name='us-east-1')
    response = generate_conversation(
        bedrock_client, model_id, system_prompts, inference_config, input_image)

    output_message = response['output']['message']

    print(f"Role: {output_message['role']}")

    for content in output_message['content']:
        print(f"Text: {content['text']}")
    

    token_usage = response['usage']
    print(f"Input tokens:  {token_usage['inputTokens']}")
    print(f"Output tokens:  {token_usage['outputTokens']}")
    print(f"Total tokens:  {token_usage['totalTokens']}")
    print(f"Stop reason: {response['stopReason']}")

    return output_message['content'][0]['text']