
class SFrameEvent
    attr_accessor :_message
    attr_accessor :_parameters

    def initialize(message, parameters = {})
        @_message = message
        @_parameters = parameters
    end
end


class SFrameContext
    attr_accessor :_event
    attr_accessor :_return
    attr_accessor :_data

    def initialize(event, default_return = nil)
        @_event = event
        @_return = default_return
        @_data = {}
    end
end


class SCompartment
    attr_accessor :state
    attr_accessor :state_args
    attr_accessor :state_vars
    attr_accessor :enter_args
    attr_accessor :exit_args
    attr_accessor :forward_event
    attr_accessor :parent_compartment

    def initialize(state, parent_compartment = nil)
        @state = state
        @state_args = {}
        @state_vars = {}
        @enter_args = {}
        @exit_args = {}
        @forward_event = nil
        @parent_compartment = parent_compartment
    end

    def copy
        c = SCompartment.new(@state, @parent_compartment)
        c.state_args = @state_args.dup
        c.state_vars = @state_vars.dup
        c.enter_args = @enter_args.dup
        c.exit_args = @exit_args.dup
        c.forward_event = @forward_event
        c
    end
end


class S
    attr_accessor :_state_stack
    attr_accessor :__compartment
    attr_accessor :__next_compartment
    attr_accessor :_context_stack

    def initialize
        @_state_stack = []
        @_context_stack = []
        # HSM: Create parent compartment chain
        __parent_comp_0 = SCompartment.new("P", nil)
        @__compartment = SCompartment.new("A", __parent_comp_0)
        @__next_compartment = nil
        __frame_event = SFrameEvent.new("$>")
        __ctx = SFrameContext.new(__frame_event, nil)
        @_context_stack.push(__ctx)
        __kernel(@_context_stack[@_context_stack.length - 1]._event)
        @_context_stack.pop
    end

    def __kernel(__e)
        # Route event to current state
        __router(__e)
        while @__next_compartment != nil
            next_compartment = @__next_compartment
            @__next_compartment = nil
            exit_event = SFrameEvent.new("<$", @__compartment.exit_args)
            __router(exit_event)
            @__compartment = next_compartment
            if next_compartment.forward_event == nil
                enter_event = SFrameEvent.new("$>", @__compartment.enter_args)
                __router(enter_event)
            else
                forward_event = next_compartment.forward_event
                next_compartment.forward_event = nil
                if forward_event._message == "$>"
                    __router(forward_event)
                else
                    enter_event = SFrameEvent.new("$>", @__compartment.enter_args)
                    __router(enter_event)
                    __router(forward_event)
                end
            end
        end
    end

    def __router(__e)
        state_name = @__compartment.state
        handler_name = "_state_#{state_name}"
        if respond_to?(handler_name, true)
            send(handler_name, __e)
        end
    end

    def __transition(next_compartment)
        @__next_compartment = next_compartment
    end

    def e1
        __e = SFrameEvent.new("e1", {})
        __ctx = SFrameContext.new(__e, nil)
        @_context_stack.push(__ctx)
        __kernel(__e)
        @_context_stack.pop
    end

    def e2
        __e = SFrameEvent.new("e2", {})
        __ctx = SFrameContext.new(__e, nil)
        @_context_stack.push(__ctx)
        __kernel(__e)
        @_context_stack.pop
    end

    def _state_P(__e)
    end

    def _state_A(__e)
        if __e._message == "e1"
            _state_P(__e)
        elsif __e._message == "e2"
            _state_P(__e)
        end
    end
end

puts("TAP version 14")
puts("1..1")
begin
    s = S.new
    if s.respond_to?(:e)
        s.e()
    end
    puts("ok 1 - multiple_handlers")
rescue => ex
    puts("not ok 1 - multiple_handlers # #{ex}")
end

