# using root permission
sudo -i
$USER=cjc

# setting up pravate key
chmod 600 /home/$USER/.ssh/id_rsa

# setting up ssh configs
ln ssh/config /home/$USER/.ssh/config

# setting up pacman mirrors
# TODO

# setting up archlinuxcn
# TODO
pacman -Syu
pacman -S archlinuxcn-keyring

# setting up pacman verbose pkg list
sed "s/#VerbosePkgLists/VerbosePkgLists"

# setting up scale (150%)
# simply modify font size
gsettings set org.gnome.desktop.interface text-scaling-factor 1.5

# install packages
pacman -Syu --noconfirm
pacman -S --noconfirm pycharm-professional vim code npm github-desktop-bin yarn \ # about coding
    clash chromium telegram-desktop goldendict-qt5-git typora nixnote2 \ # GUI applications
    electron-netease-cloud-music \
    openbsd-netcat bash-completion onedrive-abraunegg \ # CLI applications or libaraies
    proxychains-ng tldr pkgtools

# install AUR packages
# base-devel may be needed in compiling AUR packages
pacman -S --noconfirm base-devel yay
yay --aururl "https://aur.tuna.tsinghua.edu.cn" --save
# TODO
yay -S k380-function-keys-conf-git deepin-wine-tim consolas-font

# setting up clash systemd service
if [ ! -e /etc/systemd/system/clash.service ]; then
    cat > /etc/systemd/system/clash.service <<- EOF
    [Unit]                            
    Description=A rule based proxy in Go.
    After=network.target
                        
    [Service]
    Type=simple
    User=cjc
    Restart=on-abort
    ExecStart=/usr/bin/clash
                            
    [Install]
    WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable clash
systemctl start clash
fi
# Note: default config file is ~/.config/clash/config.yaml

# setting up Chinese IME
pacman -S --noconfirm fcitx-im fcitx-rime
if [ ! -e /home/$HOME/.pam_environment ]; then # TODO may have permission problems
    cat > /home/$HOME/.pam_environment <<- EOF
    GTK_IM_MODULE=fcitx
    QT_IM_MODULE=fcitx
    XMODIFIERS=@im=fcitx
EOF
fi 

# setting up pip mirror
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# gnome settings
# gnome ternimal keybindings
# TODO
dconf write /org/gnome/terminal/legacy/keybindings/next-tab "'<Control>Tab'"
dconf write /org/gnome/terminal/legacy/keybindings/new-tab "'<Control>n'"

# setting up proxychains
# TODO

# for deepin-wine-tim
# setting up HiDPI
# env WINEPREFIX="$HOME/.deepinwine/Deepin-TIM" winecfg

# setting up bash profiles
cat < my_bash.profile >> ~/.bashrc

# setting up onedrive systemd service
systemctl --user enable onedrive
systemctl --user start onedrive
