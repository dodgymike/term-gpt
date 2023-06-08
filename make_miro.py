import requests
import json
import os
import re

import openai

import argparse

import time

data_filename="data.json"
config_filename="config.json"

def save_data(data, filename=data_filename):
    with open(filename, 'w') as f:
        json.dump(data, f) 

def load_data(filename=data_filename):
    with open(filename, 'r') as f:
        return json.load(f) 

if not os.path.isfile(config_filename):
    save_data({}, config_filename)

config=load_data(config_filename)
config_required=False

if "access_token" not in config:
    config_required=True

parser = argparse.ArgumentParser()

parser.add_argument('--access_token', required=config_required, help='Access token for authentication.')
parser.add_argument('--board_id', required=config_required, help='Board ID.')
parser.add_argument('--gpt_key', required=config_required, help='GPT key for AI processing.')
parser.add_argument('--data_filename', required=config_required, help='Data file name.')

args = parser.parse_args()

if args.access_token is not None:
    config["access_token"] = args.access_token
if args.gpt_key is not None:
    config["gpt_key"] = args.gpt_key
if args.data_filename is not None:
    config["data_filename"] = args.data_filename
if args.board_id is not None:
    config["board_id"] = args.board_id

save_data(config, "config.json")

# Replace these with your actual values
access_token = config["access_token"]
board_id = config["board_id"]
data_filename = config["data_filename"] #'data.json'

openai.api_key = config["gpt_key"]
# print(openai.api_key)

# exit()

ANSI_TO_MARKDOWN = {
    '\033[0m': '',        # Reset
    # '\033[1m': '**',      # Bold
    # '\033[4m': '__',      # Underline
    # '\033[31m': '<color=#FF0000>',     # Red
    # '\033[32m': '<color=#00FF00>',     # Green
    # '\033[33m': '<color=#FFFF00>',     # Yellow
    # '\033[34m': '<color=#0000FF>',     # Blue
    # '\033[35m': '<color=#FF00FF>',     # Magenta
    # '\033[36m': '<color=#00FFFF>',     # Cyan
    # '\033[37m': '<color=#FFFFFF>',     # White
}

def remove_ansi_control_codes(text):
    return re.sub(r'\x1B[@-_][0-?]*[ -/]*[@-~]', ' ', text)

def terminal_to_markdown(text):
    for ansi, markdown in ANSI_TO_MARKDOWN.items():
        text = text.replace(ansi, markdown)

    text = text.replace("\n", "<br>\n")
    # return text
    return remove_ansi_control_codes(text)
    
def ask_gpt(question):
    print("::::::::::::::::::::")
    print(question)
    print("::::::::::::::::::::")

    result = "B0rk"
    try:
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}])
        print("------------")
        print(chat_completion)
        print("------------")

        result = chat_completion.choices[0].message.content
    except Exception as e:
        print("*********")
        print(e)
        print(json.dumps(e))
        print("*********")
        time.sleep(2)
        try:
            chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}])
            print("@@@@@@@@@@@@@@@@@@@@@")
            print(chat_completion)
            print("@@@@@@@@@@@@@@@@@@@@@")

            result = chat_completion.choices[0].message.content
        except Exception as e:
            print(e)
            print("b0rk")
            # result = "{}"
    
    print("////////////////////////")
    print(result)
    print("////////////////////////")

    return result

def connect_widgets(board_id, a, b):
    miro_data = {
        "startItem": { "id": a},
        "endItem": { "id": b},
    }
    return requests.post(
        f'https://api.miro.com/v2/boards/{board_id}/connectors',
        headers=headers,
        data=json.dumps(miro_data),
    )

def update_text_widget(board_id, item_id, text):
    text = text[:1500]

    miro_data = {
        'data': {
            'content': text,
        },
    }

    response = requests.patch(
        f'https://api.miro.com/v2/boards/{board_id}/texts/{item_id}',
        headers=headers,
        data=json.dumps(miro_data),
    )

    response_json = response.json()
    print("====================")
    print(response_json)
    print(response_json['id'])
    print("====================")

    return response_json['id']

def make_text_widget(board_id, parent_id, text, width, x, y, font_size = 16):
    text = text[:1500]

    miro_data = {
        'data': {
            'content': text,
        },
        "position": {
            'x': x + 50,
            'y': y,
        },
        "geometry": {
            "width": width,
        },
        'style': {
            'fontSize': font_size,
            'fontFamily': 'Arial',
            'textAlign': 'left',
        },
        "parent": {
            "id": parent_id,
        }
    }

    response = requests.post(
        f'https://api.miro.com/v2/boards/{board_id}/texts',
        headers=headers,
        data=json.dumps(miro_data),
    )

    print("!!!!!!!!!!!!!!!!!!!!")
    print(text)
    print("====================")
    print(response.text)
    print("^^^^^^^^^^^^^^^^^^^^")
    response_json = response.json()
    print(response_json)
    print(response_json['id'])
    print("====================")

    return (response_json['id'], x + width + 50, width)

def get_item_geometry(board_id, item_id):
    response = requests.post(
        f'https://api.miro.com/v2/boards/{board_id}/items/{item_id}',
        headers=headers,
        data=json.dumps(miro_data),
    )

    return (response.json()['geometry'])

def create_frame(board_id, title, x, y, width=1200, height=4000):
    miro_data = {
        'data': {
            'title': title,
        },
        "position": {
            'x': x,
            'y': y,
        },
        "geometry": {
            "width": width,
            "height": height,
        },
        # 'style': {
        #     'fontSize': font_size,
        #     'fontFamily': 'Arial',
        #     'textAlign': 'left',
        # }
    }

    print(miro_data)

    response = requests.post(
        f'https://api.miro.com/v2/boards/{board_id}/frames',
        headers=headers,
        data=json.dumps(miro_data),
    )

    print("#############")
    print(response)
    print("#############")

    return response.json()['id']


def create_host_sticky(board_id, parent_id, text, x, y):
    # if parent_id is not None:
    #     parent_id = int(parent_id)
    
    miro_data = {
        'data': {
            'content': text,
        },
        # "position": {
        #     'x': x,
        #     'y': y,
        # },
        # "geometry": {
        #     "width": width,
        # },
        # 'style': {
        #     'fontSize': font_size,
        #     'fontFamily': 'Arial',
        #     'textAlign': 'left',
        # }
        "parent": {
            "id": parent_id,
        }
    }

    print(miro_data)

    response = requests.post(
        f'https://api.miro.com/v2/boards/{board_id}/sticky_notes',
        headers=headers,
        data=json.dumps(miro_data),
    )

    print("#############")
    print(response)
    print("#############")

    return response.json()['id']

# ask_gpt("wtf")
# exit(-1)

if not os.path.isfile(data_filename):
    save_data({})

data = load_data()

data['command_x'] = data['command_x'] if 'command_x' in data else 100
data['command_y'] = data['command_y'] if 'command_y' in data else 100
data['command_widget_id'] = data['command_widget_id'] if 'command_widget_id' in data else None
data['command_widget_text'] = data['command_widget_text'] if 'command_widget_text' in data else 'Hello world'

data['result_x'] = data['result_x'] if 'result_x' in data else 100
data['result_y'] = data['result_y'] if 'result_y' in data else 100

data['gpt_x'] = data['gpt_x'] if 'gpt_x' in data else 100
data['gpt_y'] = data['gpt_y'] if 'gpt_y' in data else 100

font_size = 16

headers = {
    'Authorization': 'Bearer ' + access_token,
    'Content-Type': 'application/json',
}

if "command_frame_widget_id" not in data:
    data["command_frame_widget_id"] = create_frame(board_id, "Commands", 1000, 0, 4000)
    save_data(data)

with open('hax.fifo') as fifo:
    current_line = ""
    while True:
        current_char = "-"
        while current_char and current_char != '%':
            current_char = fifo.read(1)
            current_line += current_char
            current_char = remove_ansi_control_codes(current_char)
            # print(current_char)
            # print(current_char == '%')
            if current_char == '%':
                # print("-------")
                break

        current_line_clean = terminal_to_markdown(current_line)

        if 'mrdavis@MRs-MacBook-Pro' not in current_line_clean:
            # print(current_line_clean)

            # lines.append(current_line_clean)
            continue

        current_line = ""

        current_line_clean = current_line_clean.replace('mrdavis@MRs-MacBook-Pro', '')
        current_line_clean = current_line_clean.replace('%', '')

        (current_line_clean, dummy) = current_line_clean.split('ile://MRs-MacBook-Pro.local/Users/mrdavis/source/term-gpt', 1)
        # current_line_clean = current_line_clean.replace('ile://MRs-MacBook-Pro.local/Users/mrdavis/source/term-gpt','')

        # miro_content = "<br>\n".join(lines)
        # lines = [ current_line_clean ]

        (command, result) = current_line_clean.split('\n', 1)

        if "command_frame_widget_id" not in data:
            data["command_frame_widget_id"] = create_frame(board_id, "Commands", 1000, 0, 4000)
            save_data(data)

        while True:
            try:
                gpt_thoughts = ask_gpt("""
When I issue this command in the terminal, I get the following result. Provide details about the command and the result, in the answer format. Add any interesting or unusual findings.
Command:
ls -l
Result:
total 48
-rw-r--r--  1 mrdavis  staff    202 Jun  3 10:57 config.json
-rw-r--r--@ 1 mrdavis  staff   2901 Jun  3 11:07 data.json
prw-r--r--  1 mrdavis  staff      0 Jun  3 11:10 hax.fifo
-rw-r--r--@ 1 mrdavis  staff  13229 Jun  3 11:12 make_miro.py

Answer format:
{
"command": "ls",
"arguments": ["-l"],
"command_purpose_tldr": "list files",
"result_tldr": "the directory contains 4 files",
"interesting_findings": "One file 'hax.fifo' is unusual because it is a named pipe"
}
""" + f"""
Command:
{command}
Result:
{result}
""")
    
                gpt_thoughts = gpt_thoughts.replace('Answer format:', '')
                gpt_info = None
                gpt_info = json.loads(gpt_thoughts)
                break
            except Exception as e:
                print(e)
                time.sleep(1)

        while True:
            try:
                gpt_host_thoughts = ask_gpt("""
Answer format:
{
"host": "bob.com",
"ip_address": "1.2.3.4",
"username": "unknown",
"further_information": "Some information about the host"
}

Answer format when no information can be found:
{}
""" + f"""
Respond in JSON format only. When I issue the command '{command}' on a mac in the terminal, I get the following result. What host or ip address is involved, along with any information about that host or ip address?
        {result}
""")

                gpt_host_thoughts = gpt_host_thoughts.replace('Answer format:', '')

                gpt_host_info = None
                gpt_host_info = json.loads(gpt_host_thoughts)
                break
            except Exception as e:
                print(e)
                time.sleep(1)
        
        if "host" in gpt_host_info:
            hostname = gpt_host_info["host"]
            ip_address = gpt_host_info["ip_address"]
            further_information = gpt_host_info["further_information"]

            if "hosts" not in data:
                data["hosts"] = {}
            if hostname not in data["hosts"]:
                data["hosts"][hostname] = { "information": [] }

                data["hosts"][hostname]["frame_id"] = create_frame(board_id, hostname, 0, 0)
                save_data(data)

                hostname_sticky_id = create_host_sticky(board_id, data["hosts"][hostname]["frame_id"], hostname, 0, 0)

            create_host_sticky(board_id, data["hosts"][hostname]["frame_id"], f"{gpt_info['command']}: {further_information}", 0, 0)
            create_host_sticky(board_id, data["hosts"][hostname]["frame_id"], f"{gpt_info['command']}: {gpt_info['result_tldr']}", 0, 0)
            create_host_sticky(board_id, data["hosts"][hostname]["frame_id"], f"{gpt_info['command']}: {gpt_info['interesting_findings']}", 0, 0)

            if ip_address is not None and len(ip_address) > 0 and "ip_address" not in data["hosts"][hostname]:
                data["hosts"][hostname]["ip_address"] = ip_address

                create_host_sticky(board_id, data["hosts"][hostname]["frame_id"], data["hosts"][hostname]["ip_address"], 0, 0)
            elif "ip_address" not in data["hosts"][hostname]:
                data["hosts"][hostname]["ip_address"] = "Unknown"
            
            data["hosts"][hostname]["hostname"] = hostname
            data["hosts"][hostname]["information"].append(further_information)
            data["hosts"][hostname]["information"].append(gpt_info['result_tldr'])
            data["hosts"][hostname]["information"].append(gpt_info['interesting_findings'])
            data["hosts"][hostname]["information"].append(data["hosts"][hostname]["ip_address"])

            if "host_summary_widget_id" not in data["hosts"][hostname]:
                (data["hosts"][hostname]["host_summary_widget_id"], xx, yy) = make_text_widget(board_id, data["hosts"][hostname]["frame_id"], "Summarisation starting", 500, data['command_x'], data['gpt_y'], font_size)

            context = "\n- ".join(data["hosts"][hostname]["information"])

            gpt_host_summary = None
            while True:
                try:
                    gpt_host_summary = ask_gpt(f"""
Summarise the following information about a computer system with hostname '{hostname}':
- {context} {hostname}
    """)


                    break
                except Exception as e:
                    print(e)
                    time.sleep(1)

            update_text_widget(board_id, data["hosts"][hostname]["host_summary_widget_id"], gpt_host_summary)

        gpt_host_thoughts = gpt_host_thoughts.replace(' .', ' .\n')
        gpt_host_thoughts = gpt_host_thoughts.replace('. ', '. \n')

        result_newline_count = result.count("\n")
        gpt_newline_count = gpt_thoughts.count("\n")
        gpt_host_newline_count = gpt_host_thoughts.count("\n")

        miro_content_left = command
        miro_content_right = result
        miro_content_gpt_thoughts = gpt_thoughts
        miro_content_gpt_host_thoughts = gpt_host_thoughts

        print('/////////')
        print(miro_content_left)
        print('/////////')
        print(miro_content_right)
        print('/////////')
        print(miro_content_gpt_thoughts)
        print('/////////')
        print(miro_content_gpt_host_thoughts)
        print('/////////')

        miro_content_left = f'<p>{miro_content_left}</p>'
        miro_content_right = f'<p>{miro_content_right}</p>'
        miro_content_gpt_thoughts = f'<p>{miro_content_gpt_thoughts}</p>'
        miro_content_gpt_host_thoughts = f'<p>{miro_content_gpt_host_thoughts}</p>'

        if len(miro_content_left) <= 0 or miro_content_left == '':
            continue

        (left_widget_id, left_widget_x, left_widget_width) = make_text_widget(board_id, data["command_frame_widget_id"], miro_content_left, 500, data['command_x'], data['gpt_y'], font_size)
        (gpt_widget_id, gpt_widget_x, gpt_widget_width) = make_text_widget(board_id, data["command_frame_widget_id"], miro_content_gpt_thoughts, 1000, left_widget_x + (1000/2), data['gpt_y'], font_size)
        (gpt_2_widget_id, gpt_2_widget_x, right_2_widget_width) = make_text_widget(board_id, data["command_frame_widget_id"], miro_content_gpt_host_thoughts, 250, gpt_widget_x + (250/2), data['gpt_y'], font_size)
        (right_widget_id, right_widget_x, right_widget_width) = make_text_widget(board_id, data["command_frame_widget_id"], miro_content_right, 1500, gpt_2_widget_x + (1500/2), data['gpt_y'], font_size)

        connect_widgets(board_id, left_widget_id, gpt_widget_id)
        connect_widgets(board_id, gpt_widget_id, gpt_2_widget_id)
        connect_widgets(board_id, gpt_2_widget_id, right_widget_id)

        # data['command_y'] += font_size + 2

        # data['result_y'] += result_newline_count * (font_size + 4)

        data['gpt_y'] += max([gpt_newline_count, result_newline_count]) * (font_size + 4)

        save_data(data)
