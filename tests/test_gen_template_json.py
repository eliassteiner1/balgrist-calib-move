import os 
import sys
import json
from   glob import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from   calib_move.core.generatejson import main_generate_json



if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
        
    argv = [
        "--vid-folder-path", "H:/code_bal/VISCERAL_DATASET_REC_A/internal_calibration"
    ]
    main_generate_json(argv=argv)
    
    

    # with open("test.json", mode="w", encoding="utf-8") as file:
    #     json.dump(somedata, file, indent=4)
        
    # with open("tests/static_window_test.json", mode="r", encoding="utf-8") as file:
    #     read_data = json.load(file)

    

