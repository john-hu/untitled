# Install cutting board

1. check the JRE
```shell
java --version
```

2. If no JRE installed, we need to install one
```shell
sudo apt install openjdk-17-jre-headless
```

test it:
```shell
hchu@wiseipes:~$ java --version
openjdk 17 2021-09-14
OpenJDK Runtime Environment (build 17+35-Ubuntu-120.04)
OpenJDK 64-Bit Server VM (build 17+35-Ubuntu-120.04, mixed mode, sharing)
```

3. download the solr (running as root)
```shell
wget https://dlcdn.apache.org/lucene/solr/8.10.1/solr-8.10.1.tgz
sha512sum solr-8.10.1.tgz
```
Check the checksum MUST be:
```shell
1e8593b4a9b196aa3a12edc1928c83fc108f1cae2dd17f17a10b76d2b1a441341db6a165f74bca0f78bfc7fd0d63b30f525221d5725529961212886a50ee6aa7
```

4. config the solr
```shell
tar xzvf solr-8.10.1.tgz solr-8.10.1/bin/install_solr_service.sh --strip-components=2
sudo bash ./install_solr_service.sh solr-8.10.1.tgz
```

# Install silver plate

0. prepare nginx
```shell
sudo apt install nginx
```

1. download the source
```shell
mkdir -p /opt/silver_plate
cd /opt/silver_plate
wget https://github.com/john-hu/untitled/archive/refs/heads/main.zip
unzip untitled-main.zip
```
Since the repo is private repo, we may not be able to download it from the server.
We can configure the deployment key at GitHub or download it from browser and use scp to copy it.

We can download the source and prepare everything in our owned account and chown the files to
the silver_plate account.

2. prepare python
```shell
sudo apt install python3.9
wget https://bootstrap.pypa.io/get-pip.py
python3.9 get-pip.py
# put ~/.local/bin to PATH
export PATH=$PATH:~/.local/bin/
```

3. prepare env
```shell
pip install virtualenv
python3.9 -m virtual env
source env/bin/activate
pip install -r requirement.txt
```

4. prepare account
```shell
useradd -d /opt/silver_plate silver_plate
chown -R silver_plate:silver_plate /opt/silver_plate
```

5. start the server

To have the silver_plate service, we have to copy the service and socket file to `systemd` folders.
```shell
cp /opt/silver_plate/server_settings/image/silver_plate.service /etc/systemd/system/
cp /opt/silver_plate/server_settings/image/silver_plate.socket /etc/systemd/system/
```

Before starting the service, we need to modify the nginx to load the site from silver plate:
```shell
cp /opt/silver_plate/server_settings/image/nginx.conf /etc/nginx/sites-available/default
```

After that, we can start the service
```shell
systemctl start silver_plate.service
```
