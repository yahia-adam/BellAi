from bellai.core.agent import BellAIAgent
from pprint import pprint

import asyncio
from bellai.tools.places_service import *

if __name__ == "__main__":
    agent = BellAIAgent()
    
    async def main():
        res = await agent.process_message("hi", "test_session")
        print("----"*5)
        pprint(res, indent=2, width=100)
    
    asyncio.run(main())

