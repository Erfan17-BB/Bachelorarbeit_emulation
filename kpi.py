from dataclasses import dataclass

# Kpi-Klasse

@dataclass
class Kpi:

    created_items : int = 0
    wip : int = 0 # umlaufbestand
    tp_all : int = 0 # gesamtdurchsatz
    tp_1 : int = 0 # durchsatz lane 1
    tp_2 : int = 0
    tp_3 : int = 0