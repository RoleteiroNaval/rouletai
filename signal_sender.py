#!/usr/bin/env python3
"""
Signal Sender - Professional Bot Interface for Voice Agent V4
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass
from typing import Dict, Optional
from voice_bridge import VoiceBridge

log = logging.getLogger('signal_sender')

import os
from dotenv import load_dotenv
load_dotenv('config/.env')

@dataclass
class Signal:
    number: int
    strategy: str
    confidence: int
    priority: str = 'NORMAL'  # LOW, NORMAL, HIGH, CRITICAL
    source: str = 'bot'

class ProfessionalSignalSender:
    def __init__(self, voice_bridge: VoiceBridge):
        self.bridge = voice_bridge
        self.metrics = {
            'sent': 0,
            'latency_avg': 0,
            'latency_samples': []
        }
        print("Conectando ao servidor:", self.bridge.server_url)
        print("Token carregado:", self.bridge.token)
        
    def create_signal(self, number: int, strategy: str, confidence: int = 80) -> Dict:
        """Create validated production signal"""
        latency = random.randint(10, 50)  # Simulated latency
        
        priority_map = {
            confidence: 'LOW',
            75: 'NORMAL', 
            85: 'HIGH',
            95: 'CRITICAL'
        }
        
        priority = next((p for c, p in sorted(priority_map.items(), reverse=True) if confidence >= c), 'LOW')
        
        signal = {
            'action': 'signal',
            'token': self.bridge.token,
            'data': {
                'number': number,
                'strategy': strategy,
                'confidence': confidence,
                'priority': priority,
            },
            'latency': latency,
            'time': time.strftime('%H:%M:%S'),
        }
        
        log.info(f'Signal created | {number}/{strategy} | conf:{confidence}% prio:{priority}')
        return signal
    
    async def send(self, signal: Dict):
        """Send with metrics"""
        start = time.time()
        self.bridge._send_async(signal)
        latency = (time.time() - start) * 1000
        
        self.metrics['sent'] += 1
        self.metrics['latency_samples'].append(latency)
        if len(self.metrics['latency_samples']) > 100:
            self.metrics['latency_samples'] = self.metrics['latency_samples'][-100:]
        self.metrics['latency_avg'] = sum(self.metrics['latency_samples']) / len(self.metrics['latency_samples'])
        
        log.info(f'METRIC sent:{self.metrics["sent"]} latency:{latency:.1f}ms avg:{self.metrics["latency_avg"]:.1f}')
    
    async def test_loop(self):
        """Test signal generator"""
        strategies = ['T5', 'T7', 'D3', 'P9']
        numbers = list(range(0, 37))
        
        while True:
            number = random.choice(numbers)
            strategy = random.choice(strategies)
            confidence = random.randint(70, 100)
            
            signal = self.create_signal(number, strategy, confidence)
            await self.send(signal)
            
            await asyncio.sleep(random.uniform(1, 5))

async def main():
    logging.basicConfig(level=logging.INFO)
    bridge = VoiceBridge()
    await asyncio.sleep(2)  # Wait connect
    
    sender = ProfessionalSignalSender(bridge)
    
    # Test single
    # signal = sender.create_signal(17, 'T5', 92)
    # await sender.send(signal)
    
    # Test continuous
    await sender.test_loop()

if __name__ == '__main__':
    asyncio.run(main())

