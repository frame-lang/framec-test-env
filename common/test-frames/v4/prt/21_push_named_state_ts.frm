@@target typescript

@@system PushNamedStateTest {
    interface:
        pushB()
        goToB()
        pop()
        getState(): str

    machine:
        $A {
            pushB() {
                console.log("Pushing B onto stack from A");
                `push$ $B
            }

            goToB() {
                console.log("Transitioning to B");
                -> $B
            }

            pop() {
                console.log("Pop in A - nothing to pop, staying in A");
            }

            getState(): str {
                return "A";
            }
        }

        $B {
            pushB() {
                console.log("Already in B");
            }

            goToB() {
                console.log("Already in B");
            }

            pop() {
                console.log("Popping from B back to previous state");
                `-> pop$
            }

            getState(): str {
                return "B";
            }
        }
}

function main(): void {
    console.log("=== Test 21: Push Named State (TypeScript) ===");
    const s = new PushNamedStateTest();

    // Initial state should be A
    let state = s.getState();
    console.log(`1. Initial state: ${state}`);
    if (state !== "A") throw new Error(`Expected 'A', got '${state}'`);

    // Push B onto the stack (doesn't change state)
    s.pushB();
    state = s.getState();
    console.log(`2. After pushB() - still in: ${state}`);
    if (state !== "A") throw new Error(`Expected 'A' after push (no transition), got '${state}'`);

    // Transition to B
    s.goToB();
    state = s.getState();
    console.log(`3. After goToB() - now in: ${state}`);
    if (state !== "B") throw new Error(`Expected 'B' after transition, got '${state}'`);

    // Pop should restore to B (what we pushed), not A
    s.pop();
    state = s.getState();
    console.log(`4. After pop() - restored to: ${state}`);
    if (state !== "B") throw new Error(`Expected 'B' after pop (pushed state), got '${state}'`);

    console.log("PASS: Push named state with full workflow works correctly");
}

main();
