#!/usr/bin/env python3
"""
Cenário 4: Spike Test - Pico súbito de requisições
Objetivo: Testar resposta do sistema a picos súbitos de carga
"""

from run_single_scenario import run_scenario

SCENARIO = {
    "description": "Spike Test - Pico súbito de requisições",
    "users": 100,
    "spawn_rate": 50,
    "duration": "5m",
    "hpa_enabled": True,
    "objetivo": "Testar resposta do sistema a picos súbitos de carga"
}

if __name__ == "__main__":
    exit(run_scenario("cenario_4_spike", SCENARIO))
