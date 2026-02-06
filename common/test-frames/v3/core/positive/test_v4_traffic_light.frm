@@target python

@@system SimpleTrafficLight {
    interface:
        tick()
        getColor(): str
    
    machine:
        $Red {
            tick() {
                -> $Green()
            }
            getColor() {
                system.return = "red"
            }
        }
        
        $Green {
            tick() {
                -> $Yellow()
            }
            getColor() {
                system.return = "green"
            }
        }
        
        $Yellow {
            tick() {
                -> $Red()
            }
            getColor() {
                system.return = "yellow"
            }
        }
    
    domain:
        color = "red"
}

# Test code
def test_traffic_light():
    light = SimpleTrafficLight()
    
    # Should start in Red
    assert light.getColor() == "red", f"Expected red, got {light.getColor()}"
    
    # Tick to Green
    light.tick()
    assert light.getColor() == "green", f"Expected green, got {light.getColor()}"
    
    # Tick to Yellow
    light.tick()
    assert light.getColor() == "yellow", f"Expected yellow, got {light.getColor()}"
    
    # Tick back to Red
    light.tick()
    assert light.getColor() == "red", f"Expected red, got {light.getColor()}"
    
    print("SUCCESS: All traffic light tests passed")

if __name__ == "__main__":
    test_traffic_light()