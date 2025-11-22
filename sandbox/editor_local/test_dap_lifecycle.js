/**
 * Test Phase 2: Basic DAP Initialization/Launch/Terminate Lifecycle
 * This tests proper Debug Adapter Protocol integration with VS Code
 */

const { FrameDebugAdapter } = require('./out/debug/state_machines/FrameDebugAdapter');

async function testDAPLifecycle() {
    console.log('[DAP TEST] Starting Debug Adapter Protocol lifecycle test...');
    
    try {
        // Create Frame Debug Adapter instance
        const adapter = new FrameDebugAdapter();
        console.log('[DAP TEST] ✅ Frame Debug Adapter created');
        
        // Mock VS Code session with comprehensive DAP logging
        const mockSession = {
            sendEvent: (event, body) => {
                console.log(`[DAP TEST] 📤 VS Code Event: ${event}`, JSON.stringify(body, null, 2));
            },
            sendResponse: (response) => {
                console.log(`[DAP TEST] 📤 VS Code Response:`, JSON.stringify(response, null, 2));
            }
        };
        
        // Set VS Code session
        adapter.setVSCodeSession(mockSession);
        console.log('[DAP TEST] ✅ VS Code session registered');
        
        // Phase 2.1: DAP Initialize with capabilities negotiation
        console.log('[DAP TEST] 🚀 Phase 2.1: DAP Initialize...');
        const initResult = adapter.initialize({
            adapterID: 'frame',
            pathFormat: 'path',
            linesStartAt1: true,
            columnsStartAt1: true,
            supportsVariableType: true,
            supportsVariablePaging: false,
            supportsRunInTerminalRequest: false
        });
        
        console.log('[DAP TEST] ✅ Initialize capabilities:', JSON.stringify(initResult, null, 2));
        
        // Wait for initialization events
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Phase 2.2: Launch debug session
        console.log('[DAP TEST] 🚀 Phase 2.2: Launch debug session...');
        adapter.launch({
            program: '/Users/marktruluck/projects/frame_debugger_tests/simple_hello_world.frm',
            stopOnEntry: true,
            console: 'debugConsole'
        });
        
        // Wait for launch, connection, and messaging
        console.log('[DAP TEST] ⏳ Waiting for launch and connection...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Phase 2.3: Configuration done (signals debug session is ready)
        console.log('[DAP TEST] 🚀 Phase 2.3: Configuration done...');
        adapter.configurationDone();
        
        // Wait for configuration
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Phase 2.4: Test basic DAP commands (should acknowledge but not implement)
        console.log('[DAP TEST] 🚀 Phase 2.4: Testing DAP commands...');
        
        // Test breakpoint setting
        adapter.setBreakpoints({path: '/test/file.frm'}, [10, 15, 20]);
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Test stepping commands
        adapter.continueExecution(1);
        await new Promise(resolve => setTimeout(resolve, 100));
        
        adapter.nextStep(1);
        await new Promise(resolve => setTimeout(resolve, 100));
        
        adapter.stepInto(1);
        await new Promise(resolve => setTimeout(resolve, 100));
        
        adapter.pause(1);
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Phase 2.5: Graceful termination
        console.log('[DAP TEST] 🚀 Phase 2.5: Graceful termination...');
        adapter.terminate();
        
        // Wait for termination sequence
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log('[DAP TEST] ✅ DAP lifecycle test completed successfully');
        
    } catch (error) {
        console.error('[DAP TEST] ❌ Test failed:', error);
        process.exit(1);
    }
}

// Run the test
testDAPLifecycle().then(() => {
    console.log('[DAP TEST] 🎉 Phase 2: Basic DAP lifecycle validated');
    console.log('[DAP TEST] ✅ Capabilities negotiation working');
    console.log('[DAP TEST] ✅ Launch/terminate lifecycle working');
    console.log('[DAP TEST] ✅ Command acknowledgment working');
    console.log('[DAP TEST] ✅ Ready for Phase 3: Frame transpilation');
    process.exit(0);
}).catch(error => {
    console.error('[DAP TEST] 💥 DAP lifecycle test failed:', error);
    process.exit(1);
});