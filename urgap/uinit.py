import json


        target_json_path = Path(
        )
        if target_json_path.exists() is False:
            shutil.copy(config_json, target_json_path)

