from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool


class SearchReposTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        Search GitHub repositories based on the provided query and sorting parameters.
        """
        base_url = "https://api.github.com/search/repositories"
        params = {
            'q': tool_parameters['q'],
            'sort': tool_parameters.get('sort', ''),
            'order': tool_parameters.get('order', 'desc'),
            'page': tool_parameters['page'],
            'per_page': tool_parameters['per_page']
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        return self.create_text_message(text=str(data))