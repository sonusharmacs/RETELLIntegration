import os
import random
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage
from Sql import insert_claim, retrieve_claim, initialize_database, get_all_claims, delete_all_claims
from pypdf import PdfReader
from io import StringIO
from langchain_tavily import TavilySearch
import streamlit as st
os.environ["Anthropic_API_KEY"] = "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"
from langchain_groq import ChatGroq
llm = ChatGroq(model="qwen/qwen3.8-27b",api_key="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")
#llm = ChatAnthropic(model="claude-3.0", api_key=os.environ["Anthropic_API_KEY"])
os.environ["TAVILY_API_KEY"]="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"
initialize_database()
df_result = get_all_claims()
dl_result = delete_all_claims()

class State(TypedDict):
    messages: Annotated[list[AIMessage], add_messages]
    user_input: str
    message_type: str


class MessageClassifier(BaseModel):
    message_type: Literal["employee_info", "retrieve_Claim", "Create_Claim"] = Field(description="type of user input")

class ReadInvoicePDF(TypedDict):
    recieptname: str = Field(description="Receipt No")
    total: str = Field(description="total")
    rDate: str = Field(description="Issued")
    validreciept: bool = Field(description="Valid reciept if reciept date is present")

def tavily_tool_search():
    result = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
    )
    return result

def routerCall(state: State):
    """Route the query to the appropriate agent"""
    print("Router called with state:")
    user_input = state["user_input"]
    llm_with_schema = llm.with_structured_output(MessageClassifier)
    prompt = f'''From User input: {user_input}, classify  it according to below category
    employee_info: If user is asking for employee information
    retrieve_Claim: If user is asking for claim information 
    Create_Claim: If user is asking to create a claim
    '''
    response = llm_with_schema.invoke(prompt)
    print("Router called with response:", response)
    return {
        "messages": [AIMessage(content=response.message_type)],
        "message_type": response.message_type,
        "user_input": user_input,
    }


def retrieveEmployeeInfo(state: State):
    """Return employee information from Employee Directory"""
    print("RetrieveEmployeeInfo called with state:")
    employee_info = "Sonu Sharma, EMP1000 Software Engineer, San Francisco, CA"
    return {"messages": [AIMessage(content=employee_info)]}


def createClaim(state: State):
    """Create claim in claim system"""
    print("CreateClaim called with state:")
    claimnum = "CL" + str(random.randint(10000, 99999))
    insert_claim(claimnum, 'EMP1000', 100.0, "Pending")
    output = llm.invoke(f"Created a claim {claimnum} for the following user input: {state['user_input']}. Return the claim number with formatted output only.")
    print("CreateClaim called with state:", output.content)
    return {"messages": [AIMessage(content=output.content)]}


def retrieveClaim(state: State):
    """Retrieve claim information"""
    print("RetrieveClaim called with state:")
    claimnum = retrieve_claim('EMP1000')
    claim_text = str(claimnum) if claimnum else "No claims found"
    return {"messages": [AIMessage(content=claim_text)]}


def finalresponse(state: State):
    """Return final response to user"""
    print("FinalResponse called with state:", state['messages'])
    user_input = state["user_input"]
    prompt = f"""
    you are expert in building response with the given context below user input and context

    user input: {user_input}
    context: {state['messages']}"""
    final_output = llm.invoke(prompt)
    print("FinalResponse called with state:", final_output.content)
    return {"messages": [AIMessage(content=final_output.content)]}


def myclaim_call(user_input, uploaded_file):
    """Function to handle user input and uploaded file"""
    file_text = ""
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            file_text += " " + text
        elif uploaded_file.type == "text/plain":
            text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
            file_text += " " + text
            
    #llm.bind_tools([tavily_tool_search])
    llm_with_schema = llm.with_structured_output(ReadInvoicePDF)
    prompt=f"You are a helpful assistant, find out the reciept date, reciept number and total from {file_text} and update 'validreceipt' field accourdingly. if not found return 'validreceipt' as false and other fields as empty string. Return the output in JSON format only.",
    response = llm_with_schema.invoke(prompt)
    print("PdfExtract called with response:", response)
    user_input = user_input + " " + response.messages
    #print(user_input)
    #output = workflow.invoke({"user_input": user_input})
    #st.write(output["messages"][2].content)
    #st.write("Extracted text from file:")
    #st.write(file_text)
    st.write(response)

st.set_page_config(page_title="Claim Management System", page_icon=":guardsman:", layout="wide")
st.title("Claim Management System")
st.data_editor(df_result, use_container_width=True)
uploaded_file = st.file_uploader("Choose a file",type=["pdf", "txt"])
user_text = st.text_area(label="Enter your question:", max_chars=500)
st.button("Search", on_click=myclaim_call, args=(user_text,uploaded_file))



graph = StateGraph(State)
graph.add_node("retrieveEmployeeInfo", retrieveEmployeeInfo)
graph.add_node("retrieveClaim", retrieveClaim)
graph.add_node("createClaim", createClaim)
graph.add_node("Router", routerCall)
graph.add_node("FinalResponse", finalresponse)

graph.add_edge(START, "Router")
graph.add_conditional_edges(
    "Router",
    lambda state: state.get("message_type"),
    {
        "employee_info": "retrieveEmployeeInfo",
        "Create_Claim": "createClaim",
        "retrieve_Claim": "retrieveClaim",
    },
)
graph.add_edge("retrieveEmployeeInfo", "FinalResponse")
graph.add_edge("retrieveClaim", "FinalResponse")
graph.add_edge("createClaim", "FinalResponse")
graph.add_edge("FinalResponse", END)
workflow = graph.compile()

if __name__ == "__main__":
    output = workflow.invoke({"user_input": "I want to create a claim for my travel expenses."})
    print(output)