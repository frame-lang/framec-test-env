#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>
#include <functional>


#include <iostream>
#include <string>
#include <cassert>
#include <nlohmann/json.hpp>

class PersistStackFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    PersistStackFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class PersistStackFrameContext {
public:
    PersistStackFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    PersistStackFrameContext(PersistStackFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class PersistStackCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<PersistStackFrameEvent> forward_event;
    std::unique_ptr<PersistStackCompartment> parent_compartment;

    explicit PersistStackCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<PersistStackCompartment> clone() const {
        auto c = std::make_unique<PersistStackCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class PersistStack {
private:
    std::vector<std::unique_ptr<PersistStackCompartment>> _state_stack;
    std::unique_ptr<PersistStackCompartment> __compartment;
    std::unique_ptr<PersistStackCompartment> __next_compartment;
    std::vector<PersistStackFrameContext> _context_stack;

    void __kernel(PersistStackFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            PersistStackFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                PersistStackFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    PersistStackFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(PersistStackFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Start") {
            _state_Start(__e);
        } else if (state_name == "Middle") {
            _state_Middle(__e);
        } else if (state_name == "End") {
            _state_End(__e);
        }
    }

    void __transition(std::unique_ptr<PersistStackCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Middle(PersistStackFrameEvent& __e) {
        if (__e._message == "get_depth") {
            _context_stack.back()._return = std::any(this->depth);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("middle"));
            return;;
        } else if (__e._message == "pop_back") {
            this->depth = this->depth - 1;
            auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
        } else if (__e._message == "push_and_go") {
            this->depth = this->depth + 1;
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<PersistStackCompartment>("End");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_Start(PersistStackFrameEvent& __e) {
        if (__e._message == "get_depth") {
            _context_stack.back()._return = std::any(this->depth);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("start"));
            return;;
        } else if (__e._message == "pop_back") {
            // nothing to pop
        } else if (__e._message == "push_and_go") {
            this->depth = this->depth + 1;
            _state_stack.push_back(__compartment->clone());
            auto __new_compartment = std::make_unique<PersistStackCompartment>("Middle");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        }
    }

    void _state_End(PersistStackFrameEvent& __e) {
        if (__e._message == "get_depth") {
            _context_stack.back()._return = std::any(this->depth);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("end"));
            return;;
        } else if (__e._message == "pop_back") {
            this->depth = this->depth - 1;
            auto __popped = std::move(_state_stack.back()); _state_stack.pop_back();
            __transition(std::move(__popped));
            return;
        } else if (__e._message == "push_and_go") {
            // can't go further
        }
    }

public:
    int depth = 0;

    PersistStack() {
        __compartment = std::make_unique<PersistStackCompartment>("Start");
        PersistStackFrameEvent __frame_event("$>");
        PersistStackFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void push_and_go() {
        PersistStackFrameEvent __e("push_and_go");
        PersistStackFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void pop_back() {
        PersistStackFrameEvent __e("pop_back");
        PersistStackFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        PersistStackFrameEvent __e("get_state");
        PersistStackFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    int get_depth() {
        PersistStackFrameEvent __e("get_depth");
        PersistStackFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string save_state() {
        std::function<nlohmann::json(const PersistStackCompartment*)> __ser = [&](const PersistStackCompartment* c) -> nlohmann::json {
            if (!c) return nullptr;
            nlohmann::json __cj;
            __cj["state"] = c->state;
            nlohmann::json __sv;
            for (auto& [k, v] : c->state_vars) {
            }
            __cj["state_vars"] = __sv;
            __cj["parent"] = __ser(c->parent_compartment.get());
            return __cj;
        };
        nlohmann::json __j;
        __j["_compartment"] = __ser(__compartment.get());
        nlohmann::json __stack = nlohmann::json::array();
        for (auto& c : _state_stack) { __stack.push_back(__ser(c.get())); }
        __j["_state_stack"] = __stack;
        __j["depth"] = depth;
        return __j.dump();
    }

    static PersistStack restore_state(const std::string& json) {
        std::function<std::unique_ptr<PersistStackCompartment>(const nlohmann::json&)> __deser = [&](const nlohmann::json& d) -> std::unique_ptr<PersistStackCompartment> {
            if (d.is_null()) return nullptr;
            auto c = std::make_unique<PersistStackCompartment>(std::string(d["state"]));
            if (d.contains("state_vars")) {
                auto& sv = d["state_vars"];
            }
            if (d.contains("parent") && !d["parent"].is_null()) {
                c->parent_compartment = __deser(d["parent"]);
            }
            return c;
        };
        auto __j = nlohmann::json::parse(json);
        PersistStack __instance;
        __instance.__compartment = __deser(__j["_compartment"]);
        if (__j.contains("_state_stack")) {
            for (auto& __sc : __j["_state_stack"]) {
                __instance._state_stack.push_back(__deser(__sc));
            }
        }
        if (__j.contains("depth")) { __j["depth"].get_to(__instance.depth); }
        return __instance;
    }
};

int main() {
    printf("=== Test 25: Persist Stack (C++) ===\n");

    // Test 1: Build up a stack
    PersistStack s1;
    if (s1.get_state() != "start") {
        printf("FAIL: Expected start, got %s\n", s1.get_state().c_str());
        assert(false);
    }

    s1.push_and_go();  // Start -> Middle (push Start)
    if (s1.get_state() != "middle") {
        printf("FAIL: Expected middle, got %s\n", s1.get_state().c_str());
        assert(false);
    }
    if (s1.get_depth() != 1) {
        printf("FAIL: Expected depth 1, got %d\n", s1.get_depth());
        assert(false);
    }

    s1.push_and_go();  // Middle -> End (push Middle)
    if (s1.get_state() != "end") {
        printf("FAIL: Expected end, got %s\n", s1.get_state().c_str());
        assert(false);
    }
    if (s1.get_depth() != 2) {
        printf("FAIL: Expected depth 2, got %d\n", s1.get_depth());
        assert(false);
    }

    printf("1. Built stack: state=%s, depth=%d\n", s1.get_state().c_str(), s1.get_depth());

    // Test 2: Save state (should include stack)
    std::string json = s1.save_state();
    auto data = nlohmann::json::parse(json);
    printf("2. Saved data: %s\n", json.c_str());
    if (data["_compartment"]["state"] != "End") {
        printf("FAIL: Expected End state in saved data\n");
        assert(false);
    }
    if (!data.contains("_state_stack")) {
        printf("FAIL: Expected _state_stack in saved data\n");
        assert(false);
    }
    if (data["_state_stack"].size() != 2) {
        printf("FAIL: Expected 2 items in stack, got %zu\n", data["_state_stack"].size());
        assert(false);
    }

    // Test 3: Restore and verify stack works
    PersistStack s2 = PersistStack::restore_state(json);
    if (s2.get_state() != "end") {
        printf("FAIL: Restored: expected end, got %s\n", s2.get_state().c_str());
        assert(false);
    }
    if (s2.get_depth() != 2) {
        printf("FAIL: Restored: expected depth 2, got %d\n", s2.get_depth());
        assert(false);
    }
    printf("3. Restored: state=%s, depth=%d\n", s2.get_state().c_str(), s2.get_depth());

    // Test 4: Pop should work after restore
    s2.pop_back();  // End -> Middle (pop)
    if (s2.get_state() != "middle") {
        printf("FAIL: After pop: expected middle, got %s\n", s2.get_state().c_str());
        assert(false);
    }
    if (s2.get_depth() != 1) {
        printf("FAIL: After pop: expected depth 1, got %d\n", s2.get_depth());
        assert(false);
    }
    printf("4. After pop: state=%s, depth=%d\n", s2.get_state().c_str(), s2.get_depth());

    // Test 5: Pop again
    s2.pop_back();  // Middle -> Start (pop)
    if (s2.get_state() != "start") {
        printf("FAIL: After 2nd pop: expected start, got %s\n", s2.get_state().c_str());
        assert(false);
    }
    if (s2.get_depth() != 0) {
        printf("FAIL: After 2nd pop: expected depth 0, got %d\n", s2.get_depth());
        assert(false);
    }
    printf("5. After 2nd pop: state=%s, depth=%d\n", s2.get_state().c_str(), s2.get_depth());

    printf("PASS: Persist stack works correctly\n");
    return 0;
}
