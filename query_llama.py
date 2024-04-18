import sys
import http.client
import json

hostname = "celadon.wellesley.edu"
port = 7999
url = "/api/predict"

def completion_query(prompt,max_tokens=10,temperature=0.95,samples=1):
    input_json = {"data": [prompt, max_tokens, temperature,samples]}
    args =  [prompt, max_tokens, temperature,samples]
    words = "null"
    body = json.dumps({"data": ["Completions", prompt, max_tokens, temperature, samples, words]})
    headers = {"Content-Type": "application/json"}
    conn = http.client.HTTPConnection(hostname, port)
    conn.request("POST", url, body, headers)
    res = conn.getresponse()
    result = json.loads(res.read())
    conn.close()
    completion = result['data'][0]
    return completion

def word_query(prompt,wordlist):
    w = wordlist.split(';')
    words = '\n'.join(w)
    temperature = 0.95
    samples = 1
    max_tokens = 10
    body = json.dumps({"data": ["Words", prompt, max_tokens, temperature, samples, words]})
    headers = {"Content-Type": "application/json"}
    conn = http.client.HTTPConnection(hostname, port)
    conn.request("POST", url, body, headers)
    res = conn.getresponse()
    result = json.loads(res.read())
    conn.close()
    probs = result['data'][0].strip('[').strip(']').split(',')
    return {w[i]:float(p) for i,p in enumerate(probs)}

def token_query(prompt,samples):
    words = 'null'
    temperature = 0.95
    max_tokens = 10
    body = json.dumps({"data": ["Tokens", prompt, max_tokens, temperature, samples, words]})
    headers = {"Content-Type": "application/json"}
    conn = http.client.HTTPConnection(hostname, port)
    conn.request("POST", url, body, headers)
    res = conn.getresponse()
    result = json.loads(res.read())
    conn.close()
    result = result["data"][0]
    return dict(eval(result))

def main():
    if len(sys.argv) < 3:
        print("Usage: python query_llama.py mode input")
        return
    mode = sys.argv[1]
    if mode == "completions":
        result = completion_query(sys.argv[2])
        print(result)
        return result
    elif mode == "words":
        prompt = sys.argv[2]
        if len(sys.argv) < 4:
            print("Usage: python query_llama.py words prompt wordlist\nWords in word list should be separated by semi-colons.")
            return
        words = sys.argv[3]
        result = word_query(prompt,words)
        print(result)
        return result
    elif mode == "tokens":
        prompt = sys.argv[2]
        if len(sys.argv) < 4:
            print("Usage: python query_llama.py tokens prompt top_n\ntop_n should be an integer")
            return
        samples = int(sys.argv[3])
        result = token_query(prompt,samples)
        print(result)
        return result
    else:
        print("Unrecognized query mode.")
        return

if __name__ == "__main__":
    main()
