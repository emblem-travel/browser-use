from browser_use import Agent, BrowserConfig, Controller
from browser_use.browser.browser import BrowserContext, BrowserContextConfig, Browser
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from pydantic import BaseModel

import asyncio
from dotenv import load_dotenv

load_dotenv()


class AvailabilityItem(BaseModel):
	date: str
	times: list[str]


class AvailabilityItems(BaseModel):
	items: list[AvailabilityItem]
	captcha_encountered: bool = False


async def main():
	controller = Controller(output_model=AvailabilityItems)
	agent = Agent(
		task='find me availabilities for meow wolf las vegas for 3rd march 2025 to 5th march 2025.',
		validate_output=True,
		llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp'),
		controller=controller,
		browser_context=BrowserContext(
			browser=Browser(config=BrowserConfig(headless=False)),
			config=BrowserContextConfig(
				wait_between_actions=2,
				browser_window_size={
					'width': 1000,
					'height': 1920,
				},
				viewport_expansion=-1,
			),
		),
	)
	result = await agent.run()
	print(result)


asyncio.run(main())
