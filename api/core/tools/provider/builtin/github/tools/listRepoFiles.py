from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class ListRepoFilesTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        Lists files and directories in a specified path within a GitHub repository.
        """
        base_url = f"https://api.github.com/repos/{tool_parameters['owner']}/{tool_parameters['repo']}/contents/{tool_parameters['path']}"
        response = requests.get(base_url)
        data = response.json()
        return self.create_text_message(text=str(data))