A quick helper to make re-training and downloading snips assistants easier on a raspberry pi using a headless chrome browser.  Once snips supports training and downloading in an easier fashion this will be unsupported.

## Pre-reqs
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3 python3-pip
sudo apt-get install libminizip1 libwebpmux2 libgtk-3-0
pip3 install selenium
```

## Chrome and ChromeDriver
```
wget http://security.debian.org/debian-security/pool/updates/main/c/chromium-browser/chromium_63.0.3239.84-1~deb9u1_armhf.deb
wget http://security.debian.org/debian-security/pool/updates/main/c/chromium-browser/chromium-driver_63.0.3239.84-1~deb9u1_armhf.deb
```

## Install Chrome
```
#this will error because of dependencies.  This is okay and will be fixed in the next step.
sudo dpkg -i chromium_63.0.3239.84-1~deb9u1_armhf.deb
```

```
#this will install the required version of chromium-browser
sudo apt-get install -f
```

## Install ChromeDriver
```
sudo dpkg -i chromium-driver_63.0.3239.84-1~deb9u1_armhf.deb
```

## Usage

```python
from snips import *

snips_helper = Snips(chrome_driver_path='/chromedriver/path', download_dir='/download/path')
snips_helper.login("your@email.com", "your_p@$$word")


#retrain snips assistant
snips_helper.retrain()

#download snips assistant
snips_helper.download_assistant()

