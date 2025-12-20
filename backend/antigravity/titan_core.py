from .singularity_core import SingularityCore
import asyncio

class AetherTitanOmniscience:
    """
    v5000.0 Singularity Engine Interface.
    Integrates the SingularityCore agent with the high-level scanner API.
    """
    def __init__(self):
        self.core = None

    async def commence_singularity(self, target_url, on_log=None, on_finding=None):
        """
        Launches the advanced Neural-Symbolic scan.
        """
        if on_log:
            on_log(f"[*] ACTIVATING AETHER TITAN OMNISCIENCE PROTOCOL v5000.0")
            on_log(f"[*] Target Acquired: {target_url}")
            on_log(f"[*] Initializing Neural Swarm...")
        
        self.core = SingularityCore(on_log=on_log, on_finding=on_finding)
        
        # Run the singularity event loop
        await self.core.run(target_url)
        
        if on_log:
             on_log(f"[+] SINGULARITY EVENT CONCLUDED.")
