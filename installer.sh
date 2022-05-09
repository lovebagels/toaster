GREY='\033[0;37m'
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RESET='\033[0m' # No Color

SOURCE_DIR=$PWD

echo "${GREEN}:: Welcome to the toaster installer! 🍞"
echo ":: This script will download and install toaster and add it to your path${RESET}"

echo "${GREY}Making ~/.toaster directory...${RED}"
mkdir ~/.toaster

echo "${GREY}Copying default bakeries....${RED}"
cp $PWD/defaults/bakery.json ~/.toaster/bakery.json

echo "${GREY}Making subdirectories...${RED}"
cd ~/.toaster
mkdir .cache apps bakery binaries bin packages package_data
printf $RESET

if [[ "$PATH" =~ (^|:)"$HOME/.toaster/bin"(:|$) ]]; then
    echo "${YELLOW}Toaster is already in your path. Horray! 🎉${RESET}"
else
    echo "Adding toaster to your path..."

    pathexport='\n# Add toaster to path :)\nexport PATH="$HOME/.toaster/bin:$PATH"\n'
    echo $pathexport >>~/.zshrc
    echo $pathexport >>~/.bashrc

    echo "${GREEN}Toaster was added to your path. Horray! 🎉${RESET}"
fi

# Link toaster itself to toaster PATH
ln -sf $SOURCE_DIR/src/toaster/cli.py ~/.toaster/bin/toaster
chmod +x ~/.toaster/bin/toaster

echo "${GREEN}Toaster has been installed! 🍞 :)${RESET}"

cd $PWD
