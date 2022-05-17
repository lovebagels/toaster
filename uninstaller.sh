RED='\033[1;31m'
GREEN='\033[1;32m'
RESET='\033[0m' # No Color

printf "${RED}Are you sure you want to uninstall toaster? (THIS WILL REMOVE ALL YOUR AMAZING PACKAGES AS WELL) ${RESET}"
read -r

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${GREEN}Toaster will not be not uninstalled!${RESET}"
    exit 1
fi

echo "Uninstalling toaster... 😔"

rm -rf ~/.toaster
