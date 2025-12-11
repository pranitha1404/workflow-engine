import asyncio, websockets, json

run_id = "70e6edde-c06e-470d-83f5-162e9615cc16"
uri = f"ws://127.0.0.1:8000/ws/run/{run_id}"

async def main():
    try:
        async with websockets.connect(uri) as ws:
            async for msg in ws:
                try:
                    print(json.dumps(json.loads(msg), indent=2, ensure_ascii=False))
                except:
                    print(msg)
    except Exception as e:
        print("connection closed:", e)

asyncio.run(main())
