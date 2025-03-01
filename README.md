## Local Setup:
First time:  
py -m venv venv  
Windows: > venv\Scripts\activate
Linux: $ . venv/bin/activate
pip install requirements.txt

Linux:  
$ . venv/bin/activate  

Windows: (cmd in Scoreboard directory)  
venv\Scripts\activate  

pip install discord-py-interactions --upgrade

## Server Setup:
Remove the build line in the docker compose file  
Add the .key file in the db folder  