import os
from openai import OpenAI
from dotenv import load_dotenv
import json

class ImageAnalyzer:
    def __init__(self, image_dir = "temp/", index = 0):
        self.url_main = "https://raw.githubusercontent.com/WanruXX/nyota_files/refs/heads/main/"
        self.example_image_url = "example/Rainbow%20Harvest.jpg"
        self.example_text = """Rainbow Harvest

Garnet beads are round and full, with a deep, alluring wine-red hue, reminiscent of ripe pomegranate seeds. Tourmaline crystals are transparent and vibrant, like a dreamy neon, reflecting brilliant light under illumination.

The combination of these two creates a striking yet harmonious clash of colors, with red and multicolored hues intertwining like a grand jewelry feast, exuding elegance with every movement. Garnet can improve blood circulation and regulate endocrine functions, while tourmaline releases negative ions, balances the body's bioelectricity, and brings positive energy. Wearing them long-term can bring beauty and health to the wearer.

Perfect for: those seeking increased energy, creativity, emotional healing, and spiritual growth through the revitalizing and balancing properties of Garnet.
"""
        self.instruction_example = "Please write an introduction for a jwerlry product. Please carefully identify the jewelry type, color, meterial, style and other design features. First, you will give it a beautiful name as the tile. Then you need to describe the features you just indentified. You also need to write the jewelry's the effects and symbols of the meterials and designs, especially phsycologically and spiritually. At last, starting with 'Perfect for:', give me one sentence of what group of people it is perfect for according to its features and effects."
        # self.prompt = "Please follow this template and write an introduction for another jwerlry product. Make sure everything is within 900 characters."
        self.image_sub_dir = image_dir
        self.client = OpenAI(api_key=os.getenv('API_KEY'))
        self.index = index
        

    def get_prompt(self, image_filename):
        item_type = ""
        if image_filename[0] == 'N':
            item_type = "necklace"
        elif image_filename[0] == 'B':
            item_type = "bracelet"
        elif image_filename[0] == 'E':
            item_type = "earings"
        elif image_filename[0] == 'R':
            item_type = "ring"
        elif image_filename[0] == 'P':
            item_type = "bracelet"
        else:
            item_type = "phone strap"
        
        return f"Please follow this template and write an introduction for the {item_type} in the picture. Make sure everything is within 900 characters."
            
    def analyze_image(self, image_filename):
        print(
            f"Sending API request for image: {image_filename}")
        try:
            iamge_url = self.url_main + self.image_sub_dir + image_filename + "?raw=true"
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.instruction_example},
                            {
                                "type": "image_url",
                                "image_url": {"url": self.url_main + self.example_image_url},
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": self.example_text}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.get_prompt(image_filename)},
                            {
                                "type": "image_url",
                                "image_url": {"url": iamge_url},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            description = response.choices[0].message.content
            print("Received caption for", image_filename)
            return description.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while analyzing the image."


    def write_to_file(self, image_full_path, description):
        print(f"Writing description to file: {image_full_path}")
        with open(image_full_path, 'w') as file:
            file.write(description)


    def process_images(self, item_iamges):
        image_dir = os.path.join(os.getcwd(), self.image_sub_dir)
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        output_data = []
        for record_id, filename in item_iamges.items():
            response = self.analyze_image(filename)
            image_full_path = os.path.join(self.image_sub_dir, f'{filename}.txt')
            self.write_to_file(image_full_path, response)
            found = response.find("\n")
            output_data.append({
                "image:":filename,
                "title:": response[0:found].strip('*'),
                "description": response[found+1:].strip('\n'),
                "record_id": record_id
                })
            print("Finish generating ", filename)

        combined_filename = os.path.join(image_dir, "description_output_" + str(self.index) + ".json")
        with open(combined_filename, 'w') as combined_file:
            json.dump(output_data, combined_file, indent=4)
            self.index += 1
        print(f"All captions have been combined into: {combined_filename}")
        
        return output_data


    def estimate_cost(self, image_filenames):
        n = len(image_filenames)
        
        # Original fixed cost estimate
        cost_per_image = 0.00765  # $0.00765 per image for the actual vision processing
        total_vision_processing_cost = n * cost_per_image

        # Additional token-based cost calculation
        cost_per_1K_output_tokens = 0.03  # $0.03 per 1K tokens for output
        cost_per_1K_input_tokens = 0.01   # $0.01 per 1K tokens for input

        # Calculate total input length from instruction text and image URLs
        total_input_text1 = (self.instruction_example + self.prompt + self.url_main + self.image_sub_dir)
        totle_input_text2 = " ".join(image_filenames)
        total_input_tokens = (len(total_input_text1) * n + len(totle_input_text2)) / 4  # Rough estimate of token count

        # Assume an average output token count per image
        average_output_tokens_per_image = 120
        total_output_tokens = average_output_tokens_per_image * n

        # Calculate total cost for input and output tokens
        total_input_token_cost = (total_input_tokens / 1000) * cost_per_1K_input_tokens
        total_output_token_cost = (total_output_tokens / 1000) * cost_per_1K_output_tokens

        # Sum up all costs
        total_cost = total_vision_processing_cost + total_input_token_cost + total_output_token_cost
        return total_cost


    # def generate_descriptions(self, item_iamges):
    #     self.process_images(item_iamges)
        # cost = self.estimate_cost(image_filenames)
        # print("The estimated cost for analyzing (assuming each image is 1024x1024 and you did not enter a crazy instruction)", len(
        #     image_filenames), "images is", cost)
        # input_key = input("Would you like to continue?[y/n]: ")
        # if input_key == 'y':
        #     self.process_images(item_iamges)
        # else:
        #     print("Terminate generation")
        #     exit()
