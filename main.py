import time

# TODO: move logic into gui -> leave only gui here to start
# do setup and run stages?

from mouser import MouserOrderClient
import mouser.config as mouser_config

from bom_handler import BOMHandler

def setup():
    pass    
    
def main(): 
    success = False
    count = 0
    
    while count < mouser_config.API_TIMEOUT_MAX_RETRIES and not success:
        client = MouserOrderClient()
        bom_handler = BOMHandler()
        bom_handler.get_bom_files()
        bom_handler.process_bom_file(bom_handler.BOM_files[0])
        success = client.order_parts_from_data_array(bom_handler.data_array)
        count+=1
        if not success:
            time.sleep(mouser_config.API_TIMEOUT_SLEEP_S)

    print(f"tries:{count} - success: {success}")    
    
if __name__ == "__main__":
    main()

