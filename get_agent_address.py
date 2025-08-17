#!/usr/bin/env python3
"""
Simple script to get the FitAgent address without running the full agent
"""

from uagents import Agent

# Create agent with same configuration to get the address
fitagent_coach = Agent(
    name="fitagent_nutrition_coach",
    port=8081,
    seed="fitagent_coach_seed_phrase_for_consistency",
    mailbox=True,
    endpoint=["http://localhost:8081/submit"]
)

print(f"\n🤖 FitAgent Nutrition Coach Address:")
print(f"📍 {fitagent_coach.address}")
print(f"\n🔗 Agent Inspector URL:")
print(f"https://agentverse.ai/inspect/?uri=http://localhost:8081&address={fitagent_coach.address}")
print(f"\n📋 Use this address in your client code:")
print(f'FITAGENT_COACH_ADDRESS = "{fitagent_coach.address}"')
print()
