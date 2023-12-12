import asyncio

import aiohttp


async def main():
    client = aiohttp.ClientSession()

    # response = await client.post('http://127.0.0.1:8080/advertisement',
    #                             json={"title": "advertisement_1", "description": "I sell a car", "owner": "Vailiy S."},
    #                              )
    #
    # print(response.status)
    # print(await response.json())

    # response = await client.patch('http://127.0.0.1:8080/advertisement/1',
    #                     json={"description": "I sell a bike"},
    #                                                           )
    #
    # print(response.status)
    # print(await response.json())

    response = await client.delete("http://127.0.0.1:8080/advertisement/1")

    print(response.status)
    print(await response.json())

    response = await client.get("http://127.0.0.1:8080/advertisement/1")

    print(response.status)
    print(await response.json())

    await client.close()


asyncio.run(main())
