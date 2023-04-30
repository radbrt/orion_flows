import torch
from instruct_pipeline import InstructionTextGenerationPipeline
from transformers import AutoModelForCausalLM, AutoTokenizer
from prefect import flow, get_run_logger
from prefect.blocks.notifications import SlackWebhook



@flow(name="Dolly Slackbot")
def dolly_slackbot(question: str = "Tell me an untrue fact about the book 'Hitchiker's Guide to the Galaxy'"):
    logger = get_run_logger()
    logger.info("Starting Dolly Slackbot")
    tokenizer = AutoTokenizer.from_pretrained("/model/", padding_side="left", local_files_only=True, low_cpu_mem_usage=True)
    model = AutoModelForCausalLM.from_pretrained("/model/", torch_dtype=torch.bfloat16, local_files_only=True, low_cpu_mem_usage=True)

    generate_text = InstructionTextGenerationPipeline(model=model, tokenizer=tokenizer)

    slack_webhook_block = SlackWebhook.load("radbrt")

    engineered_prompt = f"""Create a long response to the prompt marked by triple single quotes.

    '''{question}'''
    """

    res = generate_text(engineered_prompt)
    res_text = res[0]["generated_text"]
    slack_webhook_block.notify(res_text)


if __name__ == '__main__':
    dolly_slackbot()


