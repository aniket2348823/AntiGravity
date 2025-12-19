import aiohttp
import json
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BountyAutomator:
    """
    The Autonomous Bounty Automator (v120.0).
    Handles the 'Last Mile' of the kill chain: Submitting verified PoCs to Bounty Platforms.
    """
    def __init__(self, h1_token=None, h1_username=None, dry_run=True):
        self.h1_api = "https://api.hackerone.com/v1"
        self.dry_run = dry_run
        
        if h1_token and h1_username:
            self.auth = aiohttp.BasicAuth(h1_username, h1_token)
            self.authenticated = True
        else:
            self.auth = None
            self.authenticated = False
            logger.warning("BountyAutomator initialized in OFF-LINE mode (No Credentials).")

    async def verify_scope(self, target_domain):
        """
        Checks if a target is actively in-scope for a bounty program.
        (Mocked for safety/demonstration).
        """
        logger.info(f"Verifying Scope Eligibility for: {target_domain}")
        # In a real scenario, this would query the H1/Bugcrowd API for program scope
        await asyncio.sleep(0.5)
        return True

    async def submit_critical_exploit(self, program_handle, poc_data):
        """
        Automates the submission to HackerOne once verified.
        """
        if not self.authenticated and not self.dry_run:
             logger.error("Cannot submit report: No credentials provided.")
             return "Submission Failed: Authentication missing"

        # Construct payload according to H1 API v1
        payload = {
            "data": {
                "type": "report",
                "attributes": {
                    "title": f"[CRITICAL] {poc_data.get('type', 'Unknown Vulnerability')} on {poc_data.get('target', 'Target')}",
                    "vulnerability_information": poc_data.get('proof_text', 'Automated Proof of Concept'),
                    "impact": "Full Account Takeover / Transactional Collapse / PII Leak",
                    "severity_rating": "critical",
                    "team_handle": program_handle
                }
            }
        }
        
        logger.info(f"Drafting Report for {program_handle}...")
        
        if self.dry_run:
            logger.info("DRY RUN: Skipping actual API POST.")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            return f"Submission Simulated: Report #Draft-{hash(poc_data.get('target', '')) % 10000}"

        try:
            async with aiohttp.ClientSession(auth=self.auth) as session:
                async with session.post(f"{self.h1_api}/hackers/reports", json=payload) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        report_id = result.get('data', {}).get('id', 'Unknown')
                        logger.info(f"Report Submitted Successfully: {report_id}")
                        return f"Submission Successful: Report #{report_id}"
                    else:
                        error_text = await resp.text()
                        logger.error(f"H1 Submission Failed ({resp.status}): {error_text}")
                        return f"Submission Failed: {resp.status}"
        except Exception as e:
            logger.error(f"Network Error during submission: {str(e)}")
            return f"Submission Error: {str(e)}"

# Global Instance
bounty_automator = BountyAutomator()
