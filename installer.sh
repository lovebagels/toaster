# Colors
GREY='\033[0;37m'
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[1;35m'
RESET='\033[0m' # No Color

# Echo function
# This is because `echo` doesnt work for colors on linux and `echo -e` which fixes it on linux makes mac echo the "-e" part
secho() {
    printf "${*}\n"
}

# OS
OS=$(uname)

# Get the options
download=true

while getopts ":c" option; do
    case $option in
    # c is an option which allows you to use toaster from whichever directory you are running this script from
    # this is intended mainly for developers as the repo may be either private or outdated
    # you also won't have to reinstall everytime you change something
    c)
        download=false
        SOURCE_DIR=$PWD
        ;;
    esac
done

# Check if toaster is already installed
[ -d "$HOME/.toaster" ] && secho "${GREEN}Toaster is already installed! 🍞${RESET}" && exit

# The actual installler starts here
secho "${GREEN}:: Welcome to the toaster installer! 🍞"
secho ":: This script will download and install toaster and add it to your path${RESET}"
secho "${GREY}Unless you otherwise specified, everything will be installed to $HOME/.toaster${RESET}\n"
printf "${MAGENTA}Press enter to continue or Ctrl+C to cancel!${RESET}"
read -p " "

secho "${GREY}Making ~/.toaster directory...${RED}"
mkdir ~/.toaster

# Download
if $download; then
    SOURCE_DIR="$HOME/.toaster/toaster"

    secho "${GREEN}Downloading toaster...${RESET}"
    git clone https://github.com/lovebagels/toaster ~/.toaster/toaster || exit 1
else
    secho "${YELLOW}Using toaster from current directory...${RESET}"
fi

# Download/install dependencies
python3 -m pip install \
    GitPython \
    atomicwrites \
    click \
    click-aliases \
    filelock \
    requests \
    toml \
    tqdm \
    validators

# Install
secho "${GREY}Copying default bakeries....${RED}"
cp $SOURCE_DIR/defaults/bakery.json ~/.toaster/bakery.json

secho "${GREY}Making subdirectories...${RED}"
cd ~/.toaster
mkdir .cache apps bakery binaries bin packages package_data
printf $RESET

if [[ "$PATH" =~ (^|:)"$HOME/.toaster/bin"(:|$) ]]; then
    secho "${YELLOW}Toaster is already in your path. Horray! 🎉${RESET}"
else
    secho "Adding toaster to your path..."

    pathexport='\n# Add toaster to path :)\nexport PATH="$HOME/.toaster/bin:$PATH"\n'
    secho $pathexport >>~/.zshrc
    secho $pathexport >>~/.bashrc

    secho "${GREEN}Toaster was added to your path. Horray! 🎉${RESET}"
fi

# Link toaster itself to toaster PATH
ln -sf $SOURCE_DIR/src/toaster/cli.py ~/.toaster/bin/toaster
chmod +x ~/.toaster/bin/toaster

secho "${GREEN}Toaster has been installed! 🍞 :)${RESET}"
