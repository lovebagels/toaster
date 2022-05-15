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
- [ ] Document how bakeries work
- [x] Properly implement dependencies
- [x] Versioning support
- [ ] External dependencies
- [ ] Dont link if already in path (or ask)
- [ ] Link command
- [ ] Info command for bakeries
- [x] Toaster updater
- [ ] Clean up packages.py code
- [ ] Clean up code in sysupdates.py
- [ ] Implement hash checking
- [ ] Check before installing that package supports platform
- [ ] Safer package updates
- [ ] Allow caching packages
- [ ] Clean up any bad code/comments
- [ ] Package and bakery info commands
- [ ] *See **Making installer***
- [ ] Once you're here, your hard work has paid off, so clean up any code and **add more packages duh :)**
- [ ] **MILESTONE #1: Launch toaster alpha for macOS**
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
