@@target python

# Frame VS Code Debug Adapter State Machine
# Handles VS Code Debug Adapter Protocol (DAP) integration
# Transpiles to TypeScript with Node.js and VS Code APIs


@@system FrameDebugAdapter {
    
    interface:
        # VS Code DAP commands
        initialize(args)
        launch(args)
        setBreakpoints(source, lines)
        configurationDone()
        continueExecution(threadId)
        nextStep(threadId)
        stepInto(threadId)
        stepOutOf(threadId)
        pause(threadId)
        disconnect()
        terminate()
        restart()
        
        # VS Code integration
        setVSCodeSession(session)
        
        # Events from Python runtime
        onRuntimeConnected()
        onRuntimeReady()
        onRuntimeStopped(reason, threadId, text)
        onRuntimeOutput(output, category)
        onRuntimeTerminated(exitCode)
        onRuntimeError(message)
        
        # Socket event handlers
        onData(data)
        onClose()
        onError(error)
        
    machine:
        $Initializing {
            initialize(args) {
                self.sendDebugConsole("Frame System Designer v0.12.62 - Debug adapter initializing...")
                self.clientId = args.clientID
                self.adapterID = args.adapterID
                # Initialize transpiler
                self.initializeTranspiler()
                self.sendResponse("initialize", {
                    "supportsConfigurationDoneRequest": True,
                    "supportsSetVariable": False,
                    "supportsConditionalBreakpoints": True,
                    "supportsHitConditionalBreakpoints": True,
                    "supportsEvaluateForHovers": True,
                    "supportsLogPoints": False,
                    "supportsSetExpression": False
                })
                -> $Initialized
            }
            
            # Ignore other commands during initialization
            launch(args) {
                self.sendError("launch", "Adapter not initialized")
            }
        }
        
        $Initialized {
            launch(args) {
                self.sendDebugConsole(f"Launching Frame program: {args.program}")
                self.frameFile = args.program
                self.stopOnEntry = args.stopOnEntry
                # Try transpilation with error handling
                if not self.transpileProgram() {
                    self.sendError("launch", "Failed to transpile Frame program")
                    -> $Failed
                }
                if not self.startTcpServer() {
                    self.sendError("launch", "Failed to start debug server")
                    -> $Failed
                }

                if not self.spawnPythonRuntime() {
                    self.sendError("launch", "Failed to start Python runtime")
                    -> $Failed
                }
                -> $Connecting
            }
            
            setBreakpoints(source, lines) {
                # FDASM: Handle breakpoint business logic
                self.currentSource = source.path
                print(f"[BREAKPOINT PROTOCOL] 3. FDASM → Processing breakpoints for {source.path}")
                
                # Store breakpoints specifically for the target debugging file
                if self.frameFile and source.path == self.frameFile {
                    print(f"[FDASM] ✅ Target file breakpoints: {source.path} lines: {lines}")
                    self.targetFileBreakpoints = lines
                } else {
                    print(f"[FDASM] ⚠️  Ignoring breakpoints for non-target file: {source.path}")
                }
                
                # Store for later when runtime connects
                self.pendingBreakpoints = lines
                print(f"[BREAKPOINT PROTOCOL] 4. FDASM → Stored pending breakpoints: {lines}")
                
                # Return lines for FDA to format response
                return lines
            }
            
            disconnect() {
                -> $Disconnected
            }
        }
        
        $Connecting {
            $>() {
                self.sendDebugConsole("Waiting for Python runtime connection...")
                self.connectionTimeout = 10000  # 10 seconds
            }
            
            onRuntimeConnected() {
                self.sendDebugConsole("Python runtime connected successfully")
                self.sendInitializationData()
                -> $Configuring
            }
            
            onData(data) {
                # Parse and route messages from Python runtime directly
                try {
                    message = self.parseJson(data)
                    if message.type == "event" {
                        if message.event == "connected" {
                            self.onRuntimeConnected()
                        } elif message.event == "ready" {
                            self.onRuntimeReady()
                        } elif message.event == "stopped" {
                            self.onRuntimeStopped(
                                message.data.reason,
                                message.data.threadId,
                                message.data.text
                            )
                        } elif message.event == "output" {
                            self.onRuntimeOutput(
                                message.data.output,
                                message.data.category
                            )
                        } elif message.event == "terminated" {
                            self.onRuntimeTerminated(message.data.exitCode)
                        }
                    }
                } except Exception as e {
                    print(f"[FrameDebugAdapter] Failed to parse runtime message: {e}")
                }
            }
            
            onClose() {
                print("[FrameDebugAdapter] Runtime connection closed")
                self.socket = None
            }
            
            onError(error) {
                print(f"[FrameDebugAdapter] Runtime connection error: {error}")
            }
            
            onTimeout() {
                self.sendDebugConsole("Connection timeout - retrying...")
                self.retryCount = self.retryCount + 1
                if self.retryCount < 3 {
                    self.spawnPythonRuntime()
                    # Stay in Connecting
                } else {
                    self.sendEvent("terminated", {})
                    -> $Failed
                }
            }
            
            terminate() {
                self.sendTerminateCommand()
                -> $Terminating
            }
        }
        
        $Configuring {
            onRuntimeReady() {
                self.sendDebugConsole("Runtime ready - sending breakpoints")
                self.sendBreakpoints(self.pendingBreakpoints)
                if self.stopOnEntry {
                    -> $WaitingForEntry
                } else {
                    self.sendContinueCommand()
                    -> $Running
                }
            }
            
            configurationDone() {
                self.sendDebugConsole("Configuration done - coordinating with runtime")
                print(f"[FDASM] frameFile: {self.frameFile}")
                print(f"[FDASM] currentSource: {self.currentSource}")
                
                # FDASM: Send pending breakpoints to runtime for the debugging file
                if self.targetFileBreakpoints and len(self.targetFileBreakpoints) > 0 {
                    print(f"[FDASM] Sending breakpoints for target file: {self.frameFile}, lines: {self.targetFileBreakpoints}")
                    self.sendBreakpointsToRuntime(self.targetFileBreakpoints)
                } else {
                    print(f"[FDASM] No breakpoints for target file: {self.frameFile}")
                }
                
                # May receive this before or after runtime ready
                self.configurationComplete = True
            }
            
            onRuntimeError(message) {
                self.sendEvent("output", {
                    "output": f"Runtime error: {message}\n",
                    "category": "stderr"
                })
                -> $Failed
            }
            
            onData(data) {
                # Parse and route messages from Python runtime directly
                try {
                    message = self.parseJson(data)
                    if message.type == "event" {
                        if message.event == "connected" {
                            self.onRuntimeConnected()
                        } elif message.event == "ready" {
                            self.onRuntimeReady()
                        } elif message.event == "stopped" {
                            self.onRuntimeStopped(
                                message.data.reason,
                                message.data.threadId,
                                message.data.text
                            )
                        } elif message.event == "output" {
                            self.onRuntimeOutput(
                                message.data.output,
                                message.data.category
                            )
                        } elif message.event == "terminated" {
                            self.onRuntimeTerminated(message.data.exitCode)
                        }
                    }
                } except Exception as e {
                    print(f"[FrameDebugAdapter] Failed to parse runtime message: {e}")
                }
            }
            
            onClose() {
                print("[FrameDebugAdapter] Runtime connection closed")
                self.socket = None
            }
            
            onError(error) {
                print(f"[FrameDebugAdapter] Runtime connection error: {error}")
            }
        }
        
        $WaitingForEntry {
            onRuntimeStopped(reason, threadId, text) {
                if reason == "entry" {
                    self.sendDebugConsole("Stopped on entry as requested")
                    self.sendEvent("stopped", {
                        "reason": "entry",
                        "threadId": threadId,
                        "text": text
                    })
                    -> $Paused
                } else {
                    # Unexpected stop
                    self.handleUnexpectedStop(reason, threadId, text)
                    -> $Paused
                }
            }
            
            continueExecution(threadId) {
                # User wants to continue before we hit entry point
                self.queuedCommand = "continue"
            }
        }
        
        $Running {
            onRuntimeStopped(reason, threadId, text) {
                self.sendDebugConsole(f"Runtime stopped: {reason} at thread {threadId}")
                self.sendEvent("stopped", {
                    "reason": reason,
                    "threadId": threadId,
                    "text": text
                })
                -> $Paused
            }
            
            onRuntimeOutput(output, category) {
                self.sendEvent("output", {
                    "output": output,
                    "category": category
                })
                # Stay in Running
            }
            
            onRuntimeTerminated(exitCode) {
                self.sendDebugConsole(f"Program terminated with exit code: {exitCode}")
                self.sendEvent("terminated", {"exitCode": exitCode})
                -> $Terminated
            }
            
            setBreakpoints(source, lines) {
                # FDASM: Check if breakpoints are for current file
                if self.currentSource and source.path != self.currentSource {
                    print(f"[BREAKPOINT PROTOCOL] WARNING: Ignoring breakpoints for {source.path}, debugging {self.currentSource}")
                    return []  # Return empty for non-current files
                }
                
                print(f"[BREAKPOINT PROTOCOL] 3. FDASM → Coordinating with PRT for {source.path}")
                self.sendBreakpoints(lines)
                print(f"[BREAKPOINT PROTOCOL] 4. FDASM → Sent breakpoints to PRT: {lines}")
                
                # Return lines for FDA response formatting
                return lines
            }
            
            pause(threadId) {
                self.sendPauseCommand(threadId)
                # Runtime will send stopped event
            }
            
            # Can't step while running
            nextStep(threadId) {
                self.sendError("next", "Cannot step while running")
            }
            
            stepInto(threadId) {
                self.sendError("stepIn", "Cannot step while running")
            }
            
            terminate() {
                self.sendTerminateCommand()
                -> $Terminating
            }
            
            restart() {
                self.sendDebugConsole("Restart requested - terminating current session...")
                self.sendTerminateCommand()
                -> $Terminating
            }
        }
        
        $Paused {
            continueExecution(threadId) {
                self.sendDebugConsole("Continuing execution")
                self.sendContinueCommand()
                -> $Running
            }
            
            nextStep(threadId) {
                self.sendDebugConsole("Stepping over")
                self.sendStepCommand("next")
                -> $Stepping
            }
            
            stepInto(threadId) {
                self.sendDebugConsole("Stepping into")
                self.sendStepCommand("stepIn")
                -> $Stepping
            }
            
            stepOutOf(threadId) {
                self.sendDebugConsole("Stepping out")
                self.sendStepCommand("stepOut")
                -> $Stepping
            }
            
            setBreakpoints(source, lines) {
                # FDASM: Check if breakpoints are for current file
                if self.currentSource and source.path != self.currentSource {
                    print(f"[BREAKPOINT PROTOCOL] WARNING: Ignoring breakpoints for {source.path}, debugging {self.currentSource}")
                    return []  # Return empty for non-current files
                }
                
                print(f"[BREAKPOINT PROTOCOL] 3. FDASM → Coordinating with PRT (paused) for {source.path}")
                self.sendBreakpoints(lines)
                print(f"[BREAKPOINT PROTOCOL] 4. FDASM → Sent breakpoints to PRT: {lines}")
                
                # Return lines for FDA response formatting
                return lines
            }
            
            onRuntimeOutput(output, category) {
                # Can still receive buffered output while paused
                self.sendEvent("output", {
                    "output": output,
                    "category": category
                })
            }
            
            terminate() {
                self.sendTerminateCommand()
                -> $Terminating
            }
            
            restart() {
                self.sendDebugConsole("Restart requested - terminating current session...")
                self.sendTerminateCommand()
                -> $Terminating
            }
        }
        
        $Stepping {
            onRuntimeStopped(reason, threadId, text) {
                self.sendDebugConsole(f"Step completed: {reason}")
                self.sendEvent("stopped", {
                    "reason": reason,
                    "threadId": threadId,
                    "text": text
                })
                -> $Paused
            }
            
            onRuntimeOutput(output, category) {
                self.sendEvent("output", {
                    "output": output,
                    "category": category
                })
            }
            
            # Ignore additional step commands while stepping
            nextStep(threadId) {
                self.sendError("next", "Step operation in progress")
            }
            
            stepInto(threadId) {
                self.sendError("stepIn", "Step operation in progress")
            }
            
            terminate() {
                self.sendTerminateCommand()
                -> $Terminating
            }
            
            restart() {
                self.sendDebugConsole("Restart requested during step - terminating...")
                self.sendTerminateCommand()
                -> $Terminating
            }
        }
        
        $Terminating {
            $>() {
                self.sendDebugConsole("Terminating debug session...")
                self.terminationTimeout = 5000  # 5 seconds
            }
            
            onRuntimeTerminated(exitCode) {
                self.sendDebugConsole("Runtime terminated successfully")
                self.cleanup()
                -> $Terminated
            }
            
            onTimeout() {
                self.sendDebugConsole("Termination timeout - force killing")
                self.killPythonProcess()
                -> $Terminated
            }
        }
        
        $Terminated {
            $>() {
                self.sendDebugConsole("Debug session terminated")
                self.fullCleanup()  # Complete session reset including global state
                self.sendEvent("terminated", {})
            }
            
            # Ignore all commands when terminated
            continueExecution(threadId) {}
            nextStep(threadId) {}
            terminate() {}
            
            # Handle restart from terminated state
            restart() {
                self.sendDebugConsole("Restarting debug session...")
                -> $Restarting
            }
        }
        
        $Restarting {
            $>() {
                self.sendDebugConsole("Cleaning up previous session...")
                self.fullCleanup()  # Complete state reset
                # Automatically transition back to initialized state
                -> $Initializing
            }
            
            # Ignore all other commands during restart
            continueExecution(threadId) {}
            nextStep(threadId) {}
            terminate() {}
            setBreakpoints(source, lines) {}
        }
        
        $Failed {
            $>() {
                self.sendDebugConsole("Debug session failed")
                self.fullCleanup()  # Complete session reset including global state
                self.sendEvent("terminated", {"error": True})
            }
        }
        
        $Disconnected {
            $>() {
                self.sendDebugConsole("Debug adapter disconnected")
                self.fullCleanup()  # Complete session reset including global state
            }
        }
    
    actions:
        initializeTranspiler() {
            self.sendDebugConsole("Initializing Frame transpiler...")
            # Import transpiler utilities
            self.framec = self.createTranspiler()
            self.sendDebugConsole("Frame transpiler ready")
        }
        
        transpileProgram() {
            self.sendDebugConsole(f"Transpiling Frame file: {self.frameFile}")
            # Use embedded framec binary to transpile with source mapping
            result = self.framec.transpile(self.frameFile, "python_3", {
                "debug": True,
                "sourceMap": True
            })
            
            # Store Python code and source map for debugging
            if result.python {
                self.pythonCode = result.python
                self.sourceMap = result.sourceMap or {}
            } else {
                self.pythonCode = result
                self.sourceMap = {}
            }
            
            mappingCount = Object.keys(self.sourceMap).length
            self.sendDebugConsole(f"Transpilation complete: {self.pythonCode.length} chars, {mappingCount} mappings")
            return True
        }
        
        startTcpServer() {
            self.debugPort = self.createTcpServer()
            self.sendDebugConsole(f"Debug server listening on port {self.debugPort}")
        }
        
        spawnPythonRuntime() {
            try {
                self.sendDebugConsole(f"Starting Python runtime for {self.frameFile}")
                
                # Inject debug runtime code with source mapping
                self.debugCode = self.injectDebugRuntime(self.pythonCode, self.sourceMap)
                
                # Spawn Python process with debug code via stdin
                self.pythonProcess = self.spawn("python3", ["-"], {
                    "env": {"FRAME_DEBUG_PORT": str(self.debugPort)},
                    "stdio": ["pipe", "pipe", "pipe"]
                })
                
                # Set up process event handlers
                self.setupPythonProcessHandlers()
                
                # Send debug code to Python process via stdin
                self.pythonProcess.stdin.write(self.debugCode)
                self.pythonProcess.stdin.end()
                
                self.sendDebugConsole("Python runtime started - waiting for connection...")
                return True
                
            } except Exception as e {
                self.sendDebugConsole(f"Failed to spawn Python runtime: {e}")
                self.sendEvent("terminated", {"exitCode": 1, "error": True})
                return False
            }
        }
        
        setupPythonProcessHandlers() {
            # Handle Python stdout
            self.pythonProcess.stdout.on("data", self.handlePythonStdout)
            
            # Handle Python stderr - route to DEBUG CONSOLE
            self.pythonProcess.stderr.on("data", self.handlePythonStderr)
            
            # Handle process exit with proper error reporting
            self.pythonProcess.on("exit", self.handlePythonExit)
            
            # Handle process errors
            self.pythonProcess.on("error", self.handlePythonError)
        }
        
        handlePythonStdout(data) {
            # Log Python stdout (usually empty for debug runtime)
            print(f"[FrameDebugAdapter] Python stdout: {data}")
        }
        
        handlePythonStderr(data) {
            # Send Python errors to DEBUG CONSOLE with clear formatting
            errorMessage = f"Python Error: {data.strip()}"
            print(f"[FrameDebugAdapter] Python stderr: {data}")
            self.sendEvent("output", {"output": errorMessage, "category": "stderr"})
        }
        
        handlePythonExit(exitCode) {
            print(f"[FrameDebugAdapter] Python process exited with code {exitCode}")
            
            if exitCode != 0 {
                # Python process failed - show detailed error message
                errorMessage = f"""
❌ Frame debugger failed: Python process exited with code {exitCode}

This is likely due to Bug #38 in Frame transpiler v0.81.3:
- String concatenation with escape sequences generates invalid Python
- See: https://github.com/frame-lang/frame_transpiler/issues/38

The Frame debugger cannot function until this transpiler bug is fixed.
"""
                self.sendEvent("output", {"output": errorMessage, "category": "stderr"})
            }
            
            # Always send terminated event
            self.sendEvent("terminated", {"exitCode": exitCode})
        }
        
        handlePythonError(error) {
            # Handle process spawn/execution errors
            errorMessage = f"Python process error: {error}"
            print(f"[FrameDebugAdapter] Python process error: {error}")
            self.sendEvent("output", {"output": errorMessage, "category": "stderr"})
            self.sendEvent("terminated", {"exitCode": 1, "error": True})
        }
        
        sendInitializationData() {
            self.sendToRuntime({
                "type": "command",
                "action": "initialize",
                "data": {
                    "stopOnEntry": self.stopOnEntry,
                    "sourceMap": self.sourceMap,
                    "breakpoints": self.pendingBreakpoints
                }
            })
        }
        
        sendBreakpoints(lines) {
            self.sendToRuntime({
                "type": "command",
                "action": "setBreakpoints",
                "data": {"lines": lines}
            })
        }
        
        sendBreakpointsToRuntime(lines) {
            print(f"[BREAKPOINT PROTOCOL] 5. FDASM → PRTSM: Sending breakpoints {lines}")
            # FDASM coordinates with PRTSM via sendBreakpoints action
            self.sendBreakpoints(lines)
        }
        
        sendContinueCommand() {
            self.sendToRuntime({
                "type": "command",
                "action": "continue"
            })
        }
        
        sendStepCommand(stepType) {
            self.sendToRuntime({
                "type": "command",
                "action": stepType
            })
        }
        
        sendTerminateCommand() {
            self.sendToRuntime({
                "type": "command",
                "action": "foo"
            })
        }
        
        cleanup() {
            if self.pythonProcess {
                self.pythonProcess.kill()
            }
            if self.server {
                self.server.close()
            }
        }
        
        fullCleanup() {
            # Complete session reset for restart - coordinate with runtime
            self.sendDebugConsole("Performing full session cleanup...")
            
            # Kill processes and close connections
            self.cleanup()
            
            # Reset all state variables to initial values
            self.server = None
            self.socket = None
            self.debugPort = 0
            self.pythonProcess = None
            self.frameFile = ""
            self.pythonCode = ""
            self.debugCode = ""
            self.sourceMap = {}
            self.stopOnEntry = False
            self.pendingBreakpoints = []
            self.activeBreakpoints = []
            self.clientId = ""
            self.adapterId = ""
            self.configurationComplete = False
            self.queuedCommand = None
            self.connectionTimeout = 0
            self.terminationTimeout = 0
            self.retryCount = 0
            
            self.sendDebugConsole("Session state completely reset for restart")
        }
        
        # ==== VS Code Integration Functions ====
        
        setVSCodeSession(session) {
            # Store VS Code session for integration
            self.vscodeSession = session
            print("[FrameDebugAdapter] VS Code session connected to state machine")
        }
        
        sendEvent(event, data) {
            # Send DAP event to VS Code
            # TypeScript Implementation: this.vscodeSession.sendEvent(new OutputEvent/StoppedEvent/etc)
            print(f"[FrameDebugAdapter] sendEvent: {event} - {data}")
            if self.vscodeSession {
                if event == "output" {
                    # Send output to VS Code debug console
                    self.vscodeSession.sendEvent("OutputEvent", data.output, data.category or "stdout")
                } elif event == "stopped" {
                    # Send stopped event to VS Code
                    self.vscodeSession.sendEvent("StoppedEvent", data.reason, data.threadId)
                } elif event == "terminated" {
                    # Send terminated event to VS Code
                    self.vscodeSession.sendEvent("TerminatedEvent")
                }
            }
        }
        
        sendResponse(command, data) {
            # Send DAP response to VS Code
            # TypeScript Implementation: response.body = data; this.vscodeSession.sendResponse(response)
            print(f"[FrameDebugAdapter] sendResponse: {command} - {data}")
        }
        
        sendError(command, message) {
            # Send DAP error to VS Code
            # TypeScript Implementation: this.vscodeSession.sendEvent(new OutputEvent(message, 'stderr'))
            print(f"[FrameDebugAdapter] sendError: {command} - {message}")
        }
        
        sendDebugConsole(message) {
            # Send message specifically to VS Code DEBUG CONSOLE
            # TypeScript Implementation: this.vscodeSession.sendEvent(new OutputEvent(message + '\n', 'stdout'))
            self.sendEvent("output", {"output": f"{message}\n", "category": "stdout"})
        }
        
        # ==== TCP Server Functions ====
        
        async createTcpServer() {
            # Create TCP server for Python runtime communication
            # Returns: port number that server is listening on
            
            # Create server with connection handler
            self.server = await self.createAsyncServer(self.handleRuntimeConnection)
            
            # Listen on random available port and get assigned port
            port = await self.server.listen(0, "127.0.0.1")
            
            print(f"[FrameDebugAdapter] Created TCP server on port {port}")
            return port
        }
        
        sendToRuntime(message) {
            # Send message to Python runtime via TCP socket
            # TypeScript Implementation: socket.write(JSON.stringify(message))
            print(f"[FrameDebugAdapter] sendToRuntime: {message}")
        }
        
        # ==== Process Management Functions ====
        
        spawn(command, args, options) {
            # Spawn child process
            # TypeScript Implementation: child_process.spawn(command, args, options)
            print(f"[FrameDebugAdapter] spawn: {command} {args} {options}")
            return None  # Mock process object
        }
        
        killPythonProcess() {
            # Force kill Python process
            if self.pythonProcess {
                print("[FrameDebugAdapter] Killing Python process")
                # TypeScript Implementation: this.pythonProcess.kill('SIGKILL')
            }
        }
        
        closeSocket() {
            # Close TCP server and socket connections
            if self.server {
                print("[FrameDebugAdapter] Closing TCP server")
                # TypeScript Implementation: this.server.close()
            }
        }
        
        # ==== Code Generation Functions ====
        
        createTranspiler() {
            # Create Frame transpiler instance
            # TypeScript Implementation: create transpiler using utils/native binary
            print("[FrameDebugAdapter] Creating Frame transpiler...")
            return FrameTranspiler()
        }
        
        injectDebugRuntime(pythonCode, sourceMap) {
            # Inject debug runtime into Python code with source mapping
            # TypeScript Implementation: injectDebugRuntime from PythonRuntimeLoader
            return injectDebugRuntime(pythonCode, sourceMap)
        }
        
        # ==== Utility Functions ====
        
        handleUnexpectedStop(reason, threadId, text) {
            # Handle unexpected debugging stops
            self.sendEvent("output", {
                "output": f"Unexpected stop: {reason} at thread {threadId} - {text}\n",
                "category": "stderr"
            })
        }
        
        sendPauseCommand(threadId) {
            self.sendToRuntime({
                "type": "command", 
                "action": "pause",
                "data": {"threadId": threadId}
            })
        }
        
        # ==== Network Infrastructure Functions ====
        
        createNetServer() {
            # Create a TCP network server
            # TypeScript Implementation: net.createServer()
            return NetworkServer()
        }
        
        handleRuntimeConnection(socket) {
            # Handle incoming Python runtime connection
            print("[FrameDebugAdapter] Python runtime connected")
            self.socket = socket
            
            # Set up socket event handlers using Frame interface method references
            socket.onData(self.onData)
            socket.onClose(self.onClose)
            socket.onError(self.onError)
        }
        
        
        parseJson(data) {
            # Parse JSON data
            # TypeScript Implementation: JSON.parse(data.toString())
            return JsonParser.parse(data)
        }
    
    domain:
        # VS Code integration
        var vscodeSession = None
        
        # Connection management
        var server = None
        var socket = None
        var debugPort = 0
        var pythonProcess = None
        
        # Program state
        var frameFile = ""
        var pythonCode = ""
        var debugCode = ""
        var sourceMap = {}
        var stopOnEntry = False
        var currentSource = ""  # Currently debugging file
        
        # Breakpoint management  
        var pendingBreakpoints = []
        var activeBreakpoints = []
        var targetFileBreakpoints = []  # Breakpoints for the debugging target file
        
        # Configuration
        var clientId = ""
        var adapterId = ""
        var configurationComplete = False
        var queuedCommand = None
        
        # Timeouts and retries
        var connectionTimeout = 0
        var terminationTimeout = 0
        var retryCount = 0
        
        # Debug utilities  
        var framec = None  # Transpiler instance
}