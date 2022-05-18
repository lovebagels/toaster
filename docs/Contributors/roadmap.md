# Roadmap

A list of things to do (for contributors)

- [x] Properly implement OS and architecture specific instructions
- [x] Properly implement uninstall scripts
- [x] Properly implement sources ("bakery"), bakery configuration files, and bakery updates (actually get bakeries from git, store them, handle updates for them, and use them when installing/removing/updating packages)
- [x] Implement custom bakery support (part of above)
- [x] Actually install packages to correct directories
- [x] Better packages support (custom links)
- [x] Lock database
- [x] Clean-up install package function
- [x] Properly implement package updates
- [x] Support binaries
- [x] Binary updates
- [x] Support other types of archives
- [x] Document binaries
- [x] Properly implement dependencies
- [x] Versioning support
- [x] Document "homepage" option
- [x] Support building with URL
- [x] Dont link if already in path (or ask)
- [x] Toaster updater
- [x] Document how bakeries work
- [x] Update all packages properly
- [x] Safer package updates
- [x] External dependencies ("uses")
- [x] Document "uses" option
- [x] Link/unlink command
- [x] Document using archive URLs for build
- [ ] Pretty "use" error messages
- [ ] Support scripts in binaries
- [ ] Link binaries/packages properly depending on type that was installed
- [ ] Info command for bakeries
- [ ] Clean up packages.py code
- [ ] Clean up code in sysupdates.py
- [ ] Check before installing that package supports platform
- [ ] Implement hash checking
- [ ] Allow caching packages
- [ ] Clean up any bad code/comments
- [ ] Package and bakery info commands
- [ ] Make dependencies be diff for build/binary
- [ ] packages that "Always update" like git packages
- [ ] *See **Making installer***
- [ ] Once you're here, your hard work has paid off, so clean up any code and **add more packages duh :)**
- [ ] **MILESTONE #1: Launch toaster alpha**
- [ ] **MILESTONE #2: Support "apps"**
- [ ] *See **Making installer** once again*
- [ ] Make sure Linux support works as expected
- [ ] Fix any bugs that arise
- [ ] Add new features
- [ ] Make toaster prettier
- [ ] **MILESTONE #5: Launch toaster beta for macOS and Linux**

## Making installer

- Automatically find Python 3 and install required Python dependencies
- Move toaster itself to somewhere and add that to path
- Make ~/.toaster dirs
- Add toaster's binary directories to path
