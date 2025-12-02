from frame_runtime_py import FrameEvent, FrameCompartment

class PythonDebugRuntime:
    def __init__(self, *sys_params):
        start_count = 0
        enter_count = 0
        start_args = list(sys_params[0:start_count])
        enter_args = list(sys_params[start_count:start_count+enter_count])
        domain_args = list(sys_params[start_count+enter_count:])
        state_args = {}
        self._compartment = FrameCompartment("__PythonDebugRuntime_state_Default", enter_args=enter_args, state_args=state_args)
        self._stack = []
        self._system_return_stack = []
        enter_event = FrameEvent("$enter", enter_args)
        self._frame_router(enter_event, self._compartment)
    def _frame_transition(self, next_compartment: FrameCompartment):
        self._compartment = next_compartment
        enter_event = FrameEvent("$enter", getattr(next_compartment, "enter_args", None))
        self._frame_router(enter_event, next_compartment)
    def _frame_router(self, __e: FrameEvent, c: FrameCompartment=None):
        compartment = c or self._compartment
        msg = getattr(__e, "_message", None)
        if msg is None:
            return
        handler = getattr(self, f"_event_{msg}", None)
        if handler is None:
            return
        return handler(__e, compartment)
    def _frame_stack_push(self):
        self._stack.append(self._compartment)
    def _frame_stack_pop(self):
        if self._stack:
            prev = self._stack.pop()
            self._frame_transition(prev)
    async def _action_connectToDebugServer(self):
        
        self.debugPort = self.getDebugPortFromEnv()
        if self.debugPort == 0:
                self.raiseError("FRAME_DEBUG_PORT not set")
                return
        
        self.initialized = False
        await self.openSocketConnection("127.0.0.1", self.debugPort)
        
    async def connectToDebugServer(self):
        return await self._action_connectToDebugServer()
    def _action_traceDispatch(self, frame, event, arg):
        
        # Dispatch trace events to state machine
        if event == "line":
                self.dispatchAsync(self.onTraceLine(frame, frame.f_lineno))
        elif event == "call":
                self.dispatchAsync(self.onTraceCall(frame))
        elif event == "return":
                self.dispatchAsync(self.onTraceReturn(frame))
        elif event == "exception":
                self.dispatchAsync(self.onTraceException(frame, arg[0], arg[1]))
        
        return self.traceDispatch  # Continue tracing with this function
        
    def traceDispatch(self, frame, event, arg):
        return self._action_traceDispatch(frame, event, arg)
    def _action_pauseExecution(self, frame, reason, frameLine):
        
        self.currentFrame = frame
        self.currentFrameLine = frameLine
        self.pauseReason = reason
        
        # Clear step mode when paused
        self.clearStepMode()
        
    def pauseExecution(self, frame, reason, frameLine):
        return self._action_pauseExecution(frame, reason, frameLine)
    def _action_enterPausedState(self):
        
        self.sendDebugConsole(f"Paused at line {self.currentFrameLine}")
        self.sendStoppedEvent()
        self.createResumeEvent()
        
    def enterPausedState(self):
        return self._action_enterPausedState()
    def _action_signalInitializationComplete(self):
        
        # Signal that initialization is complete using async event
        if hasattr(self, "on_initialization_complete") and self.on_initialization_complete:
                callback = self.on_initialization_complete
                callback()
        
    def signalInitializationComplete(self):
        return self._action_signalInitializationComplete()
    def _action_createResumeEvent(self):
        
        # Create async event for resume coordination
        try:
                self.resumeEvent = asyncio.Event()
        except Exception as e:
                print(f"[PythonDebugRuntime] Failed to create resume event: {e}")
        
    def createResumeEvent(self):
        return self._action_createResumeEvent()
    def _action_signalResumeEvent(self):
        
        # Signal that execution should resume
        if hasattr(self, "resumeEvent") and self.resumeEvent:
                try:
                        self.resumeEvent.set()
                except Exception as e:
                        print(f"[PythonDebugRuntime] Failed to signal resume: {e}")
        
    def signalResumeEvent(self):
        return self._action_signalResumeEvent()
    def _action_clearStepMode(self):
        
        self.stepMode = None
        self.stepTargetFrame = None
        self.stepDepth = 0
        
    def clearStepMode(self):
        return self._action_clearStepMode()
    def _action_mapToFrameLine(self, pythonLine):
        
        # Map Python line number to Frame source line
        if not self.sourceMap:
                return pythonLine
        return self.sourceMap.get(str(pythonLine), None)
        
    def mapToFrameLine(self, pythonLine):
        return self._action_mapToFrameLine(pythonLine)
    def _action_isUserCode(self, frame):
        
        # Check if frame is in user code (not debug runtime)
        return frame.f_lineno >= self.debugBoundary
        
    def isUserCode(self, frame):
        return self._action_isUserCode(frame)
    def _action_shouldStopStepNext(self, frame, frameLine):
        
        # Stop if we're at the same depth and have a valid Frame line
        return (
                self.stepDepth == 0 and
                frameLine is not None and
                self.isUserCode(frame)
        )
        
    def shouldStopStepNext(self, frame, frameLine):
        return self._action_shouldStopStepNext(frame, frameLine)
    def _action_sendStoppedEvent(self):
        
        self.sendMessage({
                "type": "event",
                "event": "stopped",
                "data": {
                        "reason": self.pauseReason,
                        "threadId": 1,
                        "text": f"Paused at Frame line {self.currentFrameLine}"
                }
        })
        
    def sendStoppedEvent(self):
        return self._action_sendStoppedEvent()
    def _action_sendMessage(self, message):
        
        try:
                data = self.encodeMessage(message)
                if isinstance(data, str):
                        payload = data.encode("utf-8")
                else:
                        payload = data
                if self.runtimeSocket:
                        try:
                                with open("/tmp/frame_runtime_log.txt", "a") as logf:
                                        logf.write(f"sending: {message}\\n")
                        except Exception:
                                pass
                        print(f"[PythonDebugRuntime] sending {message.get('event', message.get('type'))}")
                        self.runtimeSocket.sendall(payload)
        except Exception as e:
                print(f"[PythonDebugRuntime] Failed to send message: {e}")
        
        
    def sendMessage(self, message):
        return self._action_sendMessage(message)
    def _action_logDebug(self, message: str):
        
        print(f"[PythonDebugRuntime] {message}")
        
    def logDebug(self, message: str):
        return self._action_logDebug(message)
    def _action_dispatchAsync(self, coro):
        
        try:
                eventLoop = self.eventLoop
                if not eventLoop:
                        try:
                                eventLoop = asyncio.get_running_loop()
                                self.eventLoop = eventLoop
                        except Exception:
                                eventLoop = None
                if eventLoop:
                        eventLoop.call_soon_threadsafe(lambda: asyncio.create_task(coro))
                else:
                        try:
                                asyncio.run(coro)
                        except Exception as inner:
                                print(f"[PythonDebugRuntime] Coroutine scheduling fallback failed: {inner}")
        except Exception as e:
                print(f"[PythonDebugRuntime] Failed to schedule coroutine: {e}")
        
    def dispatchAsync(self, coro):
        return self._action_dispatchAsync(coro)
    async def _action_startMessageListener(self):
        
        # Start async message listener task
        try:
                self.messageTask = asyncio.create_task(self.messageListenerLoop())
        except Exception as e:
                print(f"[PythonDebugRuntime] Failed to start message listener: {e}")
        
    async def startMessageListener(self):
        return await self._action_startMessageListener()
    async def _action_messageListenerLoop(self):
        
        # Async message processing loop
        while not self.terminated and self.runtimeSocket:
                try:
        # Use async socket operations
                        await asyncio.sleep(0.01)  # Small delay to prevent busy loop
        
        # Check if socket has data available
                        if self.runtimeSocket:
                                chunk = await asyncio.to_thread(self.runtimeSocket.recv, 4096)
                                if chunk:
                                        self.bufferIncomingChunk(chunk)
                                        self.flushBufferedMessages()
                                else:
        # Socket closed
                                        break
                except Exception as e:
                        print(f"[PythonDebugRuntime] Message loop error: {e}")
                        break
        
    async def messageListenerLoop(self):
        return await self._action_messageListenerLoop()
    def _action_handleMessage(self, message):
        
        # Route incoming messages to state machine
        try:
                print(f"[PythonDebugRuntime] handleMessage: {message}")
        except Exception:
                pass
        if message.type == "command":
                action = message.action
                if action == "initialize":
                        self.applyInitializationConfig(message.data)
                elif action == "continue":
                        self.dispatchAsync(self.onContinueExecution())
                elif action == "next":
                        self.dispatchAsync(self.onNextStep())
                elif action == "stepIn":
                        self.dispatchAsync(self.onStepInto())
                elif action == "stepOut":
                        self.dispatchAsync(self.onStepOutOf())
                elif action == "setBreakpoints":
                        self.dispatchAsync(self.onSetBreakpoints(message.data.lines))
                elif action == "pause":
                        self.dispatchAsync(self.onPause())
                elif action == "terminate":
                        self.dispatchAsync(self.onTerminate())
                elif action == "getCallStack":
        # Phase 7: Call stack generation
                        threadId = message.data.get("threadId", 1)
                        self.dispatchAsync(self.onGetCallStack(threadId))
        
    def handleMessage(self, message):
        return self._action_handleMessage(message)
    def _action_applyInitializationConfig(self, data):
        
        config = {
                "stopOnEntry": data.get("stopOnEntry", False),
                "sourceMap": data.get("sourceMap", {}),
                "breakpoints": data.get("breakpoints", [])
        }
        self.dispatchAsync(self.onInitialize(config))
        
    def applyInitializationConfig(self, data):
        return self._action_applyInitializationConfig(data)
    def _action_sendEvent(self, event_type, data):
        
        # Send event to debug adapter
        print(f"[PythonDebugRuntime] sendEvent: {event_type} - {data}")
        
    def sendEvent(self, event_type, data):
        return self._action_sendEvent(event_type, data)
    def _action_sendDebugConsole(self, message):
        
        # Send message specifically to VS Code DEBUG CONSOLE
        # Python Implementation: Send via socket to debug adapter
        self.sendMessage({
                "type": "event",
                "event": "output",
                "data": {"output": message + "\n", "category": "stdout"}
        })
        
    def sendDebugConsole(self, message):
        return self._action_sendDebugConsole(message)
    async def _action_async_start(self):
        
        # Loader expects an async_start entrypoint; drive connect + connected event
        try:
                self.eventLoop = asyncio.get_event_loop()
                await self.connectToDebugServer()
                self.onConnected()
        except Exception as e:
                print(f"[PythonDebugRuntime] async_start failed: {e}")
                self.onConnectionError()
        
    async def async_start(self):
        return await self._action_async_start()
    def _action_handleTermination(self):
        
        self.sendDebugConsole("Terminating Python runtime...")
        self.stopMessageListener()
        self.sendMessage({
                "type": "event",
                "event": "terminated",
                "data": {"exitCode": 0}
        })
        self.dispatchAsync(self.closeSocketConnection())
        self.exitProgram()
        
    def handleTermination(self):
        return self._action_handleTermination()
    def _action_getDebugPortFromEnv(self):
        
        # Use proper Frame syntax with module-level imports
        return int(os.environ.get("FRAME_DEBUG_PORT", 0))
        
    def getDebugPortFromEnv(self):
        return self._action_getDebugPortFromEnv()
    def _action_createSocket(self):
        
        # Use proper Frame syntax with module-level imports
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def createSocket(self):
        return self._action_createSocket()
    async def _action_openSocketConnection(self, host, port):
        
        # Establish TCP connection to debug adapter
        try:
                self.logDebug(f"Opening socket to {host}:{port}")
                self.runtimeSocket = await asyncio.to_thread(socket.create_connection, (host, port))
                self.logDebug("Socket connected; sending onConnected")
                self.onConnected()
        except Exception as e:
                print(f"[PythonDebugRuntime] Connection error: {e}")
                self.logDebug(f"Connection error: {e}")
                self.onConnectionError()
        
    async def openSocketConnection(self, host, port):
        return await self._action_openSocketConnection(host, port)
    async def _action_closeSocketConnection(self):
        
        # Close TCP connection cleanly
        if self.runtimeSocket:
                try:
                        await asyncio.to_thread(self.runtimeSocket.close)
                except Exception as e:
                        print(f"[PythonDebugRuntime] Failed to close socket: {e}")
        self.runtimeSocket = None
        
    async def closeSocketConnection(self):
        return await self._action_closeSocketConnection()
    async def _action_sendSocketData(self, data):
        
        # Send data via TCP socket
        if not self.runtimeSocket:
                return
        try:
                if isinstance(data, str):
                        payload = data.encode("utf-8")
                else:
                        payload = data
                await asyncio.to_thread(self.runtimeSocket.sendall, payload)
        except Exception as e:
                print(f"[PythonDebugRuntime] Failed to send data: {e}")
        
    async def sendSocketData(self, data):
        return await self._action_sendSocketData(data)
    def _action_encodeMessage(self, message):
        
        # JSON encode with newline delimiter for socket protocol
        jsonText = json.dumps(message)
        return jsonText + "\n"
        
    def encodeMessage(self, message):
        return self._action_encodeMessage(message)
    def _action_stopMessageListener(self):
        
        # Stop async message listener task
        if hasattr(self, "messageTask") and self.messageTask:
                try:
                        self.messageTask.cancel()
                except Exception as e:
                        print(f"[PythonDebugRuntime] Failed to stop message listener: {e}")
        
    def stopMessageListener(self):
        return self._action_stopMessageListener()
    def _action_bufferIncomingChunk(self, data):
        
        text = self.decodeSocketChunk(data)
        if self.incomingBuffer:
                self.incomingBuffer = self.incomingBuffer + text
        else:
                self.incomingBuffer = text
        
    def bufferIncomingChunk(self, data):
        return self._action_bufferIncomingChunk(data)
    def _action_decodeSocketChunk(self, data):
        
        try:
                return data.decode("utf-8")
        except Exception:
                try:
                        return data.toString("utf8")
                except Exception:
                        try:
                                return data.toString()
                        except Exception:
                                return str(data)
        
    def decodeSocketChunk(self, data):
        return self._action_decodeSocketChunk(data)
    def _action_flushBufferedMessages(self):
        
        if not self.incomingBuffer:
                return
        parts = self.incomingBuffer.split("\n")
        totalParts = len(parts)
        if totalParts == 0:
                return
        self.incomingBuffer = parts[totalParts - 1]
        index = 0
        while index < totalParts - 1:
                line = parts[index]
                if line:
                        self.processBufferedLine(line)
                index = index + 1
        
    def flushBufferedMessages(self):
        return self._action_flushBufferedMessages()
    def _action_processBufferedLine(self, text):
        
        try:
                print(f"[PythonDebugRuntime] raw line: {text}")
        except Exception:
                pass
        try:
                message = self.parseJsonMessage(text)
                print(f"[PythonDebugRuntime] parsed message: {message}")
                self.handleMessage(message)
        except Exception as e:
                print(f"[PythonDebugRuntime] Failed to parse runtime message: {e}")
        
    def processBufferedLine(self, text):
        return self._action_processBufferedLine(text)
    def _action_trackPythonFrame(self, frame, event):
        
        # Track Python frame for call stack generation
        if event == "call":
        # Add frame to call stack
                frameInfo = {}
                frameInfo["functionName"] = frame.f_code.co_name
                frameInfo["filename"] = frame.f_code.co_filename
                frameInfo["line"] = frame.f_lineno
                frameInfo["depth"] = self.callStackDepth
                self.pythonCallStack.append(frameInfo)
        
        # Limit call stack size
                if len(self.pythonCallStack) > 50:
        # Keep only the last 50 frames
                        trimmedStack = []
                        startIndex = len(self.pythonCallStack) - 50
                        i = startIndex
                        while i < len(self.pythonCallStack):
                                frameAtI = frameRuntimeGetArrayElement(self.pythonCallStack, i)
                                trimmedStack.append(frameAtI)
                                i = i + 1
                        self.pythonCallStack = trimmedStack
        elif event == "return":
        # Remove frames from stack (unwind to current depth)
                filteredStack = []
                for frameInfo in self.pythonCallStack:
                        if frameInfo["depth"] <= self.callStackDepth:
                                filteredStack.append(frameInfo)
                self.pythonCallStack = filteredStack
        
    def trackPythonFrame(self, frame, event):
        return self._action_trackPythonFrame(frame, event)
    def _action_buildPythonCallStack(self):
        
        # Build current Python call stack for DAP
        callStack = []
        
        # Use current frame if available
        if self.currentFrame:
                currentFrameInfo = {}
                currentFrameInfo["functionName"] = self.currentFrame.f_code.co_name
                currentFrameInfo["filename"] = self.currentFrame.f_code.co_filename
                currentFrameInfo["line"] = self.currentFrame.f_lineno
                currentFrameInfo["depth"] = self.callStackDepth
                callStack.append(currentFrameInfo)
        
        # Add tracked call stack frames (most recent first)
        reversedStack = []
        index = len(self.pythonCallStack) - 1
        while index >= 0:
                frameAtIndex = frameRuntimeGetArrayElement(self.pythonCallStack, index)
                reversedStack.append(frameAtIndex)
                index = index - 1
        
        for frameInfo in reversedStack:
                shouldAdd = True
                if len(callStack) > 0:
                        firstFrame = frameRuntimeGetArrayElement(callStack, 0)
                        if frameInfo["line"] == firstFrame["line"]:
                                shouldAdd = False
                if shouldAdd:
                        callStack.append(frameInfo)
        
        return callStack
        
    def buildPythonCallStack(self):
        return self._action_buildPythonCallStack()
    def _action_sleepShort(self):
        
        # Use proper Frame syntax with module-level imports
        time.sleep(0.01)
        
    def sleepShort(self):
        return self._action_sleepShort()
    def _action_installTraceFunction(self):
        
        # Use proper Frame syntax with module-level imports
        sys.settrace(self.traceDispatch)
        
    def installTraceFunction(self):
        return self._action_installTraceFunction()
    def _action_removeTraceFunction(self):
        
        # Use proper Frame syntax with module-level imports
        sys.settrace(None)
        
    def removeTraceFunction(self):
        return self._action_removeTraceFunction()
    def _action_retryConnection(self):
        
        # Retry connection logic
        print("[PythonDebugRuntime] Retrying connection...")
        
    def retryConnection(self):
        return self._action_retryConnection()
    def _action_raiseError(self, message):
        
        # Python Implementation: raise RuntimeError(message)
        raise RuntimeError(message)
        
    def raiseError(self, message):
        return self._action_raiseError(message)
    def _action_exitProgram(self):
        
        # Use proper Frame syntax with module-level imports
        print("[PythonDebugRuntime] Exiting program")
        sys.exit(0)
        
    def exitProgram(self):
        return self._action_exitProgram()
    def _action_parseJsonMessage(self, data):
        
        # Use proper Frame syntax with module-level imports
        try:
                utf8Str = data.decode("utf-8")
        except Exception:
                if isinstance(data, str):
                        utf8Str = data
                else:
                        utf8Str = str(data)
        return json.loads(utf8Str)
        
    def parseJsonMessage(self, data):
        return self._action_parseJsonMessage(data)
    def _event_onConnected(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Connecting":
            
            self.sendDebugConsole("Connected to debug server")
            self.sendMessage({
                "type": "event",
                "event": "connected"
            })
            # Start async message listener
            self.dispatchAsync(self.startMessageListener())
            self._frame_transition(FrameCompartment("__PythonDebugRuntime_state_AwaitingInit"))
            return
            
    def _event_onConnectionError(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Connecting":
            
            self.sendDebugConsole("Failed to connect to debug server")
            self.retryConnection()
            # Stay in Connecting
            
    def _event_onContinueExecution(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_WaitingForEntry":
            
            # Skip stop on entry if user continues
            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Running")
            self._frame_transition(next_compartment)
            return
            
        elif c.state == "__PythonDebugRuntime_state_Paused":
            
            self.sendDebugConsole("Continuing execution")
            self.clearStepMode()
            self.pauseRequested = False
            self.sendMessage({
                "type": "event",
                "event": "continued",
                "data": {"threadId": 1}
            })
            self.signalResumeEvent()
            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Running")
            self._frame_transition(next_compartment)
            return
            
    def _event_onGetCallStack(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            self.sendDebugConsole(f"Call stack request for thread {threadId}")
            
            # Build current Python call stack
            callStack = self.buildPythonCallStack()
            
            self.sendMessage({
                "type": "response",
                "success": True,
                "command": "getCallStack",
                "data": {
                    "threadId": threadId,
                    "callStack": callStack
                }
            })
            
        elif c.state == "__PythonDebugRuntime_state_Paused":
            
            self.sendDebugConsole(f"Call stack request for thread {threadId}")
            
            # Build current Python call stack
            callStack = self.buildPythonCallStack()
            
            self.sendMessage({
                "type": "response",
                "success": True,
                "command": "getCallStack",
                "data": {
                    "threadId": threadId,
                    "callStack": callStack
                }
            })
            # Stay paused
            
    def _event_onInitialize(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_AwaitingInit":
            
            self.sendDebugConsole("Initializing debug runtime...")
            self.stopOnEntry = config["stopOnEntry"]
            self.sourceMap = config["sourceMap"]
            self.breakpoints = set(config["breakpoints"])
            self.initialized = True
            
            # Install trace function
            self.installTraceFunction()
            
            # Signal initialization complete using callback
            self.signalInitializationComplete()
            
            self.sendMessage({
                "type": "event",
                "event": "ready"
            })
            
            if self.stopOnEntry:
                next_compartment = FrameCompartment("__PythonDebugRuntime_state_WaitingForEntry")
            else:
                next_compartment = FrameCompartment("__PythonDebugRuntime_state_Running")
            self._frame_transition(next_compartment)
            return
            
    def _event_onNextStep(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Paused":
            
            self.sendDebugConsole("Step next")
            self.stepMode = "next"
            self.stepTargetFrame = self.currentFrame
            self.stepDepth = 0
            self.sendMessage({
                "type": "event",
                "event": "continued",
                "data": {"threadId": 1}
            })
            self.signalResumeEvent()
            self._frame_transition(FrameCompartment("__PythonDebugRuntime_state_Running"))
            return
            
    def _event_onPause(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            self.pauseRequested = True
            # Will pause on next user code line
            
    def _event_onSetBreakpoints(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            self.breakpoints = set(lines)
            self.sendMessage({
                "type": "response",
                "success": True,
                "command": "setBreakpoints"
            })
            
        elif c.state == "__PythonDebugRuntime_state_Paused":
            
            self.breakpoints = set(lines)
            self.sendMessage({
                "type": "response",
                "success": True,
                "command": "setBreakpoints"
            })
            # Stay paused
            
    def _event_onStepInto(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Paused":
            
            self.sendDebugConsole("Step into")
            self.stepMode = "stepIn"
            self.stepTargetFrame = None
            self.sendMessage({
                "type": "event",
                "event": "continued",
                "data": {"threadId": 1}
            })
            self.signalResumeEvent()
            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Running")
            self._frame_transition(next_compartment)
            return
            
    def _event_onStepOutOf(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Paused":
            
            self.sendDebugConsole("Step out")
            self.stepMode = "stepOut"
            self.stepTargetFrame = self.currentFrame
            self.stepDepth = 0
            self.sendMessage({
                "type": "event",
                "event": "continued",
                "data": {"threadId": 1}
            })
            self.signalResumeEvent()
            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Running")
            self._frame_transition(next_compartment)
            return
            
    def _event_onTerminate(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            self.handleTermination()
                            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Terminating")
            self._frame_transition(next_compartment)
            return
            
            
        elif c.state == "__PythonDebugRuntime_state_Paused":
            
            self.signalResumeEvent()
            self.handleTermination()
                            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Terminating")
            self._frame_transition(next_compartment)
            return
            
            
    def _event_onTraceCall(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            if self.stepMode == "next":
                self.stepDepth = self.stepDepth + 1
            elif self.stepMode == "stepOut":
                self.stepDepth = self.stepDepth + 1
            
            # Phase 7: Track call stack
            self.callStackDepth = self.callStackDepth + 1
            self.trackPythonFrame(frame, "call")
            
    def _event_onTraceException(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            frameLine = self.mapToFrameLine(frame.f_lineno)
            self.sendDebugConsole(f"Exception: {exc_type.__name__}: {exc_value}")
            
            if self.stopOnException and self.isUserCode(frame):
                self.pauseExecution(frame, "exception", frameLine)
                self.enterPausedState()
                                    next_compartment = FrameCompartment("__PythonDebugRuntime_state_Paused")
                self._frame_transition(next_compartment)
                return
            
            
    def _event_onTraceLine(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_WaitingForEntry":
            
            frameLine = self.mapToFrameLine(lineno)
            if frameLine is not None and self.isUserCode(frame):
                self.pauseExecution(frame, "entry", frameLine)
                self.enterPausedState()
                                    next_compartment = FrameCompartment("__PythonDebugRuntime_state_Paused")
                self._frame_transition(next_compartment)
                return
            
            # Continue execution if not user code
            
        elif c.state == "__PythonDebugRuntime_state_Running":
            
            # Map Python line to Frame line
            frameLine = self.mapToFrameLine(lineno)
            
            # Check for breakpoints
            if frameLine in self.breakpoints and self.isUserCode(frame):
                self.pauseExecution(frame, "breakpoint", frameLine)
                self.enterPausedState()
                                    next_compartment = FrameCompartment("__PythonDebugRuntime_state_Paused")
                self._frame_transition(next_compartment)
                return
            
            
            # Handle step modes
            if self.stepMode == "stepIn":
                if frameLine is not None and self.isUserCode(frame):
                    self.pauseExecution(frame, "step", frameLine)
                    self.enterPausedState()
                                            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Paused")
                    self._frame_transition(next_compartment)
                    return
            
            elif self.stepMode == "next":
                if self.shouldStopStepNext(frame, frameLine):
                    self.pauseExecution(frame, "step", frameLine)
                    self.enterPausedState()
                                            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Paused")
                    self._frame_transition(next_compartment)
                    return
            
            elif self.stepMode == "stepOut":
                # Will be handled in onTraceReturn
                pass
            
            # Handle pause request
            if self.pauseRequested and frameLine is not None and self.isUserCode(frame):
                self.pauseExecution(frame, "pause", frameLine)
                self.enterPausedState()
                                    next_compartment = FrameCompartment("__PythonDebugRuntime_state_Paused")
                self._frame_transition(next_compartment)
                return
            
            
    def _event_onTraceReturn(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Running":
            
            if self.stepMode == "next":
                self.stepDepth = max(0, self.stepDepth - 1)
            elif self.stepMode == "stepOut":
                self.stepDepth = max(0, self.stepDepth - 1)
                if self.stepDepth == 0 and frame == self.stepTargetFrame:
                    self.stepMode = "stepIn"
                    self.stepTargetFrame = None
            
            # Phase 7: Track call stack
            self.callStackDepth = max(0, self.callStackDepth - 1)
            self.trackPythonFrame(frame, "return")
            
    def _event_ping(self, __e: FrameEvent, compartment: FrameCompartment):
        c = compartment or self._compartment
        if c.state == "__PythonDebugRuntime_state_Default":
            
            self.sendMessage({
                "type": "event",
                "event": "ping",
                "data": {
                    "state": self._compartment.state,
                    "paused": self.pauseReason is not None,
                    "currentFrameLine": self.currentFrameLine,
                    "lastStoppedReason": self.pauseReason
                }
            })
            
        elif c.state == "__PythonDebugRuntime_state_Connecting":
            
            self.sendPingStatus("Connecting")
            
        elif c.state == "__PythonDebugRuntime_state_Paused":
            
            self.sendPingStatus("Paused")
            
    def onConnected(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onConnected", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onConnectionError(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onConnectionError", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onContinueExecution(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onContinueExecution", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onGetCallStack(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onGetCallStack", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onInitialize(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onInitialize", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onNextStep(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onNextStep", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onPause(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onPause", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onSetBreakpoints(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onSetBreakpoints", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onStepInto(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onStepInto", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onStepOutOf(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onStepOutOf", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onTerminate(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onTerminate", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onTraceCall(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onTraceCall", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onTraceException(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onTraceException", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onTraceLine(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onTraceLine", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def onTraceReturn(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("onTraceReturn", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
    def ping(self, *args, **kwargs):
        __initial = None
        self._system_return_stack.append(__initial)
        __e = FrameEvent("ping", list(args) if args else None)
        try:
            self._frame_router(__e, self._compartment)
            return self._system_return_stack[-1]
        finally:
            self._system_return_stack.pop()
