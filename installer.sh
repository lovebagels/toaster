echo "Welcome to the toaster installer! 🍞"

echo "Making ~/.toaster directory..."
mkdir ~/.toaster

echo "Copying default bakeries..."
cp defaults/bakery.json ~/.toaster/bakery.json

echo "Making subdirectories..."
cd ~/.toaster
mkdir .cache apps bakery binaries bin packages

echo "Adding toaster to path..."
export PATH="~/.toaster/bin:$PATH"

echo "Toaster has been installed! 🍞 :)"
