from pydantic_ai import Agent

criteria = """
The application limits the use of personal information to the strict minimum required
to provide the service.
"""

code_repository = "https://github.com/MTES-MCT/apilos/"

agent = Agent(
    "anthropic:claude-sonnet-4-0",
    instructions=f"Analyze the code repository {code_repository} and check if it meets"
    f" the following criteria: {criteria}",
)

result = agent.run_sync(
    f"Analyze the code repository {code_repository} and check if it meets the following"
    f" criteria: {criteria}"
)

print(result.output)
