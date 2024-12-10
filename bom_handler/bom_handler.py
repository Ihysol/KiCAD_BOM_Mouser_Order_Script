import os
import glob, csv
import pandas as pd

from enum import IntEnum

import bom_handler.config as config


class Keys(IntEnum):
    part_part_number = 0
    part_qty = 1
    part_reference = 2
    

class BOMHandler:
    BOM_files = [] # all found bom files
    # target_headers = [config.CSV_MOUSER_COLUMN_NAME, "Qty", "Reference"] # target headers
    
    target_headers = { Keys.part_part_number:config.CSV_MOUSER_COLUMN_NAME, Keys.part_qty:"Qty", Keys.part_reference:"Reference"}
    data_array = []

    def __init__(self, dir_path="", csv_mouser_column_name=config.CSV_MOUSER_COLUMN_NAME):
        self.csv_partnumber_column_name = csv_mouser_column_name    # get user partnumber string from bom ...     
        
        self.target_headers[Keys.part_part_number] = self.csv_partnumber_column_name
        
        if (dir_path == ""):
            self.m_dir_path = os.getcwd()
            self.data_array = {header: [] for header in self.target_headers}
        

    def get_bom_files(self, dir_path=""):
        if(dir_path == ""):
            dir_path = self.m_dir_path
        self.BOM_files = glob.glob(os.path.join(dir_path, '*.csv'))
        return self.BOM_files
    
    def summerize_sorted_items(self, items):
        def get_numerical_part(element):
                return int(''.join(filter(str.isdigit, element)))
        
        ranges = []
        start = end = items[0]

        for i in range(1, len(items)):
            current_num = get_numerical_part(items[i])
            prev_num = get_numerical_part(items[i-1])

            if current_num - prev_num == 1 and items[i][0] == items[i-1][0]:
                end = items[i]
            else:
                if get_numerical_part(start) == get_numerical_part(end):
                    ranges.append(start)
                else:
                    ranges.append(f"{start}-{end}")
                start = end = items[i]

        if get_numerical_part(start) == get_numerical_part(end):
            ranges.append(start)
        else:
            ranges.append(f"{start}-{end}")

        return ", ".join(ranges)       

    def process_bom_file(self, bom_file):       

        header_row_index = None

        with open(bom_file, 'r') as f:
            csv_reader = csv.reader(f, delimiter=config.CSV_DELIMITER)
            for idx, row in enumerate(csv_reader):
                if all(header in row for header in self.target_headers.values()):
                    header_row_index = idx
                    break

        if header_row_index is not None:
            df = pd.read_csv(bom_file, skiprows=header_row_index) # read csv, starting after target headers
            for key, header in self.target_headers.items():
                df[header] = df[header].astype(str).str.strip()     # clear white spaces
                self.data_array[key].extend(df[header].tolist()) # use extend to not get double lists

            
            # note that the CustomerPartNumber given by Reference(s) must be a string and not exceed 22 characters
            for idx, reference in enumerate(self.data_array[Keys.part_reference]):  
                temp = self.summerize_sorted_items(str(reference).split(", "))[:21]       
                if(len(temp)>=21):
                    print(f'{idx}, \"{temp}\" exceeds maximum of 21 characters -> CustomerPartNumber will be cut off at 21th character!') 
                self.data_array[Keys.part_reference][idx] = temp
                
            # print(self.data_array)
            return self.data_array
        else:
            print("Target headers not found in the BOM file.")
            return None