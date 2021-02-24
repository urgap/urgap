import json

    target_resources_path.mkdir(exist_ok=True)
    for rfile in source_resources_path.glob("**/*"):
        if rfile.is_file() is True:
            target_rfile = Path(
                str(rfile).replace(
            )
                target_rfile.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy(rfile, target_rfile)



        target_json_path = Path(
        )
        if target_json_path.exists() is False:
            shutil.copy(config_json, target_json_path)

