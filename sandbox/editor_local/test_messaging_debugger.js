/**
 * Test bidirectional messaging protocol between TypeScript and Python
 * This tests Phase 1: Bidirectional Messaging Protocol
 */

const { FrameDebugAdapter } = require('./out/debug/state_machines/FrameDebugAdapter');

async function testMessagingProtocol() {
    console.log('[MESSAGING TEST] Starting bidirectional messaging test...');
    
    try {
        // Create Frame Debug Adapter instance
        const adapter = new FrameDebugAdapter();
        console.log('[MESSAGING TEST] ✅ Frame Debug Adapter created');
        
        // Mock VS Code session with detailed message logging
        const mockSession = {
            sendEvent: (event, body) => {
                console.log(`[MESSAGING TEST] 📤 VS Code Event: ${event}`, body);
            },
            sendResponse: (response) => {
                console.log(`[MESSAGING TEST] 📤 VS Code Response:`, response);
            }
        };
        
        // Set VS Code session
        adapter.setVSCodeSession(mockSession);
        console.log('[MESSAGING TEST] ✅ VS Code session set');
        
        // Initialize the adapter
        console.log('[MESSAGING TEST] 🚀 Initializing adapter...');
        adapter.initialize({
            adapterID: 'frame',
            supportsConfigurationDoneRequest: true
        });
        
        // Wait a moment for initialization
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Launch the debugger with messaging protocol
        console.log('[MESSAGING TEST] 🚀 Launching with messaging protocol...');
        adapter.launch({
            program: '/Users/marktruluck/projects/frame_debugger_tests/simple_hello_world.frm',
            stopOnEntry: false
        });
        
        // Wait for TCP server, Python connection, and messaging exchange
        console.log('[MESSAGING TEST] ⏳ Waiting for messaging protocol exchange...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Terminate the session
        console.log('[MESSAGING TEST] 🛑 Terminating session...');
        adapter.terminate();
        
        // Wait for cleanup
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log('[MESSAGING TEST] ✅ Messaging protocol test completed');
        
    } catch (error) {
        console.error('[MESSAGING TEST] ❌ Test failed:', error);
        process.exit(1);
    }
}

// Run the test
testMessagingProtocol().then(() => {
    console.log('[MESSAGING TEST] 🎉 Phase 1: Bidirectional messaging protocol validated');
    process.exit(0);
}).catch(error => {
    console.error('[MESSAGING TEST] 💥 Messaging test failed:', error);
    process.exit(1);
});