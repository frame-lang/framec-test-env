import Foundation


class SFrameEvent {
    var _message: String
    var _parameters: [String: Any]

    init(message: String, parameters: [String: Any] = [:]) {
        self._message = message
        self._parameters = parameters
    }
}

class SFrameContext {
    var _event: SFrameEvent
    var _return: Any?
    var _data: [String: Any] = [:]

    init(event: SFrameEvent, defaultReturn: Any? = nil) {
        self._event = event
        self._return = defaultReturn
    }
}

class SCompartment {
    var state: String
    var state_args: [String: Any] = [:]
    var state_vars: [String: Any] = [:]
    var enter_args: [String: Any] = [:]
    var exit_args: [String: Any] = [:]
    var forward_event: SFrameEvent?
    var parent_compartment: SCompartment?

    init(state: String) {
        self.state = state
    }

    func copy() -> SCompartment {
        let c = SCompartment(state: self.state)
        c.state_args = self.state_args
        c.state_vars = self.state_vars
        c.enter_args = self.enter_args
        c.exit_args = self.exit_args
        c.forward_event = self.forward_event
        c.parent_compartment = self.parent_compartment
        return c
    }
}

class S {
    private var _state_stack: [SCompartment]
    private var __compartment: SCompartment
    private var __next_compartment: SCompartment?
    private var _context_stack: [SFrameContext]

    init() {
        _state_stack = []
        _context_stack = []
        // HSM: Create parent compartment chain
        let __parent_comp_0 = SCompartment(state: "P")
        self.__compartment = SCompartment(state: "A")
        self.__compartment.parent_compartment = __parent_comp_0
        self.__next_compartment = nil
        let __frame_event = SFrameEvent(message: "$>")
        let __ctx = SFrameContext(event: __frame_event)
        _context_stack.append(__ctx)
        __kernel(_context_stack[_context_stack.count - 1]._event)
        _context_stack.removeLast()
    }

    private func __kernel(_ __e: SFrameEvent) {
        __router(__e)
        while __next_compartment != nil {
            let next_compartment = __next_compartment!
            __next_compartment = nil
            let exit_event = SFrameEvent(message: "<$")
            __router(exit_event)
            __compartment = next_compartment
            if __compartment.forward_event == nil {
                let enter_event = SFrameEvent(message: "$>")
                __router(enter_event)
            } else {
                let forward_event = __compartment.forward_event!
                __compartment.forward_event = nil
                if forward_event._message == "$>" {
                    __router(forward_event)
                } else {
                    let enter_event = SFrameEvent(message: "$>")
                    __router(enter_event)
                    __router(forward_event)
                }
            }
        }
    }

    private func __router(_ __e: SFrameEvent) {
        let state_name = __compartment.state
        if state_name == "A" {
            _state_A(__e)
        } else if state_name == "P" {
            _state_P(__e)
        }
    }

    private func __transition(_ next: SCompartment) {
        __next_compartment = next
    }

    public func e1() {
        let __e = SFrameEvent(message: "e1")
        let __ctx = SFrameContext(event: __e)
        _context_stack.append(__ctx)
        __kernel(_context_stack[_context_stack.count - 1]._event)
        _context_stack.removeLast()
    }

    public func e2() {
        let __e = SFrameEvent(message: "e2")
        let __ctx = SFrameContext(event: __e)
        _context_stack.append(__ctx)
        __kernel(_context_stack[_context_stack.count - 1]._event)
        _context_stack.removeLast()
    }

    private func _state_P(_ __e: SFrameEvent) {

    }

    private func _state_A(_ __e: SFrameEvent) {
        if __e._message == "e1" {
            _state_P(__e)
        } else if __e._message == "e2" {
            _state_P(__e)
        }
    }
}

// TAP test harness
// main
    print("TAP version 14")
    print("1..1")
    let s = S()
    print("ok 1 - multiple_handlers")

