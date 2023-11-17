import os
import random as rn
import streamlit as st
from dotenv import load_dotenv

### Langchain libraries
from langchain.agents import Tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import  PromptTemplate
from langchain.schema.messages import SystemMessage
from langchain.sql_database import SQLDatabase
from langchain.vectorstores import PGVector
from langchain_experimental.sql import SQLDatabaseChain
from langchain.callbacks import StreamlitCallbackHandler
import socket
from lib.boon import BoonCaptureStdout

### Configure Streamlit app
st.set_page_config( page_title="Boon Solutions ChatGPT", page_icon="https://www.boon.com.au/wp-content/uploads/2022/09/favicon.png", )

### Load environment variables. using path so that we can allow k8s stateful replica to have individual config files
@st.cache_data
def load_chatbot_env():
    hostname = socket.gethostname()
    print("Hostname:", hostname)

    env_path = os.path.join('.', 'config', hostname, 'chatbot.env')
    load_dotenv(dotenv_path=env_path)

load_chatbot_env()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
ENCRYPT_KEY = os.environ.get("ENCRYPT_KEY")
CDAO_SQL_CHAT_URI = os.environ.get("CDAO_SQL_CHAT_URI")
CDAO_SQL_VECTOR_URI = os.environ.get("CDAO_SQL_VECTOR_URI")


print("OPENAI_API_KEY last 6 characters:", OPENAI_API_KEY[-6:])


### Get URL parameters
url_params = st.experimental_get_query_params()
try:        pid = url_params["pid"]
except:     pid = "USR"
if pid == "USR":    response = "Hello, **anonymous** user.  \n  \nHere are some example prompts:  \n- I'm participant [number]  \n- What's the highest guess?  \n- What can you do?  \n- knock knock  \n  \nYou can type your prompt or use the **I'm feeling lucky** button below." 
else:   response = "Hello, participant **"+pid+"**  \n  \nHere are some example prompts:  \n- What was my guess?  \n- What's the highest guess?  \n- What can you do?  \n- knock knock  \n  \nYou can type your prompt or use the **I'm feeling lucky** button below."

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token# + "/"
        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text)
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")


### Setup OpenAIEmbeddings
@st.cache_resource
def load_open_ai_embeddings_engine():
    return OpenAIEmbeddings()

# TODO - try catch
embeddings = load_open_ai_embeddings_engine()


### Load Questions
@st.cache_data
def load_questions():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return open(dir_path+"/questions/questions.txt", "r").read().split("\n")

# TODO - try catch
suggest_opts = load_questions()


### Load system messages
@st.cache_data
def load_system_message():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    system_message_text = open(dir_path+"/agent-description/system-message.txt", "r").read()
    print(system_message_text)
    return SystemMessage(content=system_message_text)

# TODO - try catch
system_message = load_system_message()


### Setup Vector Database Connection
@st.cache_resource
def load_pgvector():
    return PGVector(
        connection_string=CDAO_SQL_VECTOR_URI,
        embedding_function=embeddings,)
try:
    db_pg = load_pgvector()
except ConnectionError:
    st.error('Vector Database connection failed. Please try again later.')
    # TODO - should we just exit(1) and then let docker/k8s restart pod?

### Setup Competition Database Connection
@st.cache_resource
def load_competition_db():
    return SQLDatabase.from_uri(CDAO_SQL_CHAT_URI, include_tables=['competition'],)
try:
    db_sql = load_competition_db()
except ConnectionError:
    st.error('Database connection failed. Please try again later.')
    # TODO - should we just exit(1) and then let docker/k8s restart pod?

### Setup LLM
@st.cache_resource
def load_chat_open_ai(model, temperature=0, verbose=True, streaming=True):
    return ChatOpenAI(temperature=temperature, model_name=model, request_timeout=30, verbose=verbose, streaming=streaming, )
### Assign LLM model and temperature to each Agent
llm_master              = load_chat_open_ai("gpt-4",temperature=0.3) # set to 4 in prod. set temp to 0.3 to allow for riddles and jokes
llm_pg_retriever        = load_chat_open_ai("gpt-4") # seems to be ok at 3.5
llm_db_agent            = load_chat_open_ai("gpt-4") # set to 4 in prod
llm_fallback            = load_chat_open_ai("gpt-4",temperature=0.3) # set to 4 in prod
### Set default session state values
st.session_state.setdefault("is_first_load", 1 if "is_first_load" not in st.session_state else 0)
st.session_state.setdefault("messages", [{"role": "assistant", "content": response}])
st.session_state.setdefault("suggested", False)
st.session_state.setdefault("random_opts", suggest_opts[:])


### Create MainAgent Prompt Template
prompt_template = PromptTemplate(
    input_variables=["input"],
    template="The user has asked: {input}",)

# TODO - try catch


### Create SQL SubAgent
@st.cache_resource
def load_sql_db_chain(_llm_db_agent, _db_sql ):
    return SQLDatabaseChain.from_llm(
    _llm_db_agent,
    db=_db_sql,
    verbose=True,
    use_query_checker=True,)


### Create PG Retriever SubAgent
@st.cache_resource
def load_pg_retriever_chain(_llm_pg_retriever, _db_pg):
    return RetrievalQA.from_chain_type(
    llm=_llm_pg_retriever,
    chain_type="stuff",
    retriever=_db_pg.as_retriever(),)


db_agent = load_sql_db_chain(llm_db_agent, db_sql );
pg_retriever = load_pg_retriever_chain(llm_pg_retriever, db_pg)


