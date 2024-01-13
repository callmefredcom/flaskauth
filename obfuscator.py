import os
import subprocess

# Directory containing your JS files
js_directory = 'static'

# Target file to obfuscate
target_file = 'app.js'

# Check if the target file exists in the directory
if target_file in os.listdir(js_directory):
    original_file_path = os.path.join(js_directory, target_file)
    # Create a new filename with 'obs' before the '.js'
    obfuscated_file_name = target_file.replace('.js', '.obs.js')
    obfuscated_file_path = os.path.join(js_directory, obfuscated_file_name)

    # Command to obfuscate the JS file
    obfuscate_command = f"javascript-obfuscator {original_file_path} --output {obfuscated_file_path}"

    # Run the command
    subprocess.run(obfuscate_command, shell=True)

    print(f"Obfuscated {target_file} to {obfuscated_file_name}")
else:
    print(f"File {target_file} not found in {js_directory}.")