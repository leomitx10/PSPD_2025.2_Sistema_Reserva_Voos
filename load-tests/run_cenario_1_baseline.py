#!/usr/bin/env python3
"""
Cenário 1: Baseline - Configuração mínima
Objetivo: Estabelecer baseline de performance sem autoscaling
"""

from run_single_scenario import run_scenario

SCENARIO = {
    "description": "Baseline - Configuração mínima",
    "users": 10,
    "spawn_rate": 5,
    "duration": "5m",
    "hpa_enabled": False,
    "objetivo": "Estabelecer baseline de performance sem autoscaling"
}

if __name__ == "__main__":
    exit(run_scenario("cenario_1_baseline", SCENARIO))
