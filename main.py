from flask import Flask, request


FILENAME = 'data.jsonl'

app = Flask(__name__)

@app.route("/")
def hello():
    return "hello"


@app.route("/pub", methods=['POST'])
def pub():
    # print raw request data
    with open(FILENAME, 'ab') as f:
        f.write(request.data)
        f.write(b'\n')
    return "done"


if __name__ == '__main__':
    print("Starting server...")
    app.run(host='0.0.0.0')
