@target typescript

system AdapterSim {
    machine:
        $Start {
            $>() {
                // Simulate adapter handshake: initialize then continue
                console.log(JSON.stringify({ type: "command", action: "initialize", data: { stopOnEntry: false } }));
                console.log(JSON.stringify({ type: "command", action: "continue" }));
            }
        }
}
