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

class PersistRoundtripFrameEvent {
public:
    std::string _message;
    std::unordered_map<std::string, std::any> _parameters;

    PersistRoundtripFrameEvent(const std::string& message, std::unordered_map<std::string, std::any> params = {})
        : _message(message), _parameters(std::move(params)) {}
};

class PersistRoundtripFrameContext {
public:
    PersistRoundtripFrameEvent _event;
    std::any _return;
    std::unordered_map<std::string, std::any> _data;

    PersistRoundtripFrameContext(PersistRoundtripFrameEvent event, std::any default_return = {})
        : _event(std::move(event)), _return(std::move(default_return)) {}
};

class PersistRoundtripCompartment {
public:
    std::string state;
    std::unordered_map<std::string, std::any> state_args;
    std::unordered_map<std::string, std::any> state_vars;
    std::unordered_map<std::string, std::any> enter_args;
    std::unordered_map<std::string, std::any> exit_args;
    std::unique_ptr<PersistRoundtripFrameEvent> forward_event;
    std::unique_ptr<PersistRoundtripCompartment> parent_compartment;

    explicit PersistRoundtripCompartment(const std::string& state) : state(state) {}

    std::unique_ptr<PersistRoundtripCompartment> clone() const {
        auto c = std::make_unique<PersistRoundtripCompartment>(state);
        c->state_args = state_args;
        c->state_vars = state_vars;
        c->enter_args = enter_args;
        c->exit_args = exit_args;
        return c;
    }
};

class PersistRoundtrip {
private:
    std::vector<std::unique_ptr<PersistRoundtripCompartment>> _state_stack;
    std::unique_ptr<PersistRoundtripCompartment> __compartment;
    std::unique_ptr<PersistRoundtripCompartment> __next_compartment;
    std::vector<PersistRoundtripFrameContext> _context_stack;

    void __kernel(PersistRoundtripFrameEvent& __e) {
        __router(__e);
        while (__next_compartment) {
            auto next_compartment = std::move(__next_compartment);
            PersistRoundtripFrameEvent exit_event("<$");
            __router(exit_event);
            __compartment = std::move(next_compartment);
            if (!__compartment->forward_event) {
                PersistRoundtripFrameEvent enter_event("$>");
                __router(enter_event);
            } else {
                auto forward_event = std::move(__compartment->forward_event);
                if (forward_event->_message == "$>") {
                    __router(*forward_event);
                } else {
                    PersistRoundtripFrameEvent enter_event("$>");
                    __router(enter_event);
                    __router(*forward_event);
                }
            }
        }
    }

    void __router(PersistRoundtripFrameEvent& __e) {
        const auto& state_name = __compartment->state;
        if (state_name == "Idle") {
            _state_Idle(__e);
        } else if (state_name == "Active") {
            _state_Active(__e);
        }
    }

    void __transition(std::unique_ptr<PersistRoundtripCompartment> next) {
        __next_compartment = std::move(next);
    }

    void _state_Idle(PersistRoundtripFrameEvent& __e) {
        if (__e._message == "add_history") {
            auto msg = std::any_cast<std::string>(__e._parameters.at("msg"));
            this->history = this->history + std::string("idle:") + msg + std::string(",");
        } else if (__e._message == "get_counter") {
            _context_stack.back()._return = std::any(this->counter);
            return;;
        } else if (__e._message == "get_history") {
            _context_stack.back()._return = std::any(this->history);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("idle"));
            return;;
        } else if (__e._message == "go_active") {
            this->history = this->history + "idle->active,";
            auto __new_compartment = std::make_unique<PersistRoundtripCompartment>("Active");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "go_idle") {
            // already idle
        } else if (__e._message == "set_counter") {
            auto n = std::any_cast<int>(__e._parameters.at("n"));
            this->counter = n;
        }
    }

    void _state_Active(PersistRoundtripFrameEvent& __e) {
        if (__e._message == "add_history") {
            auto msg = std::any_cast<std::string>(__e._parameters.at("msg"));
            this->history = this->history + std::string("active:") + msg + std::string(",");
        } else if (__e._message == "get_counter") {
            _context_stack.back()._return = std::any(this->counter);
            return;;
        } else if (__e._message == "get_history") {
            _context_stack.back()._return = std::any(this->history);
            return;;
        } else if (__e._message == "get_state") {
            _context_stack.back()._return = std::any(std::string("active"));
            return;;
        } else if (__e._message == "go_active") {
            // already active
        } else if (__e._message == "go_idle") {
            this->history = this->history + "active->idle,";
            auto __new_compartment = std::make_unique<PersistRoundtripCompartment>("Idle");
            __new_compartment->parent_compartment = __compartment->clone();
            __transition(std::move(__new_compartment));
            return;
        } else if (__e._message == "set_counter") {
            auto n = std::any_cast<int>(__e._parameters.at("n"));
            this->counter = n * 2;
        }
    }

public:
    int counter = 0;
    std::string history = "";
    std::string mode = "normal";

    PersistRoundtrip() {
        __compartment = std::make_unique<PersistRoundtripCompartment>("Idle");
        PersistRoundtripFrameEvent __frame_event("$>");
        PersistRoundtripFrameContext __ctx(std::move(__frame_event));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_active() {
        PersistRoundtripFrameEvent __e("go_active");
        PersistRoundtripFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    void go_idle() {
        PersistRoundtripFrameEvent __e("go_idle");
        PersistRoundtripFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_state() {
        PersistRoundtripFrameEvent __e("get_state");
        PersistRoundtripFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void set_counter(int n) {
        std::unordered_map<std::string, std::any> __params;
        __params["n"] = n;
        PersistRoundtripFrameEvent __e("set_counter", std::move(__params));
        PersistRoundtripFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    int get_counter() {
        PersistRoundtripFrameEvent __e("get_counter");
        PersistRoundtripFrameContext __ctx(std::move(__e), std::any(int()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<int>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    void add_history(std::string msg) {
        std::unordered_map<std::string, std::any> __params;
        __params["msg"] = msg;
        PersistRoundtripFrameEvent __e("add_history", std::move(__params));
        PersistRoundtripFrameContext __ctx(std::move(__e));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        _context_stack.pop_back();
    }

    std::string get_history() {
        PersistRoundtripFrameEvent __e("get_history");
        PersistRoundtripFrameContext __ctx(std::move(__e), std::any(std::string()));
        _context_stack.push_back(std::move(__ctx));
        __kernel(_context_stack.back()._event);
        auto __result = std::any_cast<std::string>(std::move(_context_stack.back()._return));
        _context_stack.pop_back();
        return __result;
    }

    std::string save_state() {
        std::function<nlohmann::json(const PersistRoundtripCompartment*)> __ser = [&](const PersistRoundtripCompartment* c) -> nlohmann::json {
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
        __j["counter"] = counter;
        __j["history"] = history;
        __j["mode"] = mode;
        return __j.dump();
    }

    static PersistRoundtrip restore_state(const std::string& json) {
        std::function<std::unique_ptr<PersistRoundtripCompartment>(const nlohmann::json&)> __deser = [&](const nlohmann::json& d) -> std::unique_ptr<PersistRoundtripCompartment> {
            if (d.is_null()) return nullptr;
            auto c = std::make_unique<PersistRoundtripCompartment>(std::string(d["state"]));
            if (d.contains("state_vars")) {
                auto& sv = d["state_vars"];
            }
            if (d.contains("parent") && !d["parent"].is_null()) {
                c->parent_compartment = __deser(d["parent"]);
            }
            return c;
        };
        auto __j = nlohmann::json::parse(json);
        PersistRoundtrip __instance;
        __instance.__compartment = __deser(__j["_compartment"]);
        if (__j.contains("_state_stack")) {
            for (auto& __sc : __j["_state_stack"]) {
                __instance._state_stack.push_back(__deser(__sc));
            }
        }
        if (__j.contains("counter")) { __j["counter"].get_to(__instance.counter); }
        if (__j.contains("history")) { __j["history"].get_to(__instance.history); }
        if (__j.contains("mode")) { __j["mode"].get_to(__instance.mode); }
        return __instance;
    }
};

int main() {
    printf("=== Test 24: Persist Roundtrip (C++) ===\n");

    // Test 1: Create system and build up state
    PersistRoundtrip s1;
    s1.set_counter(5);
    s1.add_history("start");
    s1.go_active();
    s1.set_counter(3);  // Should be 6 in Active (doubled)
    s1.add_history("work");

    if (s1.get_state() != "active") {
        printf("FAIL: Expected active, got %s\n", s1.get_state().c_str());
        assert(false);
    }
    if (s1.get_counter() != 6) {
        printf("FAIL: Expected 6, got %d\n", s1.get_counter());
        assert(false);
    }
    printf("1. State before save: state=%s, counter=%d\n", s1.get_state().c_str(), s1.get_counter());
    printf("   History: %s\n", s1.get_history().c_str());

    // Test 2: Save state
    std::string json = s1.save_state();
    auto data = nlohmann::json::parse(json);
    printf("2. Saved data keys present\n");
    if (data["_compartment"]["state"] != "Active") {
        printf("FAIL: Expected Active state in save data\n");
        assert(false);
    }
    if (data["counter"] != 6) {
        printf("FAIL: Expected counter=6 in save data\n");
        assert(false);
    }

    // Test 3: Restore to new instance
    PersistRoundtrip s2 = PersistRoundtrip::restore_state(json);

    if (s2.get_state() != "active") {
        printf("FAIL: Expected active, got %s\n", s2.get_state().c_str());
        assert(false);
    }
    if (s2.get_counter() != 6) {
        printf("FAIL: Expected 6, got %d\n", s2.get_counter());
        assert(false);
    }
    printf("3. Restored state: state=%s, counter=%d\n", s2.get_state().c_str(), s2.get_counter());

    // Test 4: State machine continues to work after restore
    s2.set_counter(2);  // Should be 4 in Active (doubled)
    if (s2.get_counter() != 4) {
        printf("FAIL: Expected 4, got %d\n", s2.get_counter());
        assert(false);
    }
    printf("4. Counter after set_counter(2): %d\n", s2.get_counter());

    // Test 5: Verify history was preserved
    if (s2.get_history() != s1.get_history()) {
        printf("FAIL: History mismatch: '%s' vs '%s'\n", s2.get_history().c_str(), s1.get_history().c_str());
        assert(false);
    }
    printf("5. History preserved: %s\n", s2.get_history().c_str());

    // Test 6: Transitions work after restore
    s2.go_idle();
    if (s2.get_state() != "idle") {
        printf("FAIL: Expected idle after go_idle\n");
        assert(false);
    }
    s2.set_counter(10);  // Not doubled in Idle
    if (s2.get_counter() != 10) {
        printf("FAIL: Expected 10, got %d\n", s2.get_counter());
        assert(false);
    }
    printf("6. After go_idle: state=%s, counter=%d\n", s2.get_state().c_str(), s2.get_counter());

    printf("PASS: Persist roundtrip works correctly\n");
    return 0;
}
