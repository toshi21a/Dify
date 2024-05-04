from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class ListRepoBranchesTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        List all branches in a specific GitHub repository.
        """
        base_url = f"https://api.github.com/repos/{tool_parameters['owner']}/{tool_parameters['repo']}/branches"
        params = {
            'protected': tool_parameters.get('protected', ''),
            'per_page': tool_parameters.get('per_page', 20),
            'page': tool_parameters.get('page', 1)
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        return self.create_text_message(text=str(data))