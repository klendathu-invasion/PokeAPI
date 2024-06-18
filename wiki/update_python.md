[[_TOC_]]

# How to update python

## Install new version

To install the version X, run the command :
```bash
sudo apt install python3.X
```

## Configure the update-alternative

Check the configuration of update-alternatives :
```bash
sudo update-alternatives --config python3
```
If you get an error `no alternatives for python3`, add the previous version of python in the update-alternatives :
```bash
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.Y NB
```
Then add the new version :
```bash
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.X NB+1
```
Use the new version of python :
```bash
sudo update-alternatives --config python3
# enter the number of update-alternatives you want use (NB+1 for the version X)
```

## Update the libraries

You can check all the libraries outdated :
```bash
pip list --outdated --format=json
```

You can update all the libraries outdated (warning :  update some librabries can affect the project, save the version in requierements.txt before) :
```bash
pip list --outdated --format=json | jq -r '.[] | "\(.name)==\(.latest_version)"' | awk -F '==' '{print $1}' | xargs -n1 pip install -U --upgrade-strategy eager
```
Or update one by one :
```bash
pip install -U --upgrade-strategy eager LIBRARY
```
