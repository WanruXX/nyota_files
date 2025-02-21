from urllib import response
import openai
import os
import datetime
from openai import OpenAI
import urllib.parse
from dotenv import load_dotenv


def analyze_image(image_url, image_url_example, instruction_text, client):
    print(
        f"Sending API request for image: {image_url} with the instruction: {instruction_text}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction_text[0]},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url_example},
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": """Rainbow Harvest

Garnet beads are round and full, with a deep, alluring wine-red hue, reminiscent of ripe pomegranate seeds. Tourmaline crystals are transparent and vibrant, like a dreamy neon, reflecting brilliant light under illumination.

The combination of these two creates a striking yet harmonious clash of colors, with red and multicolored hues intertwining like a grand jewelry feast, exuding elegance with every movement. Garnet can improve blood circulation and regulate endocrine functions, while tourmaline releases negative ions, balances the body's bioelectricity, and brings positive energy. Wearing them long-term can bring beauty and health to the wearer.

Perfect for: those seeking increased energy, creativity, emotional healing, and spiritual growth through the revitalizing and balancing properties of Garnet.
"""}]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction_text[1]},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        description = response.choices[0].message.content
        # Status message for API response
        print(f"Received caption: {description}")
        return description.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while analyzing the image."


def write_to_file(description, filename, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, f'{filename}.txt')
    # Status message for writing to file
    print(
        f"Writing caption to file: {os.path.join(folder_path, f'{filename}.txt')}")
    with open(file_path, 'w') as file:
        file.write(description)


def process_images(image_urls, instruction_text, output_folder, client):
    all_descriptions = []  # List to hold all descriptions

    # Process each image and collect descriptions
    for i in range(1, len(image_urls)):
        filename = os.path.basename(image_urls[i])
        # Decode URL-encoded characters
        filename = urllib.parse.unquote(filename)
        # Retain the full filename without extension
        filename = os.path.splitext(filename)[0]
        response = analyze_image(image_urls[i], image_urls[0], instruction_text, client)
        write_to_file(response, filename, output_folder)
        all_descriptions.append(
            f"Image: {image_urls[i]}\nCaption: {response}\n\n")
        print("Finish generating ", filename)  # Print status message

    combined_filename = os.path.join(output_folder, "combined_output.txt")

    with open(combined_filename, 'w') as combined_file:
        # Write all descriptions to the file
        combined_file.write("\n".join(all_descriptions))

    # Print status message
    print(
        f"All captions have been combined into the file: {combined_filename}")


def estimate_cost(number_of_images, instruction_text, image_urls):
    # Original fixed cost estimate
    cost_per_image = 0.00765  # $0.00765 per image for the actual vision processing
    total_vision_processing_cost = number_of_images * cost_per_image

    # Additional token-based cost calculation
    cost_per_1K_output_tokens = 0.03  # $0.03 per 1K tokens for output
    cost_per_1K_input_tokens = 0.01   # $0.01 per 1K tokens for input

    # Calculate total input length from instruction text and image URLs
    total_input_text = instruction_text[0] +  instruction_text[1] + " ".join(image_urls)
    total_input_tokens = len(total_input_text) / \
        4  # Rough estimate of token count

    # Assume an average output token count per image
    average_output_tokens_per_image = 120
    total_output_tokens = average_output_tokens_per_image * number_of_images

    # Calculate total cost for input and output tokens
    total_input_token_cost = (
        total_input_tokens / 1000) * cost_per_1K_input_tokens
    total_output_token_cost = (
        total_output_tokens / 1000) * cost_per_1K_output_tokens

    # Sum up all costs
    total_cost = total_vision_processing_cost + \
        total_input_token_cost + total_output_token_cost
    return total_cost


def generate_captions(image_urls, instruction_text, output_folder, client):
    # Calculate the estimated cost including token-based costs
    cost = estimate_cost(len(image_urls), instruction_text, image_urls)
    print("The estimated cost for analyzing (assuming each image is 1024x1024 and you did not enter a crazy instruction)", len(
        image_urls), "images is", cost)
    input_key = input("Would you like to continue?[y/n]: ")

    if input_key == 'y':
        print(
            f"Starting the caption generation process for {len(image_urls)} images.")
        process_images(image_urls, instruction_text, output_folder, client)
    else:
        print("Terminate generation")
        exit()


if __name__ == "__main__":
    load_dotenv()
    client = OpenAI(api_key=os.getenv('API_KEY'))
    url_link_base = "https://raw.githubusercontent.com/WanruXX/nyota_files/refs/heads/main/test0/"
    files_numbers = ["example", "test1", "test2"]
    image_urls = [url_link_base + i + ".jpg?raw=true" for i in files_numbers]
    instruction_text = ["" for _ in range(2)]
    instruction_text[0] = "Please write an introduction for another jwerlry product. Please carefully identify the jewelry type, color, meterial, style and other design features. You also need to write the jewelry's the effects and symbols of meterials, especially phsycologically and spiritually. At last, give me one sentence of what group of people it is perfect for according to its features and effects."
    instruction_text[1] = "Please follow this template and write an introduction for another jwerlry product. Make sure everything is within 900 characters."
    output_folder = "C:\\Users\\wanru.xia\\source\\repos\\nyota_files\\test0"
    generate_captions(image_urls, instruction_text, output_folder, client)
