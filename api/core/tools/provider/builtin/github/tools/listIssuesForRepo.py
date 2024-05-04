from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class ListIssuesForRepoTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        Lists all issues for a specified GitHub repository.
        """
        base_url = f"https://api.github.com/repos/{tool_parameters['owner']}/{tool_parameters['repo']}/issues"
        params = {
            'page': tool_parameters.get('page', 3),
            'per_page': tool_parameters.get('per_page', 15)
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        return self.create_text_message(text=str(data))