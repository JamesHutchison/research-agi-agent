#!/usr/bin/env bash
set -e

# git settings
git config --global pull.rebase true
git config --global remote.origin.prune true

# if the .venv directory was mounted as a named volume, it needs the ownership changed
sudo chown vscode .venv || true

# make the python binary location predictable
poetry config virtualenvs.in-project true
poetry install --with=dev || true

mkdir -p .dev_container_logs
echo "*" > .dev_container_logs/.gitignore

# git clone SuperAGI if it doesn't exist
if [ ! -d ../SuperAGI ]; then
    git clone https://github.com/TransformerOptimus/SuperAGI.git /workspaces/SuperAGI
fi

# make a copy of the SuperAGI config from the template if it does not exist
if [ ! -f /workspaces/SuperAGI/config.yaml ]; then
    cp /workspaces/research-agi-agent/.devcontainer/config_template.yaml /workspaces/SuperAGI/config.yaml
fi

# soft link to superAGI
# make external_tools directory if it doesnt exist
mkdir -p /workspaces/SuperAGI/superagi/tools/external_tools
# soft link DeepResearchTool if it doesn't exist
if [ ! -d /workspaces/SuperAGI/superagi/tools/external_tools/DeepResearchTool ]; then
    ln -s /workspaces/research-agi-agent/DeepResearchTool /workspaces/SuperAGI/superagi/tools/external_tools/DeepResearchTool
fi

# setup SuperAGI
cd /workspaces/SuperAGI
pip install -r requirements.txt
