sudo mkdir /opt/toaster
cd /opt/toaster
sudo chown -R "$(id -u -n)" ./
chmod -R +rw ./
mkdir packages
mkdir binaries
mkdir apps
mkdir database
mkdir sources
cd database
git init
