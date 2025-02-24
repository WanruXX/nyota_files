from ImageAnalyzer import ImageAnalyzer
from TableDealer import TableDealer
from dotenv import load_dotenv


if __name__ == "__main__":
    batch_size = 1
    index = 0
    
    load_dotenv()
    num_new_items = batch_size
    
    while num_new_items == batch_size:
        table_dealer = TableDealer(index=index)
        new_items = table_dealer.getNewItems(batch_size=batch_size)
        num_new_items = len(new_items)
        
        if num_new_items > 0:
            image_filenames = table_dealer.downloadImages(new_items)
            image_analyzer = ImageAnalyzer(index=index)
            image_analyzer.generate_captions(image_filenames)
    
   