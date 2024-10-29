# Parquemet requests

## Setup

### Install mozilla
- Follow the instructions [here](https://askubuntu.com/questions/1502031/how-to-install-firefox-directly-from-mozilla-with-apt)


### Download and install geckodriver
- From [here](https://github.com/mozilla/geckodriver/releases)
- Unzip the file:
```
$tar -xvf filename.tar.gz
```
- Move the executable:
```
$mv path/to/geckodriver /usr/local/bin/geckodriver
```

### Activate conda environment
- Create the environment:
```
conda env create -f environment.yml
```
- Activate the environment:
```
conda activate parquemet-requests
```

### Examples
- Make a test showing the browser:
```
python request_soccer_field.py 17901xxxx path/to/ci_image J 20:00 1 --show_browser --test
```
- Make a request without showing the browser, and specifying participants and plan:
```
python request_soccer_field.py 243499070 path/to/ci_image J 20:00 1 --path_to_participants participants/participants.txt --path_to_plan plans/plan.txt
```

