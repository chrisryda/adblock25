from mitmproxy.tools.main import mitmdump
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', dest='port', type=str, help='Port proxy binds to. Default is 8080.')
parser.add_argument('-a', dest='addon', type=str, help='Which addon mitmproxy laods. Default is addon.py.')
args = parser.parse_args()

port = args.port if args.port else "8080"
addon = args.addon if args.addon else "addon.py"

mitmdump(args=[
    "-s", f"{addon}",
    "-p", f"{port}"
])
