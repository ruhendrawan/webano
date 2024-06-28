def gen(st, c):
    st.header("Generate More Labels")

    c.execute("SELECT id, url FROM content")
    contents = c.fetchall()
    content_options = {f"{content[1]} (ID: {content[0]})": content[0] for content in contents}
    content_choice = st.selectbox("Select Content to Generate", list(content_options.keys()))

    if content_choice:
        content_id = content_options[content_choice]
        c.execute("SELECT full_text FROM content WHERE id = ?", (content_id,))
        row = c.fetchone()
        if row:
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
