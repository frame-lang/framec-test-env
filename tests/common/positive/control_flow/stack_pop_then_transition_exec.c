
#include <stdio.h>
#include <stdbool.h>

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// ============================================================================
// S_FrameDict - String-keyed dictionary
// ============================================================================

typedef struct S_FrameDictEntry {
    char* key;
    void* value;
    struct S_FrameDictEntry* next;
} S_FrameDictEntry;

typedef struct {
    S_FrameDictEntry** buckets;
    int bucket_count;
    int size;
} S_FrameDict;

static unsigned int S_hash_string(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

static S_FrameDict* S_FrameDict_new(void) {
    S_FrameDict* d = malloc(sizeof(S_FrameDict));
    d->bucket_count = 16;
    d->buckets = calloc(d->bucket_count, sizeof(S_FrameDictEntry*));
    d->size = 0;
    return d;
}

static void S_FrameDict_set(S_FrameDict* d, const char* key, void* value) {
    unsigned int idx = S_hash_string(key) % d->bucket_count;
    S_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            entry->value = value;
            return;
        }
        entry = entry->next;
    }
    S_FrameDictEntry* new_entry = malloc(sizeof(S_FrameDictEntry));
    new_entry->key = strdup(key);
    new_entry->value = value;
    new_entry->next = d->buckets[idx];
    d->buckets[idx] = new_entry;
    d->size++;
}

static void* S_FrameDict_get(S_FrameDict* d, const char* key) {
    unsigned int idx = S_hash_string(key) % d->bucket_count;
    S_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return entry->value;
        }
        entry = entry->next;
    }
    return NULL;
}

static int S_FrameDict_has(S_FrameDict* d, const char* key) {
    unsigned int idx = S_hash_string(key) % d->bucket_count;
    S_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return 1;
        }
        entry = entry->next;
    }
    return 0;
}

static S_FrameDict* S_FrameDict_copy(S_FrameDict* src) {
    S_FrameDict* dst = S_FrameDict_new();
    for (int i = 0; i < src->bucket_count; i++) {
        S_FrameDictEntry* entry = src->buckets[i];
        while (entry) {
            S_FrameDict_set(dst, entry->key, entry->value);
            entry = entry->next;
        }
    }
    return dst;
}

static void S_FrameDict_destroy(S_FrameDict* d) {
    for (int i = 0; i < d->bucket_count; i++) {
        S_FrameDictEntry* entry = d->buckets[i];
        while (entry) {
            S_FrameDictEntry* next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    free(d->buckets);
    free(d);
}

// ============================================================================
// S_FrameVec - Dynamic array
// ============================================================================

typedef struct {
    void** items;
    int size;
    int capacity;
} S_FrameVec;

static S_FrameVec* S_FrameVec_new(void) {
    S_FrameVec* v = malloc(sizeof(S_FrameVec));
    v->capacity = 8;
    v->size = 0;
    v->items = malloc(sizeof(void*) * v->capacity);
    return v;
}

static void S_FrameVec_push(S_FrameVec* v, void* item) {
    if (v->size >= v->capacity) {
        v->capacity *= 2;
        v->items = realloc(v->items, sizeof(void*) * v->capacity);
    }
    v->items[v->size++] = item;
}

static void* S_FrameVec_pop(S_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[--v->size];
}

static void* S_FrameVec_last(S_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[v->size - 1];
}

static void* S_FrameVec_get(S_FrameVec* v, int index) {
    if (index < 0 || index >= v->size) return NULL;
    return v->items[index];
}

static int S_FrameVec_size(S_FrameVec* v) {
    return v->size;
}

static void S_FrameVec_destroy(S_FrameVec* v) {
    free(v->items);
    free(v);
}

// ============================================================================
// S_FrameEvent - Event routing object
// ============================================================================

typedef struct {
    const char* _message;
    S_FrameDict* _parameters;
} S_FrameEvent;

static S_FrameEvent* S_FrameEvent_new(const char* message, S_FrameDict* parameters) {
    S_FrameEvent* e = malloc(sizeof(S_FrameEvent));
    e->_message = message;
    e->_parameters = parameters;
    return e;
}

static void S_FrameEvent_destroy(S_FrameEvent* e) {
    // Note: _parameters ownership depends on context
    free(e);
}

// ============================================================================
// S_FrameContext - Interface call context
// ============================================================================

typedef struct {
    S_FrameEvent* event;
    void* _return;
    S_FrameDict* _data;
} S_FrameContext;

static S_FrameContext* S_FrameContext_new(S_FrameEvent* event, void* default_return) {
    S_FrameContext* ctx = malloc(sizeof(S_FrameContext));
    ctx->event = event;
    ctx->_return = default_return;
    ctx->_data = S_FrameDict_new();
    return ctx;
}

static void S_FrameContext_destroy(S_FrameContext* ctx) {
    S_FrameDict_destroy(ctx->_data);
    free(ctx);
}

// ============================================================================
// S_Compartment - State closure
// ============================================================================

typedef struct S_Compartment {
    const char* state;
    S_FrameDict* state_args;
    S_FrameDict* state_vars;
    S_FrameDict* enter_args;
    S_FrameDict* exit_args;
    S_FrameEvent* forward_event;
    struct S_Compartment* parent_compartment;
} S_Compartment;

static S_Compartment* S_Compartment_new(const char* state) {
    S_Compartment* c = malloc(sizeof(S_Compartment));
    c->state = state;
    c->state_args = S_FrameDict_new();
    c->state_vars = S_FrameDict_new();
    c->enter_args = S_FrameDict_new();
    c->exit_args = S_FrameDict_new();
    c->forward_event = NULL;
    c->parent_compartment = NULL;
    return c;
}

static S_Compartment* S_Compartment_copy(S_Compartment* src) {
    S_Compartment* c = malloc(sizeof(S_Compartment));
    c->state = src->state;
    c->state_args = S_FrameDict_copy(src->state_args);
    c->state_vars = S_FrameDict_copy(src->state_vars);
    c->enter_args = S_FrameDict_copy(src->enter_args);
    c->exit_args = S_FrameDict_copy(src->exit_args);
    c->forward_event = src->forward_event;  // Shallow copy OK
    c->parent_compartment = src->parent_compartment;
    return c;
}

static void S_Compartment_destroy(S_Compartment* c) {
    S_FrameDict_destroy(c->state_args);
    S_FrameDict_destroy(c->state_vars);
    S_FrameDict_destroy(c->enter_args);
    S_FrameDict_destroy(c->exit_args);
    free(c);
}

// Helper macros for context access
#define S_CTX(self) ((S_FrameContext*)S_FrameVec_last((self)->_context_stack))
#define S_PARAM(self, key) S_FrameDict_get(S_CTX(self)->event->_parameters, key)
#define S_RETURN(self) S_CTX(self)->_return
#define S_DATA(self, key) S_FrameDict_get(S_CTX(self)->_data, key)
#define S_DATA_SET(self, key, val) S_FrameDict_set(S_CTX(self)->_data, key, val)

// Forward declarations
typedef struct S S;
static void S_kernel(S* self, S_FrameEvent* __e);
static void S_router(S* self, S_FrameEvent* __e);
static void S_transition(S* self, S_Compartment* next);
static void S_state_A(S* self, S_FrameEvent* __e);
static void S_state_B(S* self, S_FrameEvent* __e);
void S_e (S* self);

struct S {
    S_FrameVec* _state_stack;
    S_Compartment* __compartment;
    S_Compartment* __next_compartment;
    S_FrameVec* _context_stack;
};

S* S_new(void) {
    S* self = malloc(sizeof(S));
    self->_state_stack = S_FrameVec_new();
    self->_context_stack = S_FrameVec_new();
    self->__compartment = S_Compartment_new("A");
    self->__next_compartment = NULL;
    S_FrameEvent* __frame_event = S_FrameEvent_new("$>", NULL);
    S_kernel(self, __frame_event);
    S_FrameEvent_destroy(__frame_event);
    return self;
}

static void S_kernel(S* self, S_FrameEvent* __e) {
    // Route event to current state
    S_router(self, __e);
    // Process any pending transition
    while (self->__next_compartment != NULL) {
        S_Compartment* next_compartment = self->__next_compartment;
        self->__next_compartment = NULL;
        // Exit current state (with exit_args from current compartment)
        S_FrameEvent* exit_event = S_FrameEvent_new("<$", self->__compartment->exit_args);
        S_router(self, exit_event);
        S_FrameEvent_destroy(exit_event);
        // Switch to new compartment
        S_Compartment_destroy(self->__compartment);
        self->__compartment = next_compartment;
        // Enter new state (or forward event)
        if (next_compartment->forward_event == NULL) {
            S_FrameEvent* enter_event = S_FrameEvent_new("$>", self->__compartment->enter_args);
            S_router(self, enter_event);
            S_FrameEvent_destroy(enter_event);
        } else {
            // Forward event to new state
            // Note: forward_event is a borrowed pointer to the caller's __e, do NOT destroy it
            S_FrameEvent* forward_event = next_compartment->forward_event;
            next_compartment->forward_event = NULL;
            if (strcmp(forward_event->_message, "$>") == 0) {
                // Forwarding enter event - just send it
                S_router(self, forward_event);
            } else {
                // Forwarding other event - send $> first, then forward
                S_FrameEvent* enter_event = S_FrameEvent_new("$>", self->__compartment->enter_args);
                S_router(self, enter_event);
                S_FrameEvent_destroy(enter_event);
                S_router(self, forward_event);
            }
            // Do NOT destroy forward_event - it's owned by the interface method caller
        }
    }
}

static void S_router(S* self, S_FrameEvent* __e) {
    const char* state_name = self->__compartment->state;
    if (strcmp(state_name, "A") == 0) {
        S_state_A(self, __e);
    } else if (strcmp(state_name, "B") == 0) {
        S_state_B(self, __e);
    }
}

static void S_transition(S* self, S_Compartment* next_compartment) {
    self->__next_compartment = next_compartment;
}

void S_destroy(S* self) {
    if (self->__compartment) S_Compartment_destroy(self->__compartment);
    if (self->_state_stack) S_FrameVec_destroy(self->_state_stack);
    if (self->_context_stack) S_FrameVec_destroy(self->_context_stack);
    free(self);
}

void S_e(S* self) {
    S_FrameEvent* __e = S_FrameEvent_new("e", NULL);
    S_FrameContext* __ctx = S_FrameContext_new(__e, NULL);
    S_FrameVec_push(self->_context_stack, __ctx);
    S_kernel(self, __e);
    S_FrameContext* __result_ctx = (S_FrameContext*)S_FrameVec_pop(self->_context_stack);
    S_FrameContext_destroy(__result_ctx);
    S_FrameEvent_destroy(__e);
}

static void S_state_A(S* self, S_FrameEvent* __e) {
    if (strcmp(__e->_message, "e") == 0) {
        S_transition(self, (S_Compartment*)S_FrameVec_pop(self->_state_stack));
        return;
        S_Compartment* __compartment = S_Compartment_new("B");
        S_transition(self, __compartment);
        return;
    }
}

static void S_state_B(S* self, S_FrameEvent* __e) {
}


// Stub functions for placeholder calls
void native(void) {}
void x(void) {}

// TAP test harness
int main(void) {
    printf("TAP version 14\n");
    printf("1..1\n");
    S* s = S_new();
    S_e(s);
    printf("ok 1 - stack_pop_then_transition_exec\n");
    S_destroy(s);
    return 0;
}

