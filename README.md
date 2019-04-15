## Todo list:
* Implement rich text editor

title = request.form['title']
    categories = request.form['categories']
    if categories == '':
        categories = 'Uncategorised'
    else:
        categories = categories.replace(' ,', ',')
        categories = categories.replace(', ', ',')
    text = request.form['text']
    summary = request.form['summary']
    if summary == '':
        if text.find('\r\n') != -1:
            summary = text[:text.find('\r\n')]
        else:
            summary = text
    with sql.connect('databases/posts.db') as conn:
        cur = conn.cursor()
        results = cur.execute('UPDATE posts SET text=?, categories=?, summary=? WHERE title==?;', (text, categories, summary, title))
        conn.commit()
