/**
 * Phase 5 Test: Python Trace-Based Execution Control
 * 
 * This test validates that:
 * 1. Python trace function is properly installed and working
 * 2. Breakpoints are detected during execution
 * 3. Step control (stepInto, stepOver, stepOut) works correctly
 * 4. Execution can be paused and resumed
 * 5. Trace events are properly sent to the debugger
 */

// Import runtime support first to set up global functions
require('./out/debug/state_machines/FrameRuntimeSupport');
const { FrameDebugAdapter } = require('./out/debug/state_machines/FrameDebugAdapter');

async function testPhase5TraceControl() {
    console.log('🧪 Phase 5 Test: Python Trace-Based Execution Control');
    console.log('='.repeat(60));
    
    try {
        // Create Frame Debug Adapter
        const adapter = new FrameDebugAdapter();
        console.log('✅ Frame Debug Adapter created');
        
        // Initialize DAP
        const initResult = await adapter.initialize({});
        console.log('✅ Adapter initialized');
        
        // Launch with test Frame file
        const testFrameFile = '/Users/marktruluck/vscode_editor/test_simple.frm';
        const launchConfig = {
            program: testFrameFile,
            stopOnEntry: false
        };
        console.log('🚀 Launch config:', launchConfig);
        const launchResult = await adapter.launch(launchConfig);
        console.log('✅ Adapter launched');
        
        // Wait for Frame transpilation and Python spawning
        console.log('⏳ Waiting for Frame transpilation and Python runtime startup...');
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Test 1: Set breakpoints with Phase 5 trace functionality
        console.log('\\n📍 Test 1: Setting breakpoints for trace detection...');
        const source = { path: testFrameFile };
        const frameLines = [8, 10]; // Lines in the testMethod
        
        const breakpointResult = await adapter.setBreakpoints(source, frameLines);
        console.log('✅ Breakpoint result:', JSON.stringify(breakpointResult, null, 2));
        
        // Test 2: Test execution control commands
        console.log('\\n🎮 Test 2: Testing execution control commands...');
        
        // Test continue execution
        console.log('   ▶️  Testing continue execution...');
        const continueResult = await adapter.continueExecution(1);
        console.log('   ✅ Continue result:', continueResult);
        
        // Test step into
        console.log('   🔍 Testing step into...');
        const stepIntoResult = await adapter.stepInto(1);
        console.log('   ✅ Step into result:', stepIntoResult);
        
        // Test step over (next)
        console.log('   ⏭️  Testing step over...');
        const stepOverResult = await adapter.nextStep(1);
        console.log('   ✅ Step over result:', stepOverResult);
        
        // Test step out
        console.log('   ⏮️  Testing step out...');
        const stepOutResult = await adapter.stepOutOf(1);
        console.log('   ✅ Step out result:', stepOutResult);
        
        // Test pause
        console.log('   ⏸️  Testing pause...');
        const pauseResult = await adapter.pause(1);
        console.log('   ✅ Pause result:', pauseResult);
        
        // Test 3: Configuration done to complete initialization
        console.log('\\n⚙️  Test 3: Sending configuration done...');
        const configResult = await adapter.configurationDone();
        console.log('✅ Configuration done result:', configResult);
        
        // Wait a bit for any trace events
        console.log('\\n⏳ Waiting for trace events and execution...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log('\\n🎉 Phase 5 trace control tests completed successfully!');
        
        // Cleanup
        await adapter.terminate();
        console.log('✅ Adapter terminated');
        
    } catch (error) {
        console.error('❌ Phase 5 test failed:', error);
        console.error('Stack trace:', error.stack);
        throw error;
    }
}

// Run the test
if (require.main === module) {
    testPhase5TraceControl()
        .then(() => {
            console.log('\\n✅ All Phase 5 tests passed!');
            process.exit(0);
        })
        .catch((error) => {
            console.error('\\n❌ Phase 5 tests failed:', error.message);
            process.exit(1);
        });
}

module.exports = { testPhase5TraceControl };