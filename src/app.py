import streamlit as st
import requests

def fetch_bedrock_response(prompt):
    try:
        headers = {
            "x-api-key": "koStY9EEHaaLwi2mL7FvW9xO3q9xnoaS9HTjzMup",#settings.API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(
            url="https://dsb1qxkgnj.execute-api.ap-southeast-1.amazonaws.com/dev/chat/",#settings.API_URL,
            json={"prompt":prompt},
            headers=headers
        )
        print(response.json())
        return response
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

# ---- STATE (PERSIST CHAT) ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- RETRIEVE + GENERATE ----
def chat_with_kb(user_input):
    # Build conversation context (last 10 turns)
    context = ""
    for msg in st.session_state.chat_history[-10:]:
        context += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context += f"User: {user_input}\n"

    raw = fetch_bedrock_response(context)
    answer = "No response received from Bedrock API. You may rephrase your prompt or restart a new session."
    sql_query = ""
    if raw.status_code == 200:
        raw_json = raw.json()

        # Extract answer
        response = raw_json["response"]
        answer = response["output"]["text"]

        # Extract SQL query from citations
        citation = response["citations"]
        location = citation[0].get("retrievedReferences", [])[0].get("location", {})
        sql_query = location.get("sqlLocation", "").get("query", "")

    # Save to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": answer, "corresponding_query": sql_query})

# ---- UI ----
st.title("💬 SMO AI Chat")
st.markdown("Powered by Amazon Bedrock. Ask questions related to SMO Marketing and Parking.")

if st.button("🔁 Restart session", key="reset"):
    st.session_state.clear()
    st.rerun()

# Display chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        if msg.get("corresponding_query"):
            with st.expander("🛢️ Corresponding Query"):
                st.caption(f"{msg["corresponding_query"]}")

# Chat input
if user_input := st.chat_input("Type your question..."):
    chat_with_kb(user_input)
    st.rerun()
