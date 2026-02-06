@@target python

@@system EventProcessor {
    interface:
        processEvent(data: str)
        
    machine:
        $Processing {
            processEvent(data: str) {
                print("Processing: " + data)
                system.return = "processed"
            }
        }
}

@@system EventForwarder {
    interface:
        handleRequest(data: str)
        
    machine:
        $Ready {
            handleRequest(data: str) {
                # Forward event to another system
                var processor = EventProcessor()
                var result = processor.processEvent(data)
                
                # Test forward event syntax (=> operator)
                # => processor.processEvent(data)
                
                print("Forwarded and got result: " + result)
                system.return = result
            }
        }
    
    domain:
        processor = None
}

# Test forward events
var forwarder = EventForwarder()
var result = forwarder.handleRequest("test data")

if result == "processed":
    print("SUCCESS: Event forwarding works")
else:
    print("FAIL: Expected 'processed', got " + str(result))