import urllib.request
import json

class FusionClient:
    def __init__(self, endpoint="http://127.0.0.1:27182/mcp"):
        self.endpoint = endpoint
        self.session_id = None
        self._init_session()

    def _init_session(self):
        init_req = urllib.request.Request(
            self.endpoint,
            data=json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "antigravity", "version": "1.0"}
                }
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(init_req, timeout=10) as resp:
            self.session_id = resp.headers.get("Mcp-Session-Id")

        notif_req = urllib.request.Request(
            self.endpoint,
            data=json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }).encode("utf-8"),
            headers={"Content-Type": "application/json", "Mcp-Session-Id": self.session_id}
        )
        try:
            with urllib.request.urlopen(notif_req, timeout=10) as _:
                pass
        except Exception:
            pass

    def call_tool(self, name, arguments):
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": arguments
                }
            }).encode("utf-8"),
            headers={"Content-Type": "application/json", "Mcp-Session-Id": self.session_id}
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))

    def run_script(self, script_code: str, read_only: bool = False):
        res = self.call_tool("fusion_mcp_execute", {
            "featureType": "script",
            "object": {
                "script": script_code,
                "readOnly": read_only
            }
        })
        return res

if __name__ == "__main__":
    client = FusionClient()
    res = client.run_script("""
import adsk.core, adsk.fusion

def run(_context: str):
    app = adsk.core.Application.get()
    print('Fusion version:', app.version)
""", read_only=True)
    print(res)
