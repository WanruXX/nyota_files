import os
from openai import OpenAI
from dotenv import load_dotenv
import json

class ImageAnalyzer:
    def __init__(self, image_dir = "temp/", index = 0):
        self.url_main = "https://raw.githubusercontent.com/WanruXX/nyota_files/refs/heads/main/"
        # self.example_image_url = "example/Rainbow%20Harvest.jpg"
#         self.example_text = """Rainbow Harvest

# Garnet beads are round and full, with a deep, alluring wine-red hue, reminiscent of ripe pomegranate seeds. Tourmaline crystals are transparent and vibrant, like a dreamy neon, reflecting brilliant light under illumination.

# The combination of these two creates a striking yet harmonious clash of colors, with red and multicolored hues intertwining like a grand jewelry feast, exuding elegance with every movement. Garnet can improve blood circulation and regulate endocrine functions, while tourmaline releases negative ions, balances the body's bioelectricity, and brings positive energy. Wearing them long-term can bring beauty and health to the wearer.

# Perfect for: those seeking increased energy, creativity, emotional healing, and spiritual growth through the revitalizing and balancing properties of Garnet.
# """
        self.instruction_example = "Please write an introduction for a jwerlry product. Please carefully identify the jewelry type, color, meterial, style and other design features. First, you will give it a beautiful name as the tile. Then you need to describe the features you just indentified. You also need to write the jewelry's the effects and symbols of the meterials and designs, especially phsycologically and spiritually. At last, starting with 'Perfect for:', give me one sentence of what group of people it is perfect for according to its features and effects."
        # self.prompt = "Please follow this template and write an introduction for another jwerlry product. Make sure everything is within 900 characters."
        self.image_sub_dir = image_dir
        self.client = OpenAI(api_key=os.getenv('API_KEY'))
        self.index = index
        

    def get_prompt(self, item_type, image_filename):
        item_type = ""
        if item_type == 'N':
            item_type = "necklace"
        elif item_type == 'B':
            item_type = "bracelet"
        elif item_type == 'E':
            item_type = "earrings"
        elif item_type == 'R':
            item_type = "ring"
        elif item_type == 'P':
            item_type = "bracelet"
        else:
            item_type = "phone strap"
        
        # return f"Please follow this template and write an introduction for the {item_type} in the picture. Make sure everything is within 900 characters."
        return f"Please write an introduction for the {item_type} in the picture with the title {image_filename}. Don't put the title in your answer. You only need to output the body text. Please carefully identify the jewelry's color, meterial, style and other design features and describe the jewelry's excellent appearance, aas well as the symbols and effects of the meterials and designs, especially phsycologically and spiritually. At last, add 'Perfect for:' in another paragraph, give me one sentence of what group of people it is perfect for according to its effects. Don't include anything like someone looking for the good outter appearance. Make sure everything is within 900 characters."
            
    def analyze_image(self, item_type, image_filename):
        print(
            f"Sending API request for image: {image_filename}")
        try:
            iamge_url = self.url_main + self.image_sub_dir + image_filename + ".jpg?raw=true"
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    # {
                    #     "role": "user",
                    #     "content": [
                    #         {"type": "text", "text": self.instruction_example},
                    #         {
                    #             "type": "image_url",
                    #             "image_url": {"url": self.url_main + self.example_image_url},
                    #         },
                    #     ],
                    # },
                    # {
                    #     "role": "assistant",
                    #     "content": [{"type": "text", "text": self.example_text}]
                    # },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.get_prompt(item_type, image_filename)},
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


    def process_images(self, input_items_file, output_items_file):
        image_dir = os.path.join(os.getcwd(), self.image_sub_dir)
        if not os.path.exists(image_dir):
            print("Image dir", image_dir, "doesn't exist")
            exit()
            
        with open(input_items_file, encoding="utf-8") as f:
            new_items = json.load(f)
            print("Loaded", input_items_file, "for processing images")
        
        for item in new_items["items"]:
            filename = item["fields"]["产品名字英文"][0]["text"]
            item_type = item["fields"]["产品品类"]
            out_des_file = os.path.join(self.image_sub_dir, f'{filename}.txt')
            item["fields"]["产品描述英文"] = self.analyze_image(item_type, filename)
            # with open(out_des_file,"r") as f:
            #     item["fields"]["产品描述英文"] = f.read()
            item["fields"]["产品描述英文"] = self.analyze_image(item_type, filename)
            self.write_to_file(out_des_file, item["fields"]["产品描述英文"])
            print("Finish generating ", filename)

        with open(output_items_file, 'w', encoding="utf-8") as combined_file:
            json.dump(new_items, combined_file, indent=4)
            self.index += 1
        print(f"All captions have been combined into: {output_items_file}")


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
