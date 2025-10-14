import asyncio
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.run.workflow import WorkflowRunEvent
from agno.workflow.step import Step
from agno.workflow.steps import Steps
from agno.workflow.types import StepOutput, StepInput
from agno.workflow.parallel import Parallel
from agno.workflow.workflow import Workflow

def my_sum(a: int, b: int) -> int:
    return a + b

def my_mul(a: int, b: int) -> int:
    return a * b

def build_agent(instructions: str) -> Agent:
    return Agent(
        instructions=instructions,
        model=Ollama(id='qwen3:1.7b'),
        tools=[my_sum]
    )

def remove_think(text: str) -> str:
    thinking = text.rfind("</think>")
    if thinking != -1:
        return text[thinking + len("</think>"):].strip()
    return text.strip()

def combine_steps_output(inputs: StepInput) -> StepOutput:
    parallel = inputs.get_step_content("parallel")
    if not isinstance(parallel, dict): return StepOutput()

    lang = remove_think(parallel.get("Lang", ""))
    answer = remove_think(parallel.get("Predict", ""))
    content = f"Language: {lang}\nPhrase: {answer}"
    return StepOutput(content=content)

async def main():
    query = "Quanto fa 50 + 150 * 50?"

    s1 = Step(name="Translate", agent=build_agent(instructions="Transform in English the user query. DO NOT answer the question and output ONLY the translated question."))
    s2 = Step(name="Predict", agent=build_agent(instructions="You will be given a question in English. You can use the tools at your disposal. Answer the question and output ONLY the answer."))

    step_a = Step(name="Lang", agent=build_agent(instructions="Detect the language from the question and output ONLY the language code. Es: 'en' for English, 'it' for Italian, 'ja' for Japanese."))
    step_b = Steps(name="Answer", steps=[s1, s2])
    step_c = Step(name="Combine", executor=combine_steps_output)
    step_f = Step(name="Final", agent=build_agent(instructions="Translate the phrase in the language code provided. Respond only with the translated answer."))

    wf = Workflow(name="Pipeline Workflow", steps=[
        Parallel(step_a, step_b, name="parallel"),  # type: ignore
        step_c,
        step_f
    ])

    result = ""
    async for event in await wf.arun(query, stream=True, stream_intermediate_steps=True):
        content = getattr(event, 'content', '')
        step_name = getattr(event, 'step_name', '')

        if event.event in [WorkflowRunEvent.step_completed]:
            print(f"{str(event.event)} --- {step_name} --- {remove_think(content).replace('\n', '\\n')[:80]}")
        if event.event in [WorkflowRunEvent.workflow_completed]:
            result = remove_think(content)
    print(f"\nFinal result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
