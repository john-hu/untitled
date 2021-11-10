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

5. create the recipe category
```shell
sudo su solr
cd /opt/solr
bin/solr create -c recipe
bin/solr config -c recipe -p 8983 -action set-user-property -property update.autoCreateFields -value false
```

# Install silver plate

0. prepare nginx
```shell
sudo apt install nginx
```

1. download the source
```shell
mkdir -p /opt/silver_plate
wget https://github.com/john-hu/untitled/archive/refs/heads/main.zip
unzip untitled-main.zip
cp untitled-main/recipe/* /opt/silver_plate
cd /opt/silver_plate
```
Since the repo is private repo, we may not be able to download it from the server.
We can configure the deployment key at GitHub or download it from browser and use scp to copy it.

We can download the source and prepare everything in our owned account and chown the files to
the silver_plate account.

2. prepare python
```shell
sudo apt install python3.9
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.9 get-pip.py
```

3. prepare env
```shell
pip install virtualenv
python3.9 -m virtualenv env
source env/bin/activate
pip install -r requirement.txt
```

4. update solr schema
```shell
sudo cp ~/untitled-main/doc/cutting_board/recipeEnum.xml /var/solr/data/recipe
sudo chown solr:solr /var/solr/data/recipe/recipeEnum.xml
python manage.py runscript create_schema --script-args http://localhost:8983/ recipe
python manage.py migrate
python manage.py collectstatic
```

5. prepare account
```shell
sudo useradd -d /opt/silver_plate silver_plate
sudo chown -R silver_plate:silver_plate /opt/silver_plate
```

6. start the server

To have the silver_plate service, we have to copy the service and socket file to `systemd` folders.
```shell
sudo cp /opt/silver_plate/server_settings/image/silver_plate.service /etc/systemd/system/
sudo cp /opt/silver_plate/server_settings/image/silver_plate.socket /etc/systemd/system/
```

Before starting the service, we need to modify the nginx to load the site from silver plate:
```shell
sudo cp /opt/silver_plate/server_settings/image/nginx.conf /etc/nginx/sites-available/default
```

After that, we can start the service
```shell
sudo systemctl reload nginx
sudo systemctl enable silver_plate.service
sudo systemctl start silver_plate.service
```
