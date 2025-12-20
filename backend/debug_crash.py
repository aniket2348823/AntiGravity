from antigravity.singularity_core import SingularityCore
import asyncio

async def test_run():
    print("Initializing Core...")
    core = SingularityCore(on_log=print, on_finding=print)
    print("Running Core...")
    await core.run("http://test-target.com")

if __name__ == "__main__":
    try:
        asyncio.run(test_run())
    except Exception as e:
        print(f"CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()
