from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class FetchUserInfoTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        Fetches detailed information about a GitHub user.
        """
        base_url = f"https://api.github.com/users/{tool_parameters['username']}"
        response = requests.get(base_url)
        data = response.json()
        return self.create_text_message(text=str(data))