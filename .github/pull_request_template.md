<!---
Based on:
* https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
* https://github.com/dealroom/dealroom/blob/develop/.github/pull_request_template.md
-->

<!---
Add link to JIRA task here
-->
https://dealroom.atlassian.net/browse/


<!---
If description is needed, uncomment
## What was done
-->


## Required checklist

Please, select all that apply. For those that do not apply, please explain why in section "Exceptions"

- [ ] My code follows the [Python styleguide](https://dealroom.atlassian.net/wiki/spaces/DATA/pages/484147227/Python+Styleguide)
- [ ] My code is formatted with [black](https://black.readthedocs.io/en/stable/)
- [ ] I have followed the [GitHub contributing guidelines](https://dealroom.atlassian.net/wiki/spaces/DATA/pages/610828294/Contributing+guidelines+on+GitHub). In particular:
  - [ ] The PR branch is in sync with the base branch
  - [ ] Branch and commit names were generated using [Jira-PR-Meta-Bookmarklet](https://dealroom.atlassian.net/wiki/spaces/DATA/pages/610828294/Contributing+guidelines+on+GitHub#Jira-PR-Meta-Bookmarklet)
- [ ] The local environment used to develop this code is based on `poetry.lock` or `requirements-dev.txt`
- [ ] I have included the changes required by no more than 1 JIRA task
- [ ] I have tested my code locally
- [ ] I have checked SonarCloud and made corresponding changes were possible
- [ ] I have checked that other automatic checks are OK
- [ ] I have reviewed my own PR


<!---
## Required checklist specific to this repo

Add here a repo-specific checklist
-->


## Optional checklist

Please, select all those that apply

- [ ] I have used new packages and I have updated `poetry.lock`, `requirements*.txt` and `pyproject.toml` accordingly
- [ ] I have made corresponding changes to the documentation <!--- add link and uncomment []() -->
- [ ] I have added tests and my tests are integrated in the automatic checks of this repo


<!---
## Exceptions

Please un-comment this section and explain here why any items of the required checklists do not apply -- e.g. old repository that needs bigger refactoring, I'm lazy, ...
-->


## Useful links

* [Data Requests](https://dealroom.atlassian.net/jira/software/projects/DR/boards/36)
* [Data Squad 1](https://dealroom.atlassian.net/jira/software/projects/DS1/boards/37)
* [Data Squad 2](https://dealroom.atlassian.net/jira/software/projects/DS2/boards/38)


This PR was made with 💚
