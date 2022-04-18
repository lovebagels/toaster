sudo mkdir /opt/toaster
cp defaults/bakery.json /opt/toaster/bakery.json
cd /opt/toaster
sudo chown -R "$(id -u -n)" ./
chmod -R +rw ./
mkdir packages
mkdir binaries
mkdir apps
mkdir bakery
