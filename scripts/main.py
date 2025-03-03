from ImageAnalyzer import ImageAnalyzer
from TableDealer import TableDealer
from dotenv import load_dotenv
import subprocess
import os

if __name__ == "__main__":
    
    load_dotenv()
    batch_size = 50
    index = 0
    image_dir = "temp/"
    table_dealer = TableDealer(image_dir=image_dir, index=index)
    
    new_items_file = os.path.join(image_dir, "new_items_" + str(index) + ".json")
    des_added_file = os.path.join(image_dir, "description_added_" + str(index) + ".json")
    
    operation = 3
    
    if operation == 0:
        # add translated names to names.json, compared with local, if existing already
        exit()
    elif operation == 1:
        # download images without english description
        table_dealer.get_new_items(new_items_file, batch_size=batch_size)
        table_dealer.download_images(new_items_file)
    elif operation == 2:
        # generate descriptions and save
        # subprocess.run(["git", "add", ".\\temp\\"])
        # subprocess.run(["git", "commit", "-am", "\"add images\""])
        # subprocess.run(["git", "push"])
        image_analyzer = ImageAnalyzer(image_dir=image_dir, index=index)
        image_analyzer.process_images(new_items_file, des_added_file)
    elif operation == 3:
        # update the table with descriptions  
        table_dealer.update_descriptions(des_added_file)
    
    
   