# git_store.py = update file on github

# import packages
from github import Github

### Import .env variables
from dotenv import load_dotenv
import os
load_dotenv()  # take environment variables from .env
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')

# create github instance
github = Github(GITHUB_ACCESS_TOKEN)

# Get all of the contents of the repository recursively
def get_contents():
    repo = github.get_user().get_repo("tgk_analytics")
    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            print(file_content)

# get a list of branches
def get_branches():
    repo = github.get_user().get_repo("tgk_analytics")
    print(list(repo.get_branches()))


# next feature
file_path = 'pages/'


get_contents()
