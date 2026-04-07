import unittest
from engine.parser import parse_strategy_targets, parse_protection_targets
from engine.calculator import get_neighbors, get_terminal_numbers
from engine.core import StrategyState
from engine.registry import registry

class TestEngine(unittest.TestCase):
    def test_calculator_neighbors(self):
        # 0 neighbors (1): 26, 0, 32
        neighbors = get_neighbors(0, 1)
        self.assertIn(0, neighbors)
        self.assertIn(26, neighbors)
        self.assertIn(32, neighbors)
        self.assertEqual(len(neighbors), 3)

    def test_calculator_terminals(self):
        t1 = get_terminal_numbers(1)
        self.assertEqual(sorted(t1), [1, 11, 21, 31])

    def test_parser_basic(self):
        # "T1 e T3 com 1 vizinho"
        # T1: 1, 11, 21, 31 -> neighbors(1) for each
        # T3: 3, 13, 23, 33 -> neighbors(1) for each
        targets = parse_strategy_targets("T1 e T3 com 1 vizinho")
        self.assertTrue(len(targets) > 0)
        # Check specific known neighbors
        # 1 neighbors: 33, 1, 20
        self.assertIn(1, targets)
        self.assertIn(33, targets)
        self.assertIn(20, targets)

    def test_parser_complex_numbers(self):
        # "9 / 19 / 29 com 2 vizinhos"
        targets = parse_strategy_targets("9 / 19 / 29 com 2 vizinhos")
        self.assertIn(9, targets)
        self.assertIn(19, targets)
        self.assertIn(29, targets)
        # Check neighbors of 9 (31, 22) (2 neighbors = 14, 31, 9, 22, 18)
        self.assertIn(31, targets)
        self.assertIn(14, targets)

    def test_parser_protection(self):
        targets = parse_protection_targets("T4 / T7")
        self.assertIn(4, targets)
        self.assertIn(14, targets)
        self.assertIn(7, targets)
        
        targets2 = parse_protection_targets("33, 5, 10")
        self.assertIn(33, targets2)
        self.assertIn(5, targets2)
        self.assertIn(10, targets2)

    def test_strategy_state(self):
        state = StrategyState(max_attempts=3)
        state.activate(1, 10, [1, 2, 3], [0]) # ID 1, Start 10, Winners [1,2,3], Protection [0]
        
        # Test Protection (Wait)
        self.assertEqual(state.process_number(99), "PROTECTION")
        self.assertEqual(state.attempt, 1)
        
        # Test Win Entry
        self.assertEqual(state.process_number(1), "WIN_ENTRY")
        
        # Reset and test Win Protection
        state.reset()
        state.activate(1, 10, [1], [0])
        self.assertEqual(state.process_number(0), "WIN_PROTECTION") # Logic 0 is win/protection
        
        # Test Loss
        state.reset()
        state.activate(1, 10, [1], [])
        state.process_number(99) # 1
        state.process_number(99) # 2
        state.process_number(99) # 3
        self.assertEqual(state.process_number(99), "LOSS") # 4 -> Loss

    def test_registry_preload(self):
        count = registry.preload()
        self.assertTrue(count > 0)
        strat = registry.get_strategy(1) # T1 + T3
        self.assertIsNotNone(strat)
        self.assertTrue(len(strat['entry']) > 0)

if __name__ == '__main__':
    unittest.main()
