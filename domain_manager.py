from typing import Tuple, List, Dict
import random
import logging
from logger_config import setup_logger

logger = setup_logger('domain_manager')

class DomainManager:
    def __init__(self, domains: Dict):
        self.domains = domains
        self.last_used = []
        logger.info("DomainManager initialized")

    def select_domain(self) -> Tuple[str, str, List[str]]:
        """Select domain, subdomain, and keywords while avoiding recent choices"""
        try:
            # Filter out recently used domains
            available_domains = [d for d in self.domains.keys() 
                              if d not in self.last_used[-2:]]
            
            if not available_domains:
                available_domains = list(self.domains.keys())
                logger.info("Reset available domains due to all being recently used")

            # Select domain and subdomain
            domain = random.choice(available_domains)
            subdomain = random.choice(list(self.domains[domain].keys()))
            keywords = self.domains[domain][subdomain][:3]

            # Update last used
            self.last_used.append(domain)
            if len(self.last_used) > 3:
                self.last_used.pop(0)

            logger.info(f"Selected domain: {domain}, subdomain: {subdomain}")
            return domain, subdomain, keywords

        except Exception as e:
            logger.error(f"Error in domain selection: {e}")
            raise