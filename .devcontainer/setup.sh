#!/bin/bash

poetry install

pre-commit install

sudo apt update
sudo apt install -y git-flow python3-cracklib entr

# custom packages
sudo apt install -y micro
sudo apt install -y ranger


# Install powerlevel10k theme
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
cp .devcontainer/.p10k.zsh ~
sed -i 's/ZSH_THEME="devcontainers"/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc
# plugins
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
sed -i 's/plugins=(git)/plugins=(git history-substring-search colored-man-pages zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc

echo 'POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true' >> ~/.zshrc

# custom aliases
echo 'alias stack="/workspaces/revolt-nexus/stack.sh"' >> ~/.zshrc
echo 'alias rr="source ranger"' >> ~/.zshrc
echo 'alias runserver="stack run-server"' >> ~/.zshrc
echo 'alias serverrun="stack run-server"' >> ~/.zshrc
echo 'alias down="stack dev down"' >> ~/.zshrc
echo 'alias dc="docker compose"' >> ~/.zshrc

# pyenv
curl https://pyenv.run | bash
echo '' >> ~/.zshrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
echo '' >> ~/.zshrc


# adding p10k configuration to the shell
echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ~/.zshrc
