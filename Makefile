# Please Don't Change
SRC_DIR := ./src
.DEFAULT_GOAL := help

help:  ## 💬 This Help Message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Linting and Formatting without Fix
lint: venv ## 🔎 Lint & Format, will not Fix but Sets Exit Code on Error
	. $(SRC_DIR)/.venv/bin/activate \
	&& black --check $(SRC_DIR) \
	&& flake8 $(SRC_DIR)/crawler/

# Linting and Formatting with Try to Fix and Modify Code
lint-fix: venv ## 📜 Lint & Format, will Try to Fix Errors and Modify Code
	. $(SRC_DIR)/.venv/bin/activate \
	&& black $(SRC_DIR)

# Clean up Project
clean: ## 🧹 Clean up Project
	rm -rf $(SRC_DIR)/.venv

# =====================================================================================
# Create and Activate Virtual Enviroment and then Install Requirement Packeges with pip
venv: $(SRC_DIR)/.venv/touchfile

$(SRC_DIR)/.venv/touchfile: ./requirements.txt
	python3 -m venv $(SRC_DIR)/.venv
	. $(SRC_DIR)/.venv/bin/activate; pip install -Ur ./requirements.txt
	touch $(SRC_DIR)/.venv/touchfile
