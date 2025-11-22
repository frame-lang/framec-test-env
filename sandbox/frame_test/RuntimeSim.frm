@target python

system RuntimeSim {
    machine:
        $Start {
            $>() {
                # Simulate runtime handshake: connected → ready → terminated
                import json
                print(json.dumps({ "type": "event", "event": "connected" }))
                print(json.dumps({ "type": "event", "event": "ready" }))
                print(json.dumps({ "type": "event", "event": "terminated", "data": { "exitCode": 0 } }))
            }
        }
}
