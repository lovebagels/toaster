# Roadmap

A list of things to do (for contributors)

- [x] Properly implement OS and architecture specific instructions
- [x] Properly implement uninstall scripts
- [x] Properly implement sources ("bakery"), bakery configuration files, and bakery updates (actually get bakeries from git, store them, handle updates for them, and use them when installing/removing/updating packages)
- [x] Implement custom bakery support (part of above)
- [x] Actually install packages to correct directories
- [x] Better packages support (custom links)
- [ ] Properly implement package updates
- [ ] Support binaries
- [ ] Implement hash checking
- [ ] Clean up any bad code/comments
- [ ] *See **Making installer***
- [ ] **MILESTONE #1: Support "apps"**
- [ ] Additional support for binary/building and uninstall scripts
- [ ] Once you're here, your hard work has paid off, so clean up any code and **add more packages duh :)**
- [ ] *See **Making installer** once again*
- [ ] Document toaster and document how bakeries work
- [ ] **MILESTONE #2: Make toaster and toaster-core public**
- [ ] **MILESTONE #3: Launch toaster alpha for macOS**
- [ ] Support custom installation paths
- [ ] Test and make any needed fixes for Linux *idk whether to put a :) or :(*
- [ ] *See **Making installer** once again*
- [ ] **MILESTONE #4: Launch toaster alpha for Linux**
- [ ] Fix any bugs that arise
- [ ] Add new features
- [ ] **MILESTONE #5: Launch toaster beta for macOS and Linux**

## Making installer

- Automatically find Python 3 and install required Python dependencies
- Move toaster itself to somewhere and add that to path
- Make /opt/toaster dirs and initiate git stuff there
- Add toaster's binary directories to path
