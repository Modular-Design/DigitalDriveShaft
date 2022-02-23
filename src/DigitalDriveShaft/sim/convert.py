# Run this script to convert all APDL scripts to .py
import ansys.mapdl.core as pymapdl
from pathlib import Path

scripts_path = Path("scripts")
items = scripts_path.iterdir()

for item in items:
    if not item.is_file():
        continue
    if item.suffix != ".txt":
        continue
    suffix = item.suffix
    name = item.name[:-len(suffix)]
    output_file = Path(scripts_path / (name + ".py"))
    pymapdl.convert_script(str(item.absolute()), str(output_file.absolute()))
