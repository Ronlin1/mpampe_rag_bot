from flask import Flask, render_template, request
import openai
import os
import requests

openai.api_type = "azure"
# Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
openai.api_version = "2023-08-01-preview"

# Azure OpenAI setup
openai.api_base = "https://mpampe.openai.azure.com/"  # Add your endpoint here
openai.api_key = os.getenv("OPENAI_API_KEY")  # Add your OpenAI API key here
deployment_id = "MpaMpe"  # Add your deployment ID here

# Azure AI Search setup
search_endpoint = "https://finetunempampe.search.windows.net"  # Add your Azure AI Search endpoint here
search_key = os.getenv("SEARCH_KEY")  # Add your Azure AI Search admin key here
search_index_name = "mpampedata"  # Add your Azure AI Search index name here

def setup_byod(deployment_id: str) -> None:
    """Sets up the OpenAI Python SDK to use your own data for the chat endpoint.

    :param deployment_id: The deployment ID for the model to use with your own data.

    To remove this configuration, simply set openai.requestssession to None.
    """

    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    # Mount a custom adapter which will use the extensions endpoint for any call using the given `deployment_id`
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )

    openai.requestssession = session

setup_byod(deployment_id)

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    if request.method == "POST":
        msg = request.form["msg"]
        response = get_chat_response(msg)
        return response

def get_chat_response(prompt):
    # Define the conversation using the Azure OpenAI API
    message_text = [
        {"role": "user", "content": prompt},
    ]

    # Generate response using Azure OpenAI
    completion = openai.ChatCompletion.create(
        messages=message_text,
        deployment_id=deployment_id,
        dataSources=[
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": search_endpoint,
                    "indexName": search_index_name,
                    "semanticConfiguration": "default",
                    "queryType": "simple",
                    "fieldsMapping": {},
                    "inScope": True,
                    "roleInformation": "You are an AI assistant that helps people find information.",
                    "filter": None,
                    "strictness": 3,
                    "topNDocuments": 5,
                    "key": search_key
                }
            }
        ],
        enhancements=None,
        temperature=0,
        top_p=1,
        max_tokens=800,
        stop=None,
        stream=True
    )

    # Extract response from API result
    # print(list(completion))
    # print("-----")
    
    # Extract response from API result
    bot_response = ""

    for chunk in completion:
        if 'choices' in chunk:
            for choice in chunk['choices']:
                if 'content' in choice['delta']:
                    bot_response += choice['delta']['content']
    # print("-----")
    print(bot_response)
    
    return bot_response

if __name__ == '__main__':
    app.run()


