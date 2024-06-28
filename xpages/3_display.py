def diplay(st, c):

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

            c.execute("SELECT label_type, labels FROM labels WHERE content_id = ?", (content_id,))
            labels = c.fetchall()
            label_dict = {label[0]: json.loads(label[1]) for label in labels}
            st.json(label_dict)
