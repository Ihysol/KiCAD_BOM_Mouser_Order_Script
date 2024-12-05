import os

import dearpygui.dearpygui as dpg
import gui.config as config

from datetime import datetime

class Timer:
    """ timer function to trigger actions periodically """    
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
    
    
# TODO: add timer to GUI to periodically update variables instead of always 
#       add update_variables() in each function that modifies variables
    
class GUI():
    
    def __init__(self, button_func):
        """ prepare all variables """
        self.process_bom_func = button_func
        self.log = ""
        self.bom_dir = None
        self.mpn_keyword = None
        
        self.start() # start gui rendering
        
    def resize_callback(self, sender, user_data):
        window_width = dpg.get_item_width("Primary Window")
        
        dpg.set_item_width("directory_selection_group", window_width*0.4)
        dpg.set_item_width("mpn_group", window_width*0.4)
        dpg.set_item_width("info_log_group", window_width*0.8)
        
        dpg.set_item_indent("directory_selection_group", window_width*0.1)
        dpg.set_item_indent("mpn_group", window_width*0.1)
        dpg.set_item_indent("info_log_group", window_width*0.1)
        
    def start(self):
        """ start to render the gui """
        dpg.create_context()
        
        with dpg.value_registry():
            dpg.add_string_value(default_value=os.getcwd(), tag="bom_dir")
            dpg.add_string_value(default_value="MPN", tag="mpn_keyword")

        dpg.add_file_dialog(
            directory_selector=True, show=False, callback=self.bom_dir_ok_callback, tag="file_dialog_id",
            cancel_callback=self.bom_dir_cancel_callback, width=600 ,height=400
        )

        with dpg.window(tag="Primary Window", autosize=True):                    
            
            # directory selection
            dpg.add_text("Directory ")
            with dpg.group(horizontal=True, tag="directory_selection_group"):
                dpg.add_input_text(auto_select_all=True, ctrl_enter_for_new_line=False, default_value=dpg.get_value("bom_dir"), tag="bom_dir_input", callback=lambda: self.update_variables())
                dpg.add_button(label="select..", callback=lambda: dpg.show_item("file_dialog_id"))
            
            dpg.add_text("Mouser Part Number Keyword: ")
            # mpn and start bom processing button
            with dpg.group(horizontal=True, tag="mpn_group"):
                dpg.add_input_text(width=300, default_value=dpg.get_value("mpn_keyword"), tag="mpn_keyword_input", callback=lambda: self.mpn_keyword_on_change())
                dpg.add_button(label="start processing BOM", callback= lambda: self.process_bom_func(dpg.get_value("bom_dir")))
            
            dpg.add_text("log:")
            # user info log
            with dpg.group(horizontal=True, tag="info_log_group"):
                dpg.add_input_text(multiline=True, width=dpg.get_item_width("Primary Window")-20 , default_value="waiting for user input...", enabled=False, tag="log_field")                
                
        # styling 
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 80, 20), category=dpg.mvThemeCat_Core)   
                dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 255, 0), category=dpg.mvThemeCat_Core)            
        dpg.bind_theme(global_theme)
        
        
        dpg.set_viewport_resize_callback(self.resize_callback)

        # neccessary evil :P
        dpg.create_viewport(title='KiCAD Mouser Order Tool', decorated=True, resizable=True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        self.update_variables()
        
    def bom_dir_ok_callback(self, sender, app_data):
        dpg.set_value(item="bom_dir", value=app_data['file_path_name'])
        dpg.set_value(item="bom_dir_input", value=dpg.get_value("bom_dir"))
        self.update_log(f'[{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}] search path for .BOM-file(s) set to: "{dpg.get_value("bom_dir")}"')
        self.update_variables()
        
    def bom_dir_cancel_callback(self, sender, app_data):
        pass
    
    def update_log(self, log_data):
        self.log += f'{log_data}\n'
        dpg.set_value("log_field", self.log)
    
    def update_variables(self):
        print("DEBUG - Variables updated")
        self.bom_dir = dpg.get_value("bom_dir_input")
        self.mpn_keyword = dpg.get_value("mpn_keyword")

    def mpn_keyword_on_change(self):
        dpg.set_value("mpn_keyword", dpg.get_value("mpn_keyword_input"))
        self.update_variables()
        