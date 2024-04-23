from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.githubadvanced.tools import (
    SearchReposTool, ListRepoBranchesTool, ListIssuesForRepoTool, FetchUserInfoTool, ListRepoFilesTool
)
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class GithubAdvancedProvider(BuiltinToolProviderController):
    def __init__(self):
        super().__init__()
        self.register_tool('searchRepos', SearchReposTool())
        self.register_tool('listRepoBranches', ListRepoBranchesTool())
        self.register_tool('listIssuesForRepo', ListIssuesForRepoTool())
        self.register_tool('fetchUserInfo', FetchUserInfoTool())
        self.register_tool('listRepoFiles', ListRepoFilesTool())

    def _validate_credentials(self, credentials: dict) -> None:
        try:
            # Example of invoking a tool with credentials to validate them
            SearchReposTool().fork_tool_runtime(
                meta={"credentials": credentials}
            ).invoke(
                user_id='',
                tool_parameters={"q": "test"}
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))