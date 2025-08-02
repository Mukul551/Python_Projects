from flask import Flask, request, jsonify
from search import search
from filter import Filter
from storage import DBStorage
import html

app = Flask(__name__)

styles = """
<style>
    body{
        background-image:url("https://i.gifer.com/embedded/download/ENjk.gif");
        background-size:cover;
        background-repeat:no-repeat;
        # background-attachement:fixed;
        margin:0;
        padding:0;
        font-family: Arial, sans-serif;
        color: #333;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;       
    }

    h1{
        color:white;
        text-align:center;
        color: #fff;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px #000;   
    }

        form {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 500px;
        padding: 20px;
        background-color: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    input[type="text"] {
        width: 100%;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        font-size: 1rem;
    }

    input[type="submit"] {
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        background-color: #007BFF;
        color: #fff;
        font-size: 1rem;
        cursor: pointer;
    }

    input[type="submit"]:hover {
        background-color: #0056b3;
    }


    .site {
        font-size: .8rem;
        color: green;
    }
    
    .snippet {
        font-size: .9rem;
        color: gray;
        margin-bottom: 30px;
    }
    
    .rel-button {
        cursor: pointer;
        color: blue;
    }

    @media (max-width: 600px) {
        h1 {
            font-size: 1.5rem;
        }
        form {
            padding: 10px;
        }
        input[type="text"], input[type="submit"] {
            font-size: 0.9rem;
        }
    }
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           "query": query,
           "link": link
          })
        });
}
</script>
"""

search_template = styles + """
    <h1>Virtuosa - An AI Powered Search Engine</h1>
    <form action="/" method="post">
        <input type="text" name="query">
        <input type="submit" value="Search">
    </form> 
    """

result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""

def show_search_form():
    return search_template

def run_search(query):
    results = search(query)
    fi = Filter(results)
    filtered = fi.filter(query)
    rendered = search_template
    filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
    for index, row in filtered.iterrows():
        rendered += result_template.format(**row)
    return rendered

@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()

@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query, link, 10)

    storage.query_results(query)
    result = storage.query_results(query)
    result["relevance"] += 1  # Increase relevance based on user feedback
    result.apply(lambda x: storage.update_relevance(x['query'], x['link'], x['relevance']), axis=1)

    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)