from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.github.tools.searchRepos import SearchReposTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class GithubProvider(BuiltinToolProviderController):
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