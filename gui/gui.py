import os

import dearpygui.dearpygui as dpg
import gui.config as config



class Timer:
    # track dpg time since last render
    
    def __init__(self, interval):
        self.total_time = dpg.get_total_time()
        self.last_total_time =dpg.get_total_time()
        self.interval = interval
        
    def update(self):
        self.total_time = dpg.get_total_time()
        delta_time = dpg.get_total_time() - self.last_total_time()
        if delta_time > self.interval:
            self.last_total_time = self.total_time
            return True
        return False

# Callback function for button click
def on_button_click(sender, app_data, user_data):
    pass
    #start_bom_processing()
    
def callback(sender, app_data):
    print("ok clicked")
    dpg.set_value(item="path_input", value=app_data['file_path_name'])
    
def cancel_callback(sender, app_data):
    print("cancel was clicked")

def gui(app_state):
    dpg.create_context()

    dpg.add_file_dialog(
        directory_selector=True, show=False, callback=callback, tag="file_dialog_id",
        cancel_callback=cancel_callback, width=600 ,height=400
    )

    with dpg.window(tag="Primary Window", autosize=True):                    
        
        with dpg.group(horizontal=True):
            dpg.add_text("Directory ")
            dpg.add_input_text(auto_select_all=True, ctrl_enter_for_new_line=False, default_value=os.getcwd(), tag="path_input")
            dpg.add_button(label="select..", callback=lambda: dpg.show_item("file_dialog_id"))
        
        with dpg.group(horizontal=True):
            dpg.add_text("Mouser Part Number Keyword: ")
            dpg.add_input_text(width=300, default_value="MPN", tag="mouser_part_number_keyword")
            dpg.add_button(label="start processing BOM", callback=on_button_click)
        
        with dpg.group(horizontal=True):
            dpg.add_text("log:")
            dpg.add_input_text(multiline=True, height=100, default_value="waiting for user input...", enabled=False)
            
    with dpg.window(tag="test"):
        with dpg.group(horizontal=True):
            dpg.add_text("thats average")
            
            
    # styleing 
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 80, 20), category=dpg.mvThemeCat_Core)   
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 255, 0), category=dpg.mvThemeCat_Core)            
    dpg.bind_theme(global_theme)

    dpg.create_viewport(title='KiCAD Mouser Order Tool', decorated=False)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
    
    