"""Scenario simulator interface (foundation stub)."""
class ScenarioSimulator:
    def __init__(self, config=None):
        self.config = config or {}

    def status(self):
        return {"ready": False, "status": "not_implemented",
                "message": "Scenario simulation requires a validated and fitted causal model."}

    def run(self, scenario):
        raise NotImplementedError("Scenario simulation is not implemented in the foundation stage.")
