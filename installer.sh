# -- Variables & Initial Functions --

# Colors
GREY='\033[0;37m'
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[1;35m'
RESET='\033[0m' # No Color

OS=$(uname)

# Echo function
# This is because `echo` doesnt work for colors on linux and `echo -e` which fixes it on linux makes mac echo the "-e" part
secho() {
    printf "${*}${RESET}\n"
}

sprint() {
    printf "${*}\n"
}

# Get the options
download=true
allow_root=false
confirm=true
while getopts ":cry" option; do
    case $option in
    # c is an option which allows you to use toaster from whichever directory you are running this script from
    # this is intended mainly for developers as the repo may be either private or outdated
    # you also won't have to reinstall everytime you change something
    c)
        download=false
        SOURCE_DIR=$PWD
        ;;
    r)
        allow_root=true
        ;;
    y)
        confirm=false
        ;;
    esac
done

if [[ "$allow_root" != true ]]; then
    # Check if running as root
    if [[ "${EUID:-${UID}}" == "0" ]]; then
        secho "${RED}Please do not install toaster as root!"
        exit 1
    fi
fi

# Check if toaster is already installed
[ -d "$HOME/.toaster" ] && secho "${GREEN}Toaster is already installed! 🍞" && exit 1

# -- Main --

# Install dependencies
install_dependencies() {
    # Dependency checks for arch-based distro
    if pacman --version >&/dev/null; then
        secho "${MAGENTA}Pacman was detected, checking if you have required packages..."

        if ! pacman -Qi gcc git; then
            echo "${RED}You are missing required system packages! Please install $(base-devel) via pacman."
            exit 1
        fi

        if ! pacman -Qi python3 python-pip; then
            echo "${RED}You are missing Python 3 and/or PIP, which are required to run toaster.\nPlease install $(python3) and $(python-pip) via pacman!"
        fi
    fi
}

# The actual installler starts here
secho "${GREEN}:: Welcome to the toaster installer! 🍞"
secho "${GREEN}:: This script will download and install toaster and add it to your path"
secho "${GREY}Unless you otherwise specified, everything will be installed to $HOME/.toaster\n"

if [[ "$confirm" == true ]]; then
    printf "${MAGENTA}Press enter to continue or Ctrl+C to cancel! ${RESET}"
    read -p " "
fi

install_dependencies

if [[ "$confirm" == true ]]; then
    read -p " "
fi

secho "${GREY}Making ~/.toaster directory..."
mkdir ~/.toaster

# Download
if $download; then
    SOURCE_DIR="$HOME/.toaster/toaster"

    secho "${GREEN}Downloading toaster..."
    git clone https://github.com/lovebagels/toaster ~/.toaster/toaster || exit 1
else
    secho "${YELLOW}Using toaster from current directory..."
fi

# Download/install dependencies
secho "${GREEN}Downloading/installing dependencies..."

python3 -m pip install \
    GitPython \
    atomicwrites \
    click \
    click-aliases \
    filelock \
    packaging \
    pathlib \
    requests \
    toml \
    tqdm \
    validators

# Install
secho "${GREY}Copying default bakeries....${RED}"
cp $SOURCE_DIR/defaults/bakery.json ~/.toaster/bakery.json

secho "${GREY}Making subdirectories...${RED}"
cd ~/.toaster
mkdir .cache apps bakery binaries bin packages package_data etc
printf $RESET

if [[ "$PATH" =~ (^|:)"$HOME/.toaster/bin"(:|$) ]]; then
    secho "${YELLOW}Toaster is already in your path. Horray! 🎉"
else
    secho "Adding toaster to your path..."

    pathexport='\n# Add toaster to path :)\nexport PATH="$HOME/.toaster/bin:$PATH"\n'
    secho $pathexport >>~/.zshrc
    secho $pathexport >>~/.bashrc

    secho "${GREEN}Toaster was added to your path. Horray! 🎉"
fi

# Link toaster itself to toaster PATH
ln -sf $SOURCE_DIR/src/toaster/cli.py ~/.toaster/bin/toaster
chmod +x ~/.toaster/bin/toaster

secho "${GREEN}Toaster has been installed! 🍞 :)"
