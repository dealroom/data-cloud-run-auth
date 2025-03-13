<!---
Based on:
* https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
* https://github.com/dealroom/dealroom/blob/develop/.github/pull_request_template.md
-->

<!---
Add link to JIRA task here
-->
<https://dealroom.atlassian.net/browse/>

<!---
If description is needed, uncomment
## What was done
-->

## Required checklist

Please, select all that apply. For those that do not apply, please explain why in section "Exceptions"

- [ ] My code follows the [Python styleguide](https://dealroom.slite.com/app/docs/74Ns9cxxCo7bKh)
- [ ] My code is formatted with [ruff](https://docs.astral.sh/ruff/)
- [ ] I have followed the [GitHub contributing guidelines](https://dealroom.slite.com/app/docs/DRrxsJrbpUvv1B). In particular:
  - [ ] The PR branch is in sync with the base branch
  - [ ] Branch and commit names were generated using the Jira-PR-Meta-Bookmarklet
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

This PR was made with 💙