### Load SQL SubAgent tool description for system
@st.cache_data
def load_sql_agent_description():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tool_description = open(dir_path+"/agent-description/sql-agent.txt", "r").read()
    print(tool_description)
    return tool_description


### Load PGVector Retriever SubAgent tool description for system
@st.cache_data
def load_pgvector_agent_description():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    tool_description = open(dir_path+"/agent-description/pgvector-agent.txt", "r").read()
    print(tool_description)
    return tool_description


### Assign SubAgents as tools to MainAgent
tools = [
    Tool(
        name="SQLAgent",
        description=load_sql_agent_description(),
        #func=sql_agent.run,),
        fail_on_error=False,
        fallbacks=[llm_fallback],
        func=db_agent.run,
        handle_tool_error=True,),
        
    Tool(
        name="PGVectorRetriever",
        description=load_pgvector_agent_description(),
        fail_on_error=False,
        fallbacks=[llm_fallback],
        func=pg_retriever,),
]


### Create MainAgent
if "conversation" not in st.session_state:
    st.session_state.conversation = create_conversational_retrieval_agent(
    llm=llm_master,
    tools=tools,
    verbose=True,
    prompt=prompt_template,
    handle_parsing_errors=True,
    remember_intermediate_steps=True,
    max_token_limit=3000,
    system_message=system_message, 
    handle_tool_error=True,)


### Define function to fix formatting for bot thought printing
def escape_markdown(s):
    if s.startswith(">") and not s.startswith("> "): # the fish ><(((('> question will cause the tail to be cut off during display as it is though to be a codeblock when > is in use. this is a hack to get around it.
        return "\\" + s
    return s.replace('```\n', "```\n\u200b") # st.code removes all leading whitespace. check css you'll notice a span with a class of stEmotionCache. this is the culprit. the \u200b is a zero width space. it's a hack to get around this.


### Custom CSS style to bypass Streamlit's default appearance
prod_style = """
        <style>
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .head {
                font-size: 24px;
                text-align: center;
            }
            .para {
                font-size: 14px;
                text-align: center;
            }
            .stChatFloatingInputContainer {
                z-index: 1;
                padding-bottom: 100px;
            }
            .stButton {
                position: fixed;
                bottom: 10px;
                padding-bottom: 10px;
                z-index: 2;
                padding-top: 19;
                padding-bottom: 19;
            }
            .st-emotion-cache-1d4fjg1 {
                color: #0074c6;
                border-top-color: #0074c6 !important;
                border-bottom-color: #0074c6 !important;
                border-left-color: #0074c6 !important;
                border-right-color: #0074c6 !important;
            }        
             .st-emotion-cache-9ilocf {
                 color: #0074c6 !important;
            } 
            hr {
                margin-top: 0px;
            }   
            code {
                font-family: monospace, 'Courier New', monospace;
            }           
            .block-container { padding-top: 5px !important;}
        </style>
            """


### _____     _____     Run Streamlit App    _____     _____     ###
### Load custom CSS style
st.markdown(prod_style, unsafe_allow_html=True)
### App header
st.markdown("""
    <p class="head">Boon Solutions ChatGPT</p>
    <p class="para">CDAO Perth 2023 GPT-4</p>
    <p class="para">Competition Result: There were 1,112 pieces of LEGO in the jar and participant 46 had the winning guess at 1,111</p>
    """,unsafe_allow_html=True) # Added competition result to the header
st.divider()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(escape_markdown(message["content"]), unsafe_allow_html=True)   
suggest = st.button(label="I'm feeling lucky",use_container_width=True)
prompt = st.chat_input(placeholder="Ask me anything here")
### Randomly input prompt when lucky button is pressed
if suggest:
    prompt = rn.choice(st.session_state.random_opts)
    st.session_state.random_opts.remove(prompt)
    if len(st.session_state.random_opts) == 0:
        st.session_state.random_opts = suggest_opts[:]
### Inject participant id into memory on first load if the id is available
if st.session_state.is_first_load == 1 and pid != "USR":
        with BoonCaptureStdout() as capture:
            st.session_state.conversation.memory.chat_memory.add_user_message("I'm participant "+str(pid))
            st.session_state.conversation.memory.chat_memory.add_ai_message("Hello. Participant "+str(pid))
            #Trace ONLY 
            print(st.session_state.conversation.memory.chat_memory)            
        st.session_state.is_first_load = 0
### Process prompt
if prompt :
    with st.chat_message(name="user",):
        st.markdown(escape_markdown(prompt), unsafe_allow_html=True)
        st.session_state.messages.append({"role":"user","content":prompt})  
    try:
        with st.chat_message(name="assistant",):
            with BoonCaptureStdout() as capture:
                st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
                response = st.session_state.conversation({"input": prompt}, callbacks=[st_callback])

            st.session_state.messages.append({"role":"assistant","content":response["output"]})  

            with st.expander("Show/Hide Work",expanded=False):    
                st.write(capture.get_output(), unsafe_allow_html=True)
                               
            st.write(escape_markdown(response["output"]), unsafe_allow_html=True)
            print(st.session_state.conversation.memory.chat_memory) #Trace ONLY 
###
    except Exception as e:
        with st.chat_message(name="assistant",):
            error_message = "Despite our efforts, we'd managed to find the edge of the Internet.  \nA program error had occured and it had prevented me from completing a task.  \nPlease try again."
            st.session_state.messages.append({"role":"assistant","content": error_message})             
            st.write(error_message)
            with st.expander("Show/Hide Error",expanded=False):    
                st.write(st.write(e), unsafe_allow_html=True)
