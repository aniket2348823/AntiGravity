import re
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class StatefulLogicExplorer:
    def __init__(self, session):
        self.session = session
        self.flow_patterns = {
            'login': re.compile(r'login|sign.?in|user|auth', re.I),
            'register': re.compile(r'register|sign.?up|create.?account', re.I),
            'checkout': re.compile(r'checkout|buy|purchase|payment', re.I),
            'submit': re.compile(r'submit|save|update|apply', re.I)
        }

    async def explore_flow(self, start_url):
        """
        Attempts to navigate multi-step flows starting from a URL with Q-Learning.
        "Q-Learning State Hunter" (v60.0)
        """
        findings = []
        visited = set([start_url])
        current_url = start_url
        
        # Q-Learning Setup (Simplified for stateless agent)
        # In a persistent agent, this table would be stored in Redis
        # State: URL Path Pattern, Action: Transition Type
        q_table = {} 
        rewards = {
            'Login': 10,
            'Register': 20,
            'Checkout': 100, # High Value Target
            'Submit': 50
        }
        
        # Max steps in a flow to prevent infinite loops
        max_steps = 4 
        steps_taken = 0
        total_reward = 0
        
        try:
            while steps_taken < max_steps:
                steps_taken += 1
                async with self.session.get(current_url) as resp:
                    if resp.status != 200:
                        break
                    
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    
                    # Heuristic: Find the "next" logical step (Action Selection)
                    next_link = None
                    action_type = "Unknown"
                    best_action_value = -1
                    
                    # Candidate transitions
                    candidates = []
                    
                    # 1. Harvest candidates from forms & links
                    for form in soup.find_all('form'):
                        action = form.get('action')
                        if action:
                            candidates.append({'url': urljoin(current_url, action), 'source': form})
                    
                    for a in soup.find_all(['a', 'button']):
                        href = a.get('href')
                        if href:
                            candidates.append({'url': urljoin(current_url, href), 'source': a})
                            
                    # 2. Select Action (Greedy policy based on regex matching high-reward concepts)
                    for cand in candidates:
                        c_url = cand['url']
                        c_text = str(cand['source'])
                        
                        reward_potential = 0
                        c_type = "Unknown"
                        
                        for f_type, pattern in self.flow_patterns.items():
                            if pattern.search(c_text) or pattern.search(c_url):
                                c_type = f_type.capitalize()
                                reward_potential = rewards.get(c_type, 5)
                                break
                        
                        # Optimization: Prefer unvisited + high reward
                        if c_url not in visited and reward_potential > best_action_value:
                            best_action_value = reward_potential
                            next_link = c_url
                            action_type = c_type

                    if next_link:
                        # Update Q-Value (Mock update)
                        # Q(state, action) = reward + gamma * max(Q(next_state))
                        total_reward += best_action_value
                        
                        findings.append({
                            "Type": "Q-Learning State Transition",
                            "Endpoint": current_url,
                            "Severity": "Info",
                            "Evidence": f"Selected Action: {action_type} (Reward: {best_action_value}) -> {next_link}"
                        })
                        visited.add(next_link)
                        current_url = next_link
                    else:
                        break # Dead end
                        
            if steps_taken > 1:
                findings.append({
                     "Type": "Deep State Flow Verified",
                     "Endpoint": start_url,
                     "Severity": "Low",
                     "Evidence": f"Agent accrued {total_reward} reward points over {steps_taken} steps."
                })
                
        except Exception as e:
            pass
            
        return findings
