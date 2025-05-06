import os
from typing import List

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from django.conf import settings

llm = LLM(
    model="mistral/" + settings.MISTRAL_MODEL,
    temperature=float(settings.MISTRAL_MODEL_TEMPERATURE),
    api_key=settings.MISTRAL_API_KEY,
)


@CrewBase
class AnalyzerCrew:
    agents: List[BaseAgent]
    tasks: List[Task]

    def get_nb_agents(self):
        return len(self.agents)

    @agent
    def thomas(self) -> Agent:
        return Agent(
            config=self.agents_config['thomas'],
            verbose=True,
            llm=llm,
        )

    @task
    def analyse_transcription(self) -> Task:
        return Task(
            config=self.tasks_config['analyse_transcription'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=settings.DEBUG,
            name='Thomas Crew',
        )
