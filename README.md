# Reprise
Leverage AI and spaced repetition to enhance learning retention. Intended for use with tools like [Obsidian](https://obsidian.md/).

**Add snippets to database**
```
python -m scripts.input
```

## Setup
### Dependencies
Install python packages with [pipenv](https://pipenv.pypa.io/en/latest/):
```
pip install pipenv
pipenv shell
pipenv install
```

Install tkinter GUI to interact with motifs before persistence to db:
```sh
brew install python-tk
```
You will likely will need to reinstall python after this (e.g. re-install from pyenv).

### Environment
This tool requires an [OpenAI API key](https://platform.openai.com/api-keys).

Create an `.env` file as follows:
```
OPENAI_API_KEY=your-api-key
VAULT_DIRECTORY=your-vault-path
```
