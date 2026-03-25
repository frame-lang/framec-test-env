#include <string>
#include <unordered_map>
#include <vector>
#include <any>
#include <memory>

// @@skip
// Persist tests require JSON serialization library (e.g., nlohmann/json)
// which is not available in the standard C++17 test environment.


#include <iostream>
#include <string>
#include <cassert>

int main() {
    printf("SKIP: Persist basic requires JSON library\n");
    return 0;
}
