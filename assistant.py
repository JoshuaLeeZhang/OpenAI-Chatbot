from openai import OpenAI
import gradio as gr

client = OpenAI()

thread = client.beta.threads.create()

def response(input, chat_history):
    """
    Handles user input, sends it to the assistant API via client.beta.threads,
    and appends the assistant's reply to the chat history.
    """

    if not input:  # Check if `message` is empty or contains only whitespace
        return "", chat_history  # Return without making changes
    
    try:
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id="asst_J78F690jublREg0AXTjIzGEC"
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            reply = messages.data[0].content[0].text.value
    except Exception as e:
        reply = f"Error: {str(e)}"

    chat_history.append((input, reply))
    return "", chat_history

theme = gr.themes.Base(
    primary_hue="green",
    font=["Roboto", "Arial", "sans-serif"],
    text_size="md",
    spacing_size="md",
    radius_size="md"
)

css = """
    body {
        font-family: 'Roboto', Arial, sans-serif !important;
    }
    .block {
        padding: 10px !important;  /* More spacing */
    }
"""

with gr.Blocks(theme = theme, css=css) as demo:
    chatbot = gr.Chatbot(show_label = False)
    with gr.Row(equal_height=True):
        msg = gr.Textbox(show_label=False, placeholder="Type a message...", scale=3)
        submitButton = gr.Button("Submit", scale=1)
    
    gr.on(
        triggers = [msg.submit, submitButton.click],
        fn = response,
        inputs = [msg, chatbot],
        outputs = [msg, chatbot]
    )

demo.launch(share=True)
