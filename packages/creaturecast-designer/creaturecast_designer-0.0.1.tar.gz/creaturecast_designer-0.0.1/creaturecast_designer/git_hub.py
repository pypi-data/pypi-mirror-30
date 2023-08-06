
from github import Github

g = Github("paxtongerrish@gmail.com", "y25H{9(]GW7423z")
paxton = g.get_user()
for owned_repo in paxton.get_repos(type='owner'):
    default_branch = owned_repo.get_branch(owned_repo.default_branch)


#for repo in g.get_user().get_repos():
#    print repo.name
#    repo.edit(has_wiki=False)