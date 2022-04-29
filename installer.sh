echo "Welcome to the toaster installer! 🍞"

echo "Making /opt/toaster directory, your password may be required..."
sudo mkdir /opt/toaster

echo "Copying default bakeries..."
sudo cp defaults/bakery.json /opt/toaster/bakery.json

echo "Giving you ownership of /opt/toaster... 🔨"
cd /opt/toaster
sudo chown -R "$(id -u -n)" ./
chmod -R +rw ./
mkdir .cache apps bakery binaries bin packages

echo "Adding toaster to path..."

echo "Toaster has been installed! 🍞 :)"
