import requests
import argparse

global host
host = "http://192.168.0.241:5000"


def terminate(key):
    r = requests.post(host+'/terminate_session',
                      json={'_key': key})
    if r.status_code != 200:
        print('Server not avaliable.')
    else:
        print(f"User session disconnected:{key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remote Desktop')
    parser.add_argument('key', help='serverkey', type=str)
    args = parser.parse_args()
    terminate(args.key)
