from flask import Flask, render_template, request, redirect, url_for, session
import os
import copy
import requests

app = Flask(__name__)

app.secret_key = "supersecretkey"

# Fetch environment variables for Azure OpenAI API
azure_openai_endpoint = os.getenv(
    "ENDPOINT_URL", ""
)
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4-o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")

# List to store user inputs and corresponding outputs
conversations = []
chat_data=[[] for i in range(15)]

# Function to call Azure OpenAI API
def get_openai_response(user_input):
    try:
        # Making the chat completion call to Azure OpenAI
        url = "https://name.openai.azure.com/openai/deployments/gpt-4-o/chat/completions?api-version=2024-09-01-preview"

        chat_num= session['chat_number']
        conversation_history = [{"role": "system", "content": "you are an assistant to provide help, try to answer correctly based on the previous conversation given"}]
        # print(chat_data[chat_num%15])
        for input, message in chat_data[chat_num%15]:
            conversation_history.append({"role": "user", "content": input})
            conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "user", "content": user_input})
        # Example data to send
        print(conversation_history)
        data = {
            # "messages": [
            #     {"role": "system", "content": "you are an old grumpy lady who insults incessantly"},
            #     {"role": "user", "content": user_input},
            # ],
            "messages": conversation_history,
            "max_tokens": 1000,
        }

        # Send POST request
        response = requests.post(
            url, json=data, headers={"api-key": ""}
        )

        data = response.json()
        # Return the response text

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "Error with OpenAI API."


@app.route("/", methods=["GET", "POST"])
def index():
    if 'chat_number' not in session:
        session['chat_number'] = 0
    if 'at_prev' not in session:
        session['at_prev'] = 0

    print(session['chat_number'])

    if request.method == "POST":
        user_input = request.form["search"]
        if user_input:
            # Call the OpenAI API to get a response
            print(user_input)
            response = get_openai_response(user_input)
            chat_num= session['chat_number']
            # Save both the input and the response in the conversations list
            chat_data[chat_num%15].append((user_input,response))
            print("here",chat_data)
            conversations.append((user_input, response))
            return redirect(url_for("index"))
    return render_template("index.html", conversations=conversations)

@app.route('/new_chat', methods=['POST'])
def new_chat():
    if session['at_prev'] == 0:
        session['chat_number'] += 1
    else:
        session['chat_number'] += 2
    session['at_prev'] = 0
    conversations.clear()
    return redirect(url_for('index'))

@app.route('/prev_chat', methods=['POST'])
def prev_chat():
    global conversations
    if session['chat_number'] > 0 :
        session['chat_number'] -= 1
        session['at_prev']= 1
    # conversations.clear()
    conversations = [item for item in chat_data[session['chat_number'] % 15]]
    print("conversations", conversations)
    print('\n chat his', chat_data)
    return redirect(url_for('index'))

@app.route('/current_chat', methods=['POST'])
def current_chat():
    global conversations
    if session['at_prev'] == 1:
        session['chat_number'] += 1
        conversations = [item for item in chat_data[session['chat_number'] % 15]]
    session['at_prev'] = 0
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)



