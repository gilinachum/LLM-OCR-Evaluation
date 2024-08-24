def generate_conversation(bedrock_client,
                          model_id,
                          system_prompts,
                          inference_config,
                          input_image):

    print(f"Generating message with model {model_id}")
    with open(input_image, "rb") as f:
        image = f.read()
    extension = input_image.split(".")[-1]
    if extension == "jpg":
        extension = "jpeg"

    message = {
        "role": "user",
        "content": [
            {
                "image": {
                    "format": extension,
                    "source": {
                        "bytes": image
                    }
                }
            }
        ]
    }

    messages = [message]

    # Send the message.
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        #additionalModelRequestFields=additional_model_fields
    )

    return response

