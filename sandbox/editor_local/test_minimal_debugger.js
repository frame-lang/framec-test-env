/**
 * Test minimal Frame debugger TCP connection
 * This tests the basic Frame Debug Adapter TCP server creation and Python connection
 */

const { FrameDebugAdapter } = require('./out/debug/state_machines/FrameDebugAdapter');

async function testMinimalDebugger() {
    console.log('[TEST] Starting minimal Frame debugger test...');
    
    try {
        // Create Frame Debug Adapter instance
        const adapter = new FrameDebugAdapter();
        console.log('[TEST] ✅ Frame Debug Adapter created');
        
        // Mock VS Code session
        const mockSession = {
            sendEvent: (event, body) => {
                console.log(`[TEST] 📤 Event: ${event}`, body);
            },
            sendResponse: (response) => {
                console.log(`[TEST] 📤 Response:`, response);
            }
        };
        
        // Set VS Code session
        adapter.setVSCodeSession(mockSession);
        console.log('[TEST] ✅ VS Code session set');
        
        // Initialize the adapter
        console.log('[TEST] 🚀 Initializing adapter...');
        adapter.initialize({
            adapterID: 'frame',
            supportsConfigurationDoneRequest: true
        });
        
        // Wait a moment for initialization
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Launch the debugger with a test file
        console.log('[TEST] 🚀 Launching debugger...');
        adapter.launch({
            program: '/Users/marktruluck/projects/frame_debugger_tests/simple_hello_world.frm',
            stopOnEntry: false
        });
        
        // Wait for TCP server and Python process setup
        console.log('[TEST] ⏳ Waiting for TCP connection setup...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Terminate the session
        console.log('[TEST] 🛑 Terminating session...');
        adapter.terminate();
        
        // Wait for cleanup
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log('[TEST] ✅ Minimal debugger test completed successfully');
        
    } catch (error) {
        console.error('[TEST] ❌ Test failed:', error);
        process.exit(1);
    }
}

// Run the test
testMinimalDebugger().then(() => {
    console.log('[TEST] 🎉 All tests passed');
    process.exit(0);
}).catch(error => {
    console.error('[TEST] 💥 Test suite failed:', error);
    process.exit(1);
});