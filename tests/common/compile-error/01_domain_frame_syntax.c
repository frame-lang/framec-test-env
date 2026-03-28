
// NEGATIVE TEST: Domain uses Frame syntax (var) which is invalid in C
// Expected: Compile error in generated C code

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// ============================================================================
// NegativeTest_FrameDict - String-keyed dictionary
// ============================================================================

typedef struct NegativeTest_FrameDictEntry {
    char* key;
    void* value;
    struct NegativeTest_FrameDictEntry* next;
} NegativeTest_FrameDictEntry;

typedef struct {
    NegativeTest_FrameDictEntry** buckets;
    int bucket_count;
    int size;
} NegativeTest_FrameDict;

static unsigned int NegativeTest_hash_string(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

static NegativeTest_FrameDict* NegativeTest_FrameDict_new(void) {
    NegativeTest_FrameDict* d = malloc(sizeof(NegativeTest_FrameDict));
    d->bucket_count = 16;
    d->buckets = calloc(d->bucket_count, sizeof(NegativeTest_FrameDictEntry*));
    d->size = 0;
    return d;
}

static void NegativeTest_FrameDict_set(NegativeTest_FrameDict* d, const char* key, void* value) {
    unsigned int idx = NegativeTest_hash_string(key) % d->bucket_count;
    NegativeTest_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            entry->value = value;
            return;
        }
        entry = entry->next;
    }
    NegativeTest_FrameDictEntry* new_entry = malloc(sizeof(NegativeTest_FrameDictEntry));
    new_entry->key = strdup(key);
    new_entry->value = value;
    new_entry->next = d->buckets[idx];
    d->buckets[idx] = new_entry;
    d->size++;
}

static void* NegativeTest_FrameDict_get(NegativeTest_FrameDict* d, const char* key) {
    unsigned int idx = NegativeTest_hash_string(key) % d->bucket_count;
    NegativeTest_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return entry->value;
        }
        entry = entry->next;
    }
    return NULL;
}

static int NegativeTest_FrameDict_has(NegativeTest_FrameDict* d, const char* key) {
    unsigned int idx = NegativeTest_hash_string(key) % d->bucket_count;
    NegativeTest_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return 1;
        }
        entry = entry->next;
    }
    return 0;
}

static NegativeTest_FrameDict* NegativeTest_FrameDict_copy(NegativeTest_FrameDict* src) {
    NegativeTest_FrameDict* dst = NegativeTest_FrameDict_new();
    for (int i = 0; i < src->bucket_count; i++) {
        NegativeTest_FrameDictEntry* entry = src->buckets[i];
        while (entry) {
            NegativeTest_FrameDict_set(dst, entry->key, entry->value);
            entry = entry->next;
        }
    }
    return dst;
}

static void NegativeTest_FrameDict_destroy(NegativeTest_FrameDict* d) {
    for (int i = 0; i < d->bucket_count; i++) {
        NegativeTest_FrameDictEntry* entry = d->buckets[i];
        while (entry) {
            NegativeTest_FrameDictEntry* next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    free(d->buckets);
    free(d);
}

// ============================================================================
// NegativeTest_FrameVec - Dynamic array
// ============================================================================

typedef struct {
    void** items;
    int size;
    int capacity;
} NegativeTest_FrameVec;

static NegativeTest_FrameVec* NegativeTest_FrameVec_new(void) {
    NegativeTest_FrameVec* v = malloc(sizeof(NegativeTest_FrameVec));
    v->capacity = 8;
    v->size = 0;
    v->items = malloc(sizeof(void*) * v->capacity);
    return v;
}

static void NegativeTest_FrameVec_push(NegativeTest_FrameVec* v, void* item) {
    if (v->size >= v->capacity) {
        v->capacity *= 2;
        v->items = realloc(v->items, sizeof(void*) * v->capacity);
    }
    v->items[v->size++] = item;
}

static void* NegativeTest_FrameVec_pop(NegativeTest_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[--v->size];
}

static void* NegativeTest_FrameVec_last(NegativeTest_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[v->size - 1];
}

static void* NegativeTest_FrameVec_get(NegativeTest_FrameVec* v, int index) {
    if (index < 0 || index >= v->size) return NULL;
    return v->items[index];
}

static int NegativeTest_FrameVec_size(NegativeTest_FrameVec* v) {
    return v->size;
}

static void NegativeTest_FrameVec_destroy(NegativeTest_FrameVec* v) {
    free(v->items);
    free(v);
}

// ============================================================================
// NegativeTest_FrameEvent - Event routing object
// ============================================================================

typedef struct {
    const char* _message;
    NegativeTest_FrameDict* _parameters;
} NegativeTest_FrameEvent;

static NegativeTest_FrameEvent* NegativeTest_FrameEvent_new(const char* message, NegativeTest_FrameDict* parameters) {
    NegativeTest_FrameEvent* e = malloc(sizeof(NegativeTest_FrameEvent));
    e->_message = message;
    e->_parameters = parameters;
    return e;
}

static void NegativeTest_FrameEvent_destroy(NegativeTest_FrameEvent* e) {
    // Note: _parameters ownership depends on context
    free(e);
}

// ============================================================================
// NegativeTest_FrameContext - Interface call context
// ============================================================================

typedef struct {
    NegativeTest_FrameEvent* event;
    void* _return;
    NegativeTest_FrameDict* _data;
} NegativeTest_FrameContext;

static NegativeTest_FrameContext* NegativeTest_FrameContext_new(NegativeTest_FrameEvent* event, void* default_return) {
    NegativeTest_FrameContext* ctx = malloc(sizeof(NegativeTest_FrameContext));
    ctx->event = event;
    ctx->_return = default_return;
    ctx->_data = NegativeTest_FrameDict_new();
    return ctx;
}

static void NegativeTest_FrameContext_destroy(NegativeTest_FrameContext* ctx) {
    NegativeTest_FrameDict_destroy(ctx->_data);
    free(ctx);
}

// ============================================================================
// NegativeTest_Compartment - State closure
// ============================================================================

typedef struct NegativeTest_Compartment {
    const char* state;
    NegativeTest_FrameDict* state_args;
    NegativeTest_FrameDict* state_vars;
    NegativeTest_FrameDict* enter_args;
    NegativeTest_FrameDict* exit_args;
    NegativeTest_FrameEvent* forward_event;
    struct NegativeTest_Compartment* parent_compartment;
} NegativeTest_Compartment;

static NegativeTest_Compartment* NegativeTest_Compartment_new(const char* state) {
    NegativeTest_Compartment* c = malloc(sizeof(NegativeTest_Compartment));
    c->state = state;
    c->state_args = NegativeTest_FrameDict_new();
    c->state_vars = NegativeTest_FrameDict_new();
    c->enter_args = NegativeTest_FrameDict_new();
    c->exit_args = NegativeTest_FrameDict_new();
    c->forward_event = NULL;
    c->parent_compartment = NULL;
    return c;
}

static NegativeTest_Compartment* NegativeTest_Compartment_copy(NegativeTest_Compartment* src) {
    NegativeTest_Compartment* c = malloc(sizeof(NegativeTest_Compartment));
    c->state = src->state;
    c->state_args = NegativeTest_FrameDict_copy(src->state_args);
    c->state_vars = NegativeTest_FrameDict_copy(src->state_vars);
    c->enter_args = NegativeTest_FrameDict_copy(src->enter_args);
    c->exit_args = NegativeTest_FrameDict_copy(src->exit_args);
    c->forward_event = src->forward_event;  // Shallow copy OK
    c->parent_compartment = src->parent_compartment;
    return c;
}

static void NegativeTest_Compartment_destroy(NegativeTest_Compartment* c) {
    NegativeTest_FrameDict_destroy(c->state_args);
    NegativeTest_FrameDict_destroy(c->state_vars);
    NegativeTest_FrameDict_destroy(c->enter_args);
    NegativeTest_FrameDict_destroy(c->exit_args);
    free(c);
}

// Helper macros for context access
#define NegativeTest_CTX(self) ((NegativeTest_FrameContext*)NegativeTest_FrameVec_last((self)->_context_stack))
#define NegativeTest_PARAM(self, key) NegativeTest_FrameDict_get(NegativeTest_CTX(self)->event->_parameters, key)
#define NegativeTest_RETURN(self) NegativeTest_CTX(self)->_return
#define NegativeTest_DATA(self, key) NegativeTest_FrameDict_get(NegativeTest_CTX(self)->_data, key)
#define NegativeTest_DATA_SET(self, key, val) NegativeTest_FrameDict_set(NegativeTest_CTX(self)->_data, key, val)

// Forward declarations
typedef struct NegativeTest NegativeTest;
static void NegativeTest_kernel(NegativeTest* self, NegativeTest_FrameEvent* __e);
static void NegativeTest_router(NegativeTest* self, NegativeTest_FrameEvent* __e);
static void NegativeTest_transition(NegativeTest* self, NegativeTest_Compartment* next);
static void NegativeTest_state_Ready(NegativeTest* self, NegativeTest_FrameEvent* __e);

struct NegativeTest {
    NegativeTest_FrameVec* _state_stack;
    NegativeTest_Compartment* __compartment;
    NegativeTest_Compartment* __next_compartment;
    NegativeTest_FrameVec* _context_stack;
    var var;
};

NegativeTest* NegativeTest_new(void) {
    NegativeTest* self = malloc(sizeof(NegativeTest));
    self->_state_stack = NegativeTest_FrameVec_new();
    self->_context_stack = NegativeTest_FrameVec_new();
    self->__compartment = NegativeTest_Compartment_new("Ready");
    self->__next_compartment = NULL;
NegativeTest_FrameEvent* __frame_event = NegativeTest_FrameEvent_new("$>", NULL);
NegativeTest_kernel(self, __frame_event);
NegativeTest_FrameEvent_destroy(__frame_event);
    return self;
}

static void NegativeTest_kernel(NegativeTest* self, NegativeTest_FrameEvent* __e) {
// Route event to current state
NegativeTest_router(self, __e);
// Process any pending transition
while (self->__next_compartment != NULL) {
    NegativeTest_Compartment* next_compartment = self->__next_compartment;
    self->__next_compartment = NULL;
    // Exit current state (with exit_args from current compartment)
    NegativeTest_FrameEvent* exit_event = NegativeTest_FrameEvent_new("<$", self->__compartment->exit_args);
    NegativeTest_router(self, exit_event);
    NegativeTest_FrameEvent_destroy(exit_event);
    // Switch to new compartment
    NegativeTest_Compartment_destroy(self->__compartment);
    self->__compartment = next_compartment;
    // Enter new state (or forward event)
    if (next_compartment->forward_event == NULL) {
        NegativeTest_FrameEvent* enter_event = NegativeTest_FrameEvent_new("$>", self->__compartment->enter_args);
        NegativeTest_router(self, enter_event);
        NegativeTest_FrameEvent_destroy(enter_event);
    } else {
        // Forward event to new state
        // Note: forward_event is a borrowed pointer to the caller's __e, do NOT destroy it
        NegativeTest_FrameEvent* forward_event = next_compartment->forward_event;
        next_compartment->forward_event = NULL;
        if (strcmp(forward_event->_message, "$>") == 0) {
            // Forwarding enter event - just send it
            NegativeTest_router(self, forward_event);
        } else {
            // Forwarding other event - send $> first, then forward
            NegativeTest_FrameEvent* enter_event = NegativeTest_FrameEvent_new("$>", self->__compartment->enter_args);
            NegativeTest_router(self, enter_event);
            NegativeTest_FrameEvent_destroy(enter_event);
            NegativeTest_router(self, forward_event);
        }
        // Do NOT destroy forward_event - it's owned by the interface method caller
    }
}
}

static void NegativeTest_router(NegativeTest* self, NegativeTest_FrameEvent* __e) {
const char* state_name = self->__compartment->state;
if (strcmp(state_name, "Ready") == 0) {
    NegativeTest_state_Ready(self, __e);
}
}

static void NegativeTest_transition(NegativeTest* self, NegativeTest_Compartment* next_compartment) {
self->__next_compartment = next_compartment;
}

void NegativeTest_destroy(NegativeTest* self) {
if (self->__compartment) NegativeTest_Compartment_destroy(self->__compartment);
if (self->_state_stack) NegativeTest_FrameVec_destroy(self->_state_stack);
if (self->_context_stack) NegativeTest_FrameVec_destroy(self->_context_stack);
free(self);
}

static void NegativeTest_state_Ready(NegativeTest* self, NegativeTest_FrameEvent* __e) {
}


int main() { return 0; }

