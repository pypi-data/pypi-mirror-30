# short-report-client

This is a small client for short-report. I write this client and Short-Report to
try out some python packages and frameworks. If you find something what's wrong,
feel free to contact me. 

After you have log in, Short-Report give you a token. So you only have to log in
once. Only the token is saved in a file, not the password. Every log in change
the token. If you run a scrip on one mashine and log in an other mashien. The
token of the first one are not longer valid.

## Install
Install requirements
```{r, engine='bash', count_lines}
sudo apt update && sudo apt -y upgrade
sudo apt install -y python3-pip
sudo -H pip3 install --upgrade pip
```
You can clone the repo:
```{r, engine='bash', count_lines}
cd
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/axju/short-report-client
cd short-report-client
pip install -e .
```

## Setup server with supervisor
Install and setup requirements
```{r, engine='bash', count_lines}
sudo apt -y install supervisor
sudo systemctl enable supervisor
sudo systemctl start supervisor
```
Login to generate the token:
```{r, engine='bash', count_lines}
short-report-client -u "usernam" -p "password"
```
Create the config file for supervisor:
```{r, engine='bash', count_lines}
mkdir ~/logs
sudo nano /etc/supervisor/conf.d/short-report-client.conf
```
With the following, change the user and stdout_logfile:
```{r, engine='text', count_lines}
[program:short-report-client]
command=/home/user/venv/bin/short-report-client -t 60
user=user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/user/logs/s-r-client.log
```
Active the settings and check the status
```{r, engine='bash', count_lines}
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status short-report-client
```


TODO:
 1. Check if the api has rights to push data to the server.


