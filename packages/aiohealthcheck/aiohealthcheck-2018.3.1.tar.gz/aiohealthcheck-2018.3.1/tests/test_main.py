import asyncio
import aiohealthcheck


def test_health(loop: asyncio.AbstractEventLoop):

    results = []
    PORT = 5000

    async def dummy_k8s():
        # Wait for server to be up
        await asyncio.sleep(0.1)

        for i in range(100):
            tup = await asyncio.open_connection(
                host='localhost', port=PORT, loop=loop
            )
            reader, writer = tup
            results.append(await reader.read(1024))
            writer.close()
            print('.', end='', flush=True)

    t1 = loop.create_task(aiohealthcheck.tcp_health_endpoint(PORT))
    t2 = loop.create_task(dummy_k8s())

    try:
        loop.run_until_complete(asyncio.wait_for(t2, 50))
    finally:
        assert results == [b'ping'] * 100
        group = asyncio.gather(t1, t2, return_exceptions=True)
        group.cancel()
        loop.run_until_complete(group)
