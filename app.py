from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr

from browser_use import Agent, BrowserConfig, Controller
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.browser import Browser, BrowserContext, BrowserContextConfig


class AvailabilityItem(BaseModel):
	date: str
	times: list[str]


class AvailabilityItems(BaseModel):
	items: list[AvailabilityItem]
	captcha_encountered: bool = False


async def run_browser_use(
	task: str,
	gemini_api_key: SecretStr,
) -> Optional[AvailabilityItems]:
	controller = Controller(output_model=AvailabilityItems)
	agent = Agent(
		task=task,
		generate_gif=False,
		llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=gemini_api_key),
		controller=controller,
		browser_context=BrowserContext(
			browser=Browser(config=BrowserConfig(headless=False)),
			config=BrowserContextConfig(
				wait_between_actions=2,
				browser_window_size={
					'width': 1000,
					'height': 1920,
				},
			),
		),
	)
	result = await agent.run()

	if type(result) is not AgentHistoryList:
		raise Exception('Result is not an AgentHistoryList')

	agent_history_list: AgentHistoryList = result
	final_result = agent_history_list.final_result()
	if final_result is None:
		return None

	typed_result = AvailabilityItems.model_validate_json(final_result)
	if typed_result is None:
		return None
	return typed_result
