# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class SlaMonitor(gl.Contract):
    service_name: str
    sla_terms: str
    latest_packet: str
    breached: bool
    severity: str
    credit_bps: int
    reason: str

    def __init__(self, service_name: str, sla_terms: str):
        self.service_name = service_name
        self.sla_terms = sla_terms
        self.latest_packet = ""
        self.breached = False
        self.severity = "none"
        self.credit_bps = 0
        self.reason = "No incident submitted"

    @gl.public.view
    def verdict(self) -> str:
        return f"{self.severity}:{self.credit_bps}:{self.reason}"

    @gl.public.view
    def is_breached(self) -> bool:
        return self.breached

    @gl.public.write
    def submit_incident(self, packet_json: str) -> str:
        prompt = f"""
        You are a GenLayer validator for an SLA monitoring contract.

        Service:
        {self.service_name}

        SLA terms:
        {self.sla_terms}

        Incident packet JSON:
        {packet_json}

        Decide whether the packet proves an SLA breach.
        Return strict JSON:
        {{
          "breached": true or false,
          "severity": "none" or "minor" or "major" or "critical",
          "credit_bps": integer from 0 to 10000,
          "reason": "one short technical sentence"
        }}
        Use 0 credit_bps when breached is false.
        """

        def leader_fn():
            return gl.nondet.exec_prompt(prompt, response_format="json")

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            mine = leader_fn()
            credit_delta = abs(int(mine["credit_bps"]) - int(leaders_res.calldata["credit_bps"]))
            return mine["breached"] == leaders_res.calldata["breached"] and mine["severity"] == leaders_res.calldata["severity"] and credit_delta <= 250

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        credit = int(result["credit_bps"])
        if credit < 0 or credit > 10000:
            raise gl.vm.UserError("credit_bps out of range")

        self.latest_packet = packet_json
        self.breached = bool(result["breached"])
        self.severity = result["severity"]
        self.credit_bps = credit
        self.reason = result["reason"]
        return self.verdict()
