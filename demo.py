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
		task='find the availabilities for Trattoria dall Oste BISTECCA ALLA FIORENTINA in Via Luigi Alamanni, 3, 50123, Firenze from 1 march to 3 march.',
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
			),
		),
	)
	result = await agent.run()


asyncio.run(main())
