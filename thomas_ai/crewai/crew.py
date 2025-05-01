import os
from typing import List

from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from django.conf import settings

llm = LLM(
    model= "mistral/" + settings.MISTRAL_MODEL,
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
    def transcription_improver(self) -> Agent:
        return Agent(
            config=self.agents_config['transcription_improver'],
            verbose=settings.DEBUG,
            llm=llm,
        )

    @agent
    def task_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['task_manager'],
            verbose=settings.DEBUG,
            llm=llm,
        )

    @task
    def transcription_improvement(self) -> Task:
        return Task(
            config=self.tasks_config['transcription_improvement']
        )

    @task
    def transcription_to_tasks(self) -> Task:
        return Task(
            config=self.tasks_config['transcription_to_tasks']
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
