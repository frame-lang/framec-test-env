@@target python_3

@@system HSMForward {
    interface:
        event_a()
        event_b()
        get_log(): list

    domain:
        var log: list = []

    machine:
        $Child => $Parent {
            event_a() {
                self.log.append("Child:event_a")
            }

            event_b() {
                self.log.append("Child:event_b_forward")
                => $^
            }

            get_log(): list {
                return self.log
            }
        }

        $Parent {
            event_a() {
                self.log.append("Parent:event_a")
            }

            event_b() {
                self.log.append("Parent:event_b")
            }

            get_log(): list {
                return self.log
            }
        }
}

def main():
    print("=== Test 08: HSM Forward ===")
    s = HSMForward()

    # event_a should be handled by Child (no forward)
    s.event_a()
    log = s.get_log()
    assert "Child:event_a" in log, f"Expected 'Child:event_a' in log, got {log}"
    print(f"After event_a: {log}")

    # event_b should forward to Parent
    s.event_b()
    log = s.get_log()
    assert "Child:event_b_forward" in log, f"Expected 'Child:event_b_forward' in log, got {log}"
    assert "Parent:event_b" in log, f"Expected 'Parent:event_b' in log (forwarded), got {log}"
    print(f"After event_b (forwarded): {log}")

    print("PASS: HSM forward works correctly")

if __name__ == '__main__':
    main()
