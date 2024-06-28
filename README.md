# Instruction for Mac Development Environment

This app requires at least `python-3.10` (default installation is 3.9).
You can upgrade python3 using `brew` on install another version using `pyenv`.

## EASIEST: Upgrade python3

```
brew install python3
source ~/.zprofile # or ~/.bash_profile
```

Now we can execute `python3` to call the latest python,
and use `python` to run the defaul one.

ALTERNATIVE: use pyenv
Skip this if you have upgrade `python3` using `brew`.

```
brew install pyenv
```
vim ~/.zprofile
or
vim ~/.bash_profile
```

Add to user profile

```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Install python-3.10
```
pyenv install 3.10.0
pyenv global 3.10.0
source ~/.zprofile # or ~/.bash_profile
```

## Install Development Dnvironment

```bash
source ./s-install-dev.sh
```

Create config file

```bash
mv app.config.sh.sample app.config.sh
vim app.config.sh
```

Run the app in dev mode
```bash
./s-run
```