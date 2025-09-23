class Plugin:
    def __init__(self, brain, config):
        self.brain = brain
        self.config = config

    def run(self):
        # Scripted responses don't need a run loop
        print("[ScriptedResponses] Ready (responses will be pulled from memory).")
