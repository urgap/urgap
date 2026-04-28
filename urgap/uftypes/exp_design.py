import types

exp_design = types.SimpleNamespace()
exp_design.ANY = "exp_design.ANY"

exp_design.input = types.SimpleNamespace()
exp_design.input.ANY = "exp_design.input.ANY"
exp_design.input.UTMX_METADATA_XLSX = ".utmx_metadata.xlsx"
exp_design.input.PX_METADATA_JSON = ".px_metadata.json"
exp_design.input.NGS_METADATA_JSON = ".ngs_metadata.json"
exp_design.input.TEST_METADATA_JSON = ".test_metadata.json"
exp_design.input.FLOWCYTO_METADATA_XLSX = ".flowcyto_metadata.xlsx"

exp_design.output = types.SimpleNamespace()
exp_design.output.ANY = "exp_design.output.ANY"
exp_design.output.UTMX_METADATA_CSV = ".utmx_metadata.csv"
exp_design.output.PX_METADATA_CSV = ".px_metadata.csv"
exp_design.output.NGS_METADATA_CSV = ".ngs_metadata.csv"
exp_design.output.TEST_METADATA_JSON = ".test_metadata.json"

