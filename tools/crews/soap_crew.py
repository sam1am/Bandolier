import os
from crewai import Agent, Task, Crew, Process
from langchain.chat_models.openai import ChatOpenAI

# Configure the OpenAI compatible endpoint
openai_endpoint = ChatOpenAI(
    model_name="Mistral-7B-Instruct-v0.2-q4f16_1",  # Replace with your actual model name if different
    openai_api_key="your-api-key",  # Replace with your actual OpenAI API key
    openai_api_base="http://localhost:8000",  # Replace with your custom API endpoint
    # openai_proxy="http://your-proxy-url"  # Replace with your proxy URL if applicable
)

# Transcript Reviewer Agent
transcript_reviewer = Agent(
  role='Transcript Reviewer',
  goal='Review and categorize therapy session transcripts according to the SOAP structure',
  backstory="""Your role involves reading and interpreting therapy session transcripts, then organizing the content
  according to the Subjective, Objective, Assessment, and Plan format.""",
  verbose=True,
  llm=openai_endpoint
)

# Health Information Analyst Agent
health_analyst = Agent(
  role='Health Information Analyst',
  goal='Analyze the categorized session information for in-depth insights',
  backstory="""You analyze organized transcript contents and extract significant clinical details,
  behavioral patterns, and other information relevant to establishing a well-rounded assessment.""",
  verbose=True,
  allow_delegation=True,
  llm=openai_endpoint
)

# Insurance Liaison Analyst Agent
insurance_liaison = Agent(
  role='Insurance Liaison Analyst',
  goal='Identify key insurance-related details in therapy sessions',
  backstory="""Your expertise centers around interpreting insurance requirements.
  You ensure that diagnostic codes, treatment modalities, and clinical justifications are
  documented properly for insurance claims.""",
  verbose=True,
  allow_delegation=True,
  llm=openai_endpoint
)

# SOAP Note Writer Agent
soap_note_writer = Agent(
  role='SOAP Note Writer',
  goal='Compose SOAP notes that integrate clinical and insurance insights',
  backstory="""You specialize in synthesizing complex clinical data into SOAP notes that meet
  both medical and insurance documentation standards.""",
  verbose=True,
  allow_delegation=True,
  llm=openai_endpoint
)

# Define tasks for the CrewAI agents
task1 = Task(
  description="""Review the provided therapy session transcript and categorize the content into
  Subjective, Objective, Assessment, and Plan sections according to the SOAP format.""",
  agent=transcript_reviewer
)

task2 = Task(
  description="""Analyze the reviewed and categorized content to extract significant clinical
  details and behavioral patterns relevant for assessment.""",
  agent=health_analyst
)

task3 = Task(
  description="Identify and document key insurance-related details such as diagnostic codes and treatment modalities.",
  agent=insurance_liaison
)

task4 = Task(
  description="""Use the analyzed clinical information and identified insurance details to write
  comprehensive and accurate SOAP notes suitable for medical records and insurance claims.""",
  agent=soap_note_writer
)

# Instantiate the crew with a sequential process
crew = Crew(
  agents=[transcript_reviewer, health_analyst, insurance_liaison, soap_note_writer],
  tasks=[task1, task2, task3, task4],
  verbose=2,
  process=Process.sequential
)

# Kick off the work!
result = crew.kickoff()

print("######################")
print("Final SOAP Notes:")
print(result)
