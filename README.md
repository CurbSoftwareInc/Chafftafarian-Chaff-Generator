# Chafftafarian Chaff Generator

This project is a chaff generator.  It generates random chaff based on your settings.

# Available Settings
- target directory default: /home/$USER/.chaff
- delete after completion default: false
- fill drive default: false
- minimum remaining disk space default: 100MB (set to 0MB to fill to capacity)
- minimum file size default: 0.1MB
- maximum file size default: 10MB
- minimum file count default: 100
- maximum file count default: 10000
- chaff file types (emails, images, or documents) default: ['txt', 'jpg', 'eml', 'pdf', 'docx', 'xlsx', 'csv']
- include languages default: ['en', 'es', 'fr', 'de', 'cn', 'jp', 'ru']

# Usage
Set settings in the .env file and run the script.

# Installation
1. Clone the repository:
   ```
   git clone https://github.com/CurbSoftwareInc/Chafftafarian-Chaff-Generator.git
   cd Chafftafarian-Chaff-Generator
   ```

2. Create and activate a Python virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
   Note: On Ubuntu/Debian systems, you may need to install python3-venv first:
   ```
   sudo apt install python3.12-venv
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your settings. Example:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file to set your desired settings.

6. Finally, run the script:
   ```
   python main.py
   ```

7. To deactivate the virtual environment when done:
   ```
   deactivate
   ```

run `python main.py` to generate chaff files.

What this script does:
It generates random files in the specified directory with the specified settings. It can fill a drive with random data, delete files after completion, and generate files of various types and sizes.

It will create files that are linked like an email with attachments.  It will create a lot of random files, it will reference the files one to another, and it will encode the files in random different ways to make it look like real data.  Some ways it will encode files are base64 encryption in different formats, zip files, and other methods to make it look like real data.  Some linked files, like emails will have refereces to other files to find compressed file passwords, or encryption keys to other files randomly.

Images in the data/images directory will be added, the script should scan that directory and randomly select images to use in the chaff generation.

The data/templates directory should have templates for the different types of files we want to generate.  The script will randomly select a template and fill it with random data from the data directory.