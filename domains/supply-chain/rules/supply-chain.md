---
description: "Supply chain domain rules and patterns"
---
# Supply Chain — Reglas del dominio

## Carrier Management
- Carrier scorecards: on-time %, damage rate, cost per unit, responsiveness
- RFP process: lane analysis → bid solicitation → award → monitoring
- Rate validation: compare against market indices + historical
- Contingency carriers para cada lane crítica

## Inventory & Demand
- ABC/XYZ classification para priorizar atención
- Safety stock = f(demand variability, lead time variability, service level)
- Forecast accuracy medida con MAPE/MAD — track por SKU
- Seasonal transitions: phase-in/phase-out con markdown strategy

## Logistics Exceptions
- Escalation tiers: L1 (auto-resolve), L2 (analyst), L3 (manager), L4 (VP)
- Claims: documentation → filing → follow-up → recovery tracking
- Root cause categories: carrier, weather, customs, warehouse, supplier

## Customs & Trade
- HS Code: clasificar al nivel de 6+ dígitos con ruling references
- Incoterms: documentar responsibilities en cada shipment
- FTA utilization: verify rules of origin antes de reclamar preferencia
- Denied party screening obligatorio antes de cada shipment

## Anti-patrones
- Forecasts sin medición de accuracy — siempre track MAPE
- Safety stock estático — recalcular periódicamente
- Claims sin documentación fotográfica
- HS classification sin verificar contra rulings previos
