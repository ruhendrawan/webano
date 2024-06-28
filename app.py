import json
import os
import streamlit as st
import requests
import sqlite3
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_core.output_parsers import JsonOutputParser

# Set up OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize LangChain OpenAI model
llm = OpenAI()

# Database setup
conn = sqlite3.connect('content.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY,
        url TEXT,
        full_text TEXT,
        summary TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS labels (
        id INTEGER PRIMARY KEY,
        content_id INTEGER,
        label_type TEXT,
        labels TEXT,
        gpt_response TEXT,
        FOREIGN KEY(content_id) REFERENCES content(id)
    )
''')

conn.commit()

def fetch_content(url):
    response = requests.get(f"https://r.jina.ai/{url}")
    return response.text

def generate_summary(content):
    summarize_chain = load_summarize_chain(llm, chain_type="map_reduce")
    return summarize_chain.run(content)

def extract_labels(the_text):
    prompt_template = PromptTemplate(
        template="Evaluate the content section of markdown text below. Ignore title and navigation. For each line, generate immediate and specific prerequisite concepts, which are not being discussed, that novice computer science student must understand before reading, as potential labels. Return JSON {{[line, labels:[{{phrase_in_text, prerequisite_concepts[concept, ]}}, ], ]}}:\n\n---\n\n{the_text}",
        input_variables=["the_text"],
    )
    model = ChatOpenAI(model="gpt-3.5-turbo")
    chain = prompt_template | model
    response = chain.invoke(
        {"messages": [], "the_text": the_text}
    )
    return response.content

def save_content_to_db(url, full_text, summary):
    c.execute("INSERT INTO content (url, full_text, summary) VALUES (?, ?, ?)",
              (url, full_text, summary))
    conn.commit()
    return c.lastrowid

def save_labels_to_db(content_id, label_type, labels, gpt_response):
    c.execute("INSERT INTO labels (content_id, label_type, labels, gpt_response) VALUES (?, ?, ?, ?)",
              (content_id, label_type, json.dumps(labels), gpt_response))
    conn.commit()

def dict_merge(a: dict, b: dict, path=[]):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                raise Exception('Conflict at ' + '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


# Streamlit UI
st.title('GPT Web Annotator')

# Page Selection
# st.page_link("app.py", label="Home", icon="🏠")
# st.page_link("pages/1_fetch.py", label="Page 1", icon="1️⃣")
# st.page_link("pages/2_gen.py", label="Page 2", icon="2️⃣")
# st.page_link("pages/3_display.py", label="Page 3", icon="3️⃣")

page = st.sidebar.selectbox("Choose a page", ["Fetch Content", "Generate More Labels", "Display Content"])

if page == "Fetch Content":
    st.header('Fetch new content from a URL')

    url_input_default = "https://nlp.stanford.edu/IR-book/html/htmledition/boolean-retrieval-1.html"
    url_input = st.text_input("Enter the URL to fetch content:", placeholder=url_input_default)

    if st.button("Fetch Content from Url ", type="primary"):

        if url_input:
            full_text = fetch_content(url_input)
            st.text_area("Fetched Content", full_text, height=200)

            summary = ""
            # with st.spinner(text="Generating summary..."):
            #     summary = generate_summary(full_text)
            #     st.text_area("Generated Summary", summary, height=200)

            with st.spinner(text="Extracting labels..."):
                gpt_response = extract_labels(full_text)
                st.text_area("GPT Response", gpt_response, height=200)

                try:
                    parser = JsonOutputParser()
                    gpt_labels = parser.parse(gpt_response)
                    st.json(gpt_labels)
                except ValueError as e:
                    gpt_labels = []
                    st.error("Error parsing GPT response as JSON.")

                content_id = save_content_to_db(url_input, full_text, summary)
                save_labels_to_db(content_id, "GPT", gpt_labels, gpt_response)
                st.success("Data saved to the database!")

elif page == "Generate More Labels":
    st.header("Generate More Labels")

    c.execute("SELECT id, url FROM content")
    contents = c.fetchall()
    content_options = {f"{content[1]} (ID: {content[0]})": content[0] for content in contents}
    content_choice = st.selectbox("Select Content to Generate", list(content_options.keys()))

    if st.button("Generate Labels", type="primary"):

        if content_choice:
            content_id = content_options[content_choice]
            c.execute("SELECT full_text FROM content WHERE id = ?", (content_id,))
            row = c.fetchone()
            if row:
                full_text = row[0]
                with st.spinner(text="Extracting labels..."):
                    gpt_response = extract_labels(full_text)
                    st.text_area("GPT Response", gpt_response, height=200)

                    try:
                        parser = JsonOutputParser()
                        gpt_labels = parser.parse(gpt_response)
                        st.json(gpt_labels)
                    except ValueError as e:
                        gpt_labels = []
                        st.error("Error parsing GPT response as JSON.")

                    save_labels_to_db(content_id, "GPT", gpt_labels, gpt_response)
                    st.success("Data saved to the database!")


elif page == "Display Content":
    st.header("Display Content and Labels")

    c.execute("SELECT id, url FROM content")
    contents = c.fetchall()
    content_options = {f"{content[1]} (ID: {content[0]})": content[0] for content in contents}
    content_choice = st.selectbox("Select Content to Display", list(content_options.keys()))

    if content_choice:
        content_id = content_options[content_choice]
        c.execute("SELECT full_text FROM content WHERE id = ?", (content_id,))
        row = c.fetchone()
        if row:
            full_text = row[0]
            st.text_area("Content", full_text, height=200)

            c.execute("SELECT id, label_type, labels FROM labels WHERE content_id = ?", (content_id,))
            label_rows = c.fetchall()
            label_dict = {}
            for label_row in label_rows:
                labelset_id, labelset_type, labelset_json = label_row
                labelset_data = json.loads(labelset_json)
                for rec_line in labelset_data:
                    for rec_label in rec_line['labels']:
                        phrase_in_text = rec_label['phrase_in_text']
                        phrase_in_text = phrase_in_text.strip("_")
                        if phrase_in_text not in label_dict:
                            label_dict[phrase_in_text] = {}
                        for concept in rec_label['prerequisite_concepts']:
                            if concept not in label_dict[phrase_in_text]:
                                label_dict[phrase_in_text][concept] = 1
                            else:
                                label_dict[phrase_in_text][concept] += 1
            st.text("Merged Labels:")
            st.json(label_dict)

            st.text("Labels generated:")
            for label in label_rows:
                label_dict = json.loads(label[2])
                st.json(label_dict, expanded=False)

conn.close()
