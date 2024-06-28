def fetch (st,):
    st.header('Fetch new content from a URL')

    url_input_default = "https://nlp.stanford.edu/IR-book/html/htmledition/boolean-retrieval-1.html"
    url_input = st.text_input("Enter the URL to fetch content:", placeholder=url_input_default)

    if url_input:
        full_text = fetch_content(url_input)
        st.text_area("Fetched Content", full_text, height=200)

        summary = ""
        # st.spinner(text="Generating summary...")
        # summary = generate_summary(full_text)
        # st.text_area("Generated Summary", summary, height=200)

        st.spinner(text="Extracting labels...")
        gpt_response = extract_labels(full_text)
        st.text_area("GPT Response", gpt_response, height=200)

        try:
            parser = JsonOutputParser()
            gpt_labels = parser.parse(gpt_response)
            st.json(gpt_labels)
        except ValueError as e:
            gpt_labels = []
            st.error("Error parsing GPT response as JSON.")

        content_id = save_content_to_db(url_input, full_text, summary, gpt_response)
        save_labels_to_db(content_id, "GPT", gpt_labels)
        st.success("Data saved to the database!")
