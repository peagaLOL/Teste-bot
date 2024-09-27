from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# HTML básico com um botão
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Simples</title>
    <script>
        function startBot() {
            fetch('/start', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').innerText = data.message;
            });
        }
    </script>
</head>
<body>
    <h1>Bem-vindo ao Bot Simples!</h1>
    <button onclick="startBot()">Start</button>
    <p id="response"></p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['POST'])
def start():
    return jsonify({"message": "Olá!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
