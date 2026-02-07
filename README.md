**Arch Linux CLI Installer**

An intuitive, Python-based command-line installer for Arch Linux, designed with beginners in mind.
This tool allows you to configure and install Arch with ease while setting up a functional [KDE Plasma](https://kde.org/plasma-desktop/) system in the background. It removes the complexity Arch is known for while keeping the lightweight nature of the OS.


How to use this:
1. Boot into the Arch Linux live environment using your installation medium.
2. If ethernet is unavailable, connect to the internet using `iwctl` for WiFi. I suggest checking the [ArchWiki](https://wiki.archlinux.org/title/Iwd) page for this.
3. Run the following one-line command `pacman -Sy git --noconfirm && git clone https://github.com/itsbt125/Arch-Linux-CLI-Installer && cd Arch-Linux-CLI-Installer && python main.py`
