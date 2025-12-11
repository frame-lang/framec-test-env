# Test Fixture Migration

**Migrated**: Wed Dec 10 14:30:16 PST 2025
**Source**: /Users/marktruluck/projects/frame_transpiler/framec_tests
**Total Categories**:       36
**Total Fixtures**:       84

## Structure

```
test-frames/
├── v3/                  # V3 architecture tests
│   ├── capabilities/    # System and state capabilities
│   ├── persistence/     # Persistence framework tests
│   ├── imports/         # Import system tests
│   ├── async/           # Async/await tests
│   ├── data_types/      # Data type tests
│   ├── operators/       # Operator tests
│   ├── scoping/         # Scope resolution tests
│   └── systems/         # System-level tests
├── legacy/              # Pre-V3 tests for compatibility
│   ├── control_flow/
│   ├── core/
│   └── regression/
└── common/              # Shared tests across versions
    ├── control_flow/
    ├── core/
    ├── data_types/
    ├── operators/
    ├── regression/
    ├── scoping/
    └── systems/
```

## Test Categories

### V3 Tests
- **capabilities/system_params**: System parameter tests
- **capabilities/system_return**: System return value tests
- **capabilities/state_parameters**: State parameter tests
- **persistence**: State persistence framework
- **imports**: Module import system
- **async**: Async/await functionality
- **data_types**: Type system and data structures
- **operators**: Operator overloading and custom operators
- **scoping**: Scope resolution and visibility
- **systems**: System-level integration

### Common Tests
- **control_flow**: Flow control structures
- **core**: Core language features
- **data_types**: Basic data types
- **operators**: Standard operators
- **regression**: Regression test suite
- **scoping**: Scope tests
- **systems**: System tests
