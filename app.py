import streamlit as st
import re
import requests
import os

st.set_page_config(page_title="Indian Legal Advisor", layout="centered")
st.title("Indian Legal Advisor")
st.markdown("Decribe your legal issue Below: ")
api_key = os.getenv("API_KEY", st.secrets.get("API_KEY","no-key-found"))
user_input = st.text_area("Enter your legal issue here: ", height=200)

def is_valid_input(text):
    return bool(re.search(r'[a-zA-Z]{3,}',text)) and len(text.strip().split())>3

def build_prompt(user_input):
    return f"""
You are a highly experienced Senior Legal Advisor specializing in Indian Law. 
A user has described their legal issue in plain natural language below.

Please analyze their situation carefully and provide a detailed response that includes the following points:

1. **Legal Domain**: Clearly identify the legal domain involved, such as criminal law, civil law, family law, labor law, cyber law, property law, etc.

2. **Relevant Indian Laws and Sections**: Mention all the applicable Indian Acts (like IPC, CrPC, IT Act, etc.) and the exact section numbers. Explain briefly what each section states and how it applies in this case.

3. **Bailable vs Non-Bailable**: Clarify whether the offense is bailable or non-bailable, and whether it is cognizable or non-cognizable. Explain both in simple terms.

4. **Punishments and Fines**: Describe the legal penalties, including imprisonment durations, fines, and any other consequences based on the applicable sections.

5. **Jurisdiction and Court Process**: Mention which court (e.g., Magistrate, District Court, Family Court, High Court) will likely hear this case and what legal procedure may follow.

6. **Advice and Next Steps**: Suggest clear steps the user can take next:
   - Should they file an FIR or complaint?
   - Consult a lawyer or legal aid service?
   - Gather evidence or documents?
   - Take any emergency action like filing for protection?

7. **Hindi Translation**: Provide a complete and easy-to-read Hindi version of the entire response.

Important:
- Use plain English and avoid legal jargon where possible.
- Make the Hindi translation simple and conversational.
- Be neutral and do not give false hope or promises.

User’s input:
\"\"\"{user_input}\"\"\"
"""
if st.button("Get the legal Advice"):
    if not user_input.strip():
        st.warning("Enter the discription of you legal issue")
    elif not is_valid_input(user_input):
        st.error("Please enter valid issue in clear format")
    else:
        with st.spinner("Generating the legal response"):
            prompt = build_prompt(user_input)
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization":f"Bearer {api_key}",
                    "Content-Type":"application/json"
                },
                json = {
                    "model":"openai/gpt-3.5-turbo",
                    "messages":[
                        {"role":"system","content":"You are helpful and honest legal advisor"},
                        {"role":"user","content":prompt}
                    ]
                }
            )
            try:
                result = response.json()
                if "choices" in result and result["choices"]:
                    output = result["choices"][0]["message"]["content"]
                    if "Hindi Translation" in output:
                        eng_part, hindi_part = output.split("Hindi Translation",1)
                        st.subheader("Legal Advice (English)")
                        st.markdown(eng_part.strip())
                        st.subheader("Legal Advice (Hindi)")
                        st.markdown(hindi_part.strip())
                    else:
                        st.markdown("Legal Advice")
                        st.write(output.strip())
                    with st.expander("Raw Expander",expanded=False):
                        st.json(result)
                elif "error" in result:
                    st.error("API Error"+result["error"].get("message","Unknown error"))
                else:
                    st.warning("Unexpected format")
                    st.json(result)
            except Exception as e:
                st.error(f"failed to parse:{str(e)}")