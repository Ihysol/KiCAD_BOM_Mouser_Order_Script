import gradio as gr
import pandas as pd
import time

from mouser import MouserOrderClient
import mouser.config as mouser_config

from bom_handler import BOMHandler

class OrderTool:
    def __init__(self):
        self.gui = None
        self.client = None
        self.bom_handler = None
        
    def get_part_json_from_bom(self, file, input_string):
        ''' function to create json from bom '''
        if file is None:
            return [None, None, "Please upload file."]
        if input_string is None or input_string == "":
            return [None, None, "Please enter name of column for part number."]
        try:
            self.client = MouserOrderClient()
            self.bom_handler = BOMHandler(csv_mouser_column_name=input_string)    
            
            self.bom_handler.process_bom_file(file)
            self.part_json = self.client.json_from_data_array(self.bom_handler.data_array)
            return [self.part_json, self.df_from_json(self.part_json), f"JSON created, parts loaded!"]
        except Exception as e:
            return [None, None,  f"Error creating json from bom: {str(e)}"]
        
    def order_parts_from_json(self, json):
        ''' function to order part json from mouser'''
        success = False
        count = 0
        try:
            while count < mouser_config.API_TIMEOUT_MAX_RETRIES and not success:
                success = self.client.order_parts_from_json(json)         
                count+=1
                if not success:
                    time.sleep(mouser_config.API_TIMEOUT_SLEEP_S)
                        
        except Exception as e:
            return f"Error processing file: {str(e)}"

        return f"tries:{count} - success: {success}"
        
    def df_from_json(self, parts_json):
        ''' reformat json to display on site'''
        try:
            df = pd.DataFrame(parts_json)
            df.insert(0, "Select", True)
            return df
        except Exception as e:
            return f"Error {str(e)}"

        
    def run(self):
        # Gradio interface
        with gr.Blocks() as application:
            gr.Markdown("# BOM Processor Tool")
            
            with gr.Column():
                file_input = gr.File(label="Upload .BOM-File", type="filepath")
                input_string = gr.Textbox(label="Name of Column in BOM for part number", placeholder="Enter column name of part number in csv...", value="MNR")
                load_json = gr.Button("Load JSON", interactive=True)
                json_state = gr.State()
                log_output = gr.Textbox(label="Info Log", interactive=False)
                order_button = gr.Button("Order Parts", visible=True)
                parts_list = gr.DataFrame(label="Parts List", interactive=True, visible=True)
            
            # load part button event
            load_json.click(self.get_part_json_from_bom, inputs=[file_input, input_string], outputs=[json_state, parts_list, log_output])
            
            # order part button event
            order_button.click(self.order_parts_from_json, inputs=[json_state], outputs=[log_output])

        # Launch the application
        application.launch()
    
def main(): 
    tool = OrderTool()
    tool.run()
    
if __name__ == "__main__":
    main()



