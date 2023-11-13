import time
import gradio as gr

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from openai import OpenAI
client = OpenAI()

#--------------------------------------
#Creating a global assistant object
#--------------------------------------
my_assistant = client.beta.assistants.create(
    instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
    name="AI Math Tutor",
    tools=[{"type": "code_interpreter"}],
    model="gpt-3.5-turbo-1106"
)

#--------------------------------------
# #Creating a global thread object
#--------------------------------------
chat_thread = client.beta.threads.create()

#--------------------------------------
#Gradio callback after user enters text
#--------------------------------------
def slow_echo(usr_message, history):
  print(f"[Debug] -> User query is [{usr_message}]\n")

  #--create a message based on user's query
  msg = client.beta.threads.messages.create(
    thread_id=chat_thread.id,
    role="user",
    content=usr_message
  )
  print(f"[Debug] -> Sent message to assistant ...\n")  

  #--run the query on the assistant's thread
  run = client.beta.threads.runs.create(
    thread_id=chat_thread.id,
    assistant_id=my_assistant.id,
    instructions="Please be polite when you answer the queries."
  )

  #--wait for the completion and post it back on the chat messages
  while run.status != 'completed' and run.status != 'failed' :
    print(f"Waiting for run to complete. Current status is {run.status}\n")
    run = client.beta.threads.runs.retrieve(
            thread_id=chat_thread.id,
            run_id=run.id
    )
    print(f"Current Run ID is {run.id}\n")
    time.sleep(0.2)

  #--store the current run to match it with the right response from the thread
  current_run = run.id

  messages = client.beta.threads.messages.list(
    thread_id=chat_thread.id
  )

  #--- look for the specific response to a run_id
  #--- have requested this as an enhancement to openai
  #--- https://community.openai.com/t/assistant-api-sdk-enhancement-get-message-by-run-id/484468
  for message in messages.data:
    if message.role == 'assistant' and message.run_id == current_run:
        response = message.content[0].text.value
        yield response

demo = gr.ChatInterface(slow_echo,
                        title="AI Math Tutor",
                        description="AI Math Tutor is a virtual learning assistant that provides personalized math instruction, explanations, and practice problems to help you improve your math skills.",
                        theme="soft",
                        examples=["What is the square root of 256", "Explain BODMAS rule?", "25th Fibonacci number?"],
                        retry_btn=None,
                        undo_btn=None,
                        clear_btn=None).queue()

if __name__ == "__main__":
    demo.launch()
        
