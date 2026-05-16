import asyncio
from duckduckgo_search import AsyncDDGS

async def test_search():
    print("Testing DuckDuckGo Search...")
    try:
        async with AsyncDDGS() as ddgs:
            results = await ddgs.text("AI product trends 2025", max_results=2)
            print(f"Results found: {len(results)}")
            for r in results:
                print(f"- {r['title']}")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
