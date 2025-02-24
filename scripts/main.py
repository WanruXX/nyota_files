from ImageAnalyzer import ImageAnalyzer
from TableDealer import TableDealer
from dotenv import load_dotenv
import subprocess

if __name__ == "__main__":
    batch_size = 50
    index = 0
    
    load_dotenv()
    n_new_items = batch_size
    table_dealer = TableDealer(index=index)
    image_analyzer = ImageAnalyzer(index=index)
    
    while n_new_items == batch_size:
        new_items = table_dealer.get_new_items(batch_size=batch_size)
        n_new_items = len(new_items)
        
        if n_new_items > 0:
            item_iamges = table_dealer.download_images(new_items)
            
            # subprocess.run(["git", "add", ".\\temp\\"])
            # subprocess.run(["git", "commit", "-am", "\"add images\""])
            # subprocess.run(["git", "push"])
            
            descriptions = image_analyzer.process_images(item_iamges)
            table_dealer.update_descriptions(descriptions)
    
   