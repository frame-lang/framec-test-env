
#include <stdio.h>
#include <stdint.h>

// Mealy Machine - output depends on state AND input (output on transitions)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// ============================================================================
// MealyMachine_FrameDict - String-keyed dictionary
// ============================================================================

typedef struct MealyMachine_FrameDictEntry {
    char* key;
    void* value;
    struct MealyMachine_FrameDictEntry* next;
} MealyMachine_FrameDictEntry;

typedef struct {
    MealyMachine_FrameDictEntry** buckets;
    int bucket_count;
    int size;
} MealyMachine_FrameDict;

static unsigned int MealyMachine_hash_string(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

static MealyMachine_FrameDict* MealyMachine_FrameDict_new(void) {
    MealyMachine_FrameDict* d = malloc(sizeof(MealyMachine_FrameDict));
    d->bucket_count = 16;
    d->buckets = calloc(d->bucket_count, sizeof(MealyMachine_FrameDictEntry*));
    d->size = 0;
    return d;
}

static void MealyMachine_FrameDict_set(MealyMachine_FrameDict* d, const char* key, void* value) {
    unsigned int idx = MealyMachine_hash_string(key) % d->bucket_count;
    MealyMachine_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            entry->value = value;
            return;
        }
        entry = entry->next;
    }
    MealyMachine_FrameDictEntry* new_entry = malloc(sizeof(MealyMachine_FrameDictEntry));
    new_entry->key = strdup(key);
    new_entry->value = value;
    new_entry->next = d->buckets[idx];
    d->buckets[idx] = new_entry;
    d->size++;
}

static void* MealyMachine_FrameDict_get(MealyMachine_FrameDict* d, const char* key) {
    unsigned int idx = MealyMachine_hash_string(key) % d->bucket_count;
    MealyMachine_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return entry->value;
        }
        entry = entry->next;
    }
    return NULL;
}

static int MealyMachine_FrameDict_has(MealyMachine_FrameDict* d, const char* key) {
    unsigned int idx = MealyMachine_hash_string(key) % d->bucket_count;
    MealyMachine_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return 1;
        }
        entry = entry->next;
    }
    return 0;
}

static MealyMachine_FrameDict* MealyMachine_FrameDict_copy(MealyMachine_FrameDict* src) {
    MealyMachine_FrameDict* dst = MealyMachine_FrameDict_new();
    for (int i = 0; i < src->bucket_count; i++) {
        MealyMachine_FrameDictEntry* entry = src->buckets[i];
        while (entry) {
            MealyMachine_FrameDict_set(dst, entry->key, entry->value);
            entry = entry->next;
        }
    }
    return dst;
}

static void MealyMachine_FrameDict_destroy(MealyMachine_FrameDict* d) {
    for (int i = 0; i < d->bucket_count; i++) {
        MealyMachine_FrameDictEntry* entry = d->buckets[i];
        while (entry) {
            MealyMachine_FrameDictEntry* next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    free(d->buckets);
    free(d);
}

// ============================================================================
// MealyMachine_FrameVec - Dynamic array
// ============================================================================

typedef struct {
    void** items;
    int size;
    int capacity;
} MealyMachine_FrameVec;

static MealyMachine_FrameVec* MealyMachine_FrameVec_new(void) {
    MealyMachine_FrameVec* v = malloc(sizeof(MealyMachine_FrameVec));
    v->capacity = 8;
    v->size = 0;
    v->items = malloc(sizeof(void*) * v->capacity);
    return v;
}

static void MealyMachine_FrameVec_push(MealyMachine_FrameVec* v, void* item) {
    if (v->size >= v->capacity) {
        v->capacity *= 2;
        v->items = realloc(v->items, sizeof(void*) * v->capacity);
    }
    v->items[v->size++] = item;
}

static void* MealyMachine_FrameVec_pop(MealyMachine_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[--v->size];
}

static void* MealyMachine_FrameVec_last(MealyMachine_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[v->size - 1];
}

static void* MealyMachine_FrameVec_get(MealyMachine_FrameVec* v, int index) {
    if (index < 0 || index >= v->size) return NULL;
    return v->items[index];
}

static int MealyMachine_FrameVec_size(MealyMachine_FrameVec* v) {
    return v->size;
}

static void MealyMachine_FrameVec_destroy(MealyMachine_FrameVec* v) {
    free(v->items);
    free(v);
}

// ============================================================================
// MealyMachine_FrameEvent - Event routing object
// ============================================================================

typedef struct {
    const char* _message;
    MealyMachine_FrameDict* _parameters;
} MealyMachine_FrameEvent;

static MealyMachine_FrameEvent* MealyMachine_FrameEvent_new(const char* message, MealyMachine_FrameDict* parameters) {
    MealyMachine_FrameEvent* e = malloc(sizeof(MealyMachine_FrameEvent));
    e->_message = message;
    e->_parameters = parameters;
    return e;
}

static void MealyMachine_FrameEvent_destroy(MealyMachine_FrameEvent* e) {
    // Note: _parameters ownership depends on context
    free(e);
}

// ============================================================================
// MealyMachine_FrameContext - Interface call context
// ============================================================================

typedef struct {
    MealyMachine_FrameEvent* event;
    void* _return;
    MealyMachine_FrameDict* _data;
} MealyMachine_FrameContext;

static MealyMachine_FrameContext* MealyMachine_FrameContext_new(MealyMachine_FrameEvent* event, void* default_return) {
    MealyMachine_FrameContext* ctx = malloc(sizeof(MealyMachine_FrameContext));
    ctx->event = event;
    ctx->_return = default_return;
    ctx->_data = MealyMachine_FrameDict_new();
    return ctx;
}

static void MealyMachine_FrameContext_destroy(MealyMachine_FrameContext* ctx) {
    MealyMachine_FrameDict_destroy(ctx->_data);
    free(ctx);
}

// ============================================================================
// MealyMachine_Compartment - State closure
// ============================================================================

typedef struct MealyMachine_Compartment {
    const char* state;
    MealyMachine_FrameDict* state_args;
    MealyMachine_FrameDict* state_vars;
    MealyMachine_FrameDict* enter_args;
    MealyMachine_FrameDict* exit_args;
    MealyMachine_FrameEvent* forward_event;
    struct MealyMachine_Compartment* parent_compartment;
} MealyMachine_Compartment;

static MealyMachine_Compartment* MealyMachine_Compartment_new(const char* state) {
    MealyMachine_Compartment* c = malloc(sizeof(MealyMachine_Compartment));
    c->state = state;
    c->state_args = MealyMachine_FrameDict_new();
    c->state_vars = MealyMachine_FrameDict_new();
    c->enter_args = MealyMachine_FrameDict_new();
    c->exit_args = MealyMachine_FrameDict_new();
    c->forward_event = NULL;
    c->parent_compartment = NULL;
    return c;
}

static MealyMachine_Compartment* MealyMachine_Compartment_copy(MealyMachine_Compartment* src) {
    MealyMachine_Compartment* c = malloc(sizeof(MealyMachine_Compartment));
    c->state = src->state;
    c->state_args = MealyMachine_FrameDict_copy(src->state_args);
    c->state_vars = MealyMachine_FrameDict_copy(src->state_vars);
    c->enter_args = MealyMachine_FrameDict_copy(src->enter_args);
    c->exit_args = MealyMachine_FrameDict_copy(src->exit_args);
    c->forward_event = src->forward_event;  // Shallow copy OK
    c->parent_compartment = src->parent_compartment;
    return c;
}

static void MealyMachine_Compartment_destroy(MealyMachine_Compartment* c) {
    MealyMachine_FrameDict_destroy(c->state_args);
    MealyMachine_FrameDict_destroy(c->state_vars);
    MealyMachine_FrameDict_destroy(c->enter_args);
    MealyMachine_FrameDict_destroy(c->exit_args);
    free(c);
}

// Helper macros for context access
#define MealyMachine_CTX(self) ((MealyMachine_FrameContext*)MealyMachine_FrameVec_last((self)->_context_stack))
#define MealyMachine_PARAM(self, key) MealyMachine_FrameDict_get(MealyMachine_CTX(self)->event->_parameters, key)
#define MealyMachine_RETURN(self) MealyMachine_CTX(self)->_return
#define MealyMachine_DATA(self, key) MealyMachine_FrameDict_get(MealyMachine_CTX(self)->_data, key)
#define MealyMachine_DATA_SET(self, key, val) MealyMachine_FrameDict_set(MealyMachine_CTX(self)->_data, key, val)

// Forward declarations
typedef struct MealyMachine MealyMachine;
static void MealyMachine_kernel(MealyMachine* self, MealyMachine_FrameEvent* __e);
static void MealyMachine_router(MealyMachine* self, MealyMachine_FrameEvent* __e);
static void MealyMachine_transition(MealyMachine* self, MealyMachine_Compartment* next);
static void MealyMachine_state_Q1(MealyMachine* self, MealyMachine_FrameEvent* __e);
static void MealyMachine_state_Q2(MealyMachine* self, MealyMachine_FrameEvent* __e);
static void MealyMachine_state_Q0(MealyMachine* self, MealyMachine_FrameEvent* __e);
void MealyMachine_i_0 (MealyMachine* self);
void MealyMachine_i_1 (MealyMachine* self);
void MealyMachine_emit_output (MealyMachine* self, int value);
int MealyMachine_get_last_output (MealyMachine* self);

struct MealyMachine {
    MealyMachine_FrameVec* _state_stack;
    MealyMachine_Compartment* __compartment;
    MealyMachine_Compartment* __next_compartment;
    MealyMachine_FrameVec* _context_stack;
    int last_output;
};

MealyMachine* MealyMachine_new(void) {
    MealyMachine* self = malloc(sizeof(MealyMachine));
    self->_state_stack = MealyMachine_FrameVec_new();
    self->_context_stack = MealyMachine_FrameVec_new();
    self->__compartment = MealyMachine_Compartment_new("Q0");
    self->__next_compartment = NULL;
    MealyMachine_FrameEvent* __frame_event = MealyMachine_FrameEvent_new("$>", NULL);
    MealyMachine_kernel(self, __frame_event);
    MealyMachine_FrameEvent_destroy(__frame_event);
    return self;
}

static void MealyMachine_kernel(MealyMachine* self, MealyMachine_FrameEvent* __e) {
    // Route event to current state
    MealyMachine_router(self, __e);
    // Process any pending transition
    while (self->__next_compartment != NULL) {
        MealyMachine_Compartment* next_compartment = self->__next_compartment;
        self->__next_compartment = NULL;
        // Exit current state (with exit_args from current compartment)
        MealyMachine_FrameEvent* exit_event = MealyMachine_FrameEvent_new("<$", self->__compartment->exit_args);
        MealyMachine_router(self, exit_event);
        MealyMachine_FrameEvent_destroy(exit_event);
        // Switch to new compartment
        MealyMachine_Compartment_destroy(self->__compartment);
        self->__compartment = next_compartment;
        // Enter new state (or forward event)
        if (next_compartment->forward_event == NULL) {
            MealyMachine_FrameEvent* enter_event = MealyMachine_FrameEvent_new("$>", self->__compartment->enter_args);
            MealyMachine_router(self, enter_event);
            MealyMachine_FrameEvent_destroy(enter_event);
        } else {
            // Forward event to new state
            // Note: forward_event is a borrowed pointer to the caller's __e, do NOT destroy it
            MealyMachine_FrameEvent* forward_event = next_compartment->forward_event;
            next_compartment->forward_event = NULL;
            if (strcmp(forward_event->_message, "$>") == 0) {
                // Forwarding enter event - just send it
                MealyMachine_router(self, forward_event);
            } else {
                // Forwarding other event - send $> first, then forward
                MealyMachine_FrameEvent* enter_event = MealyMachine_FrameEvent_new("$>", self->__compartment->enter_args);
                MealyMachine_router(self, enter_event);
                MealyMachine_FrameEvent_destroy(enter_event);
                MealyMachine_router(self, forward_event);
            }
            // Do NOT destroy forward_event - it's owned by the interface method caller
        }
    }
}

static void MealyMachine_router(MealyMachine* self, MealyMachine_FrameEvent* __e) {
    const char* state_name = self->__compartment->state;
    if (strcmp(state_name, "Q0") == 0) {
        MealyMachine_state_Q0(self, __e);
    } else if (strcmp(state_name, "Q1") == 0) {
        MealyMachine_state_Q1(self, __e);
    } else if (strcmp(state_name, "Q2") == 0) {
        MealyMachine_state_Q2(self, __e);
    }
}

static void MealyMachine_transition(MealyMachine* self, MealyMachine_Compartment* next_compartment) {
    self->__next_compartment = next_compartment;
}

void MealyMachine_destroy(MealyMachine* self) {
    if (self->__compartment) MealyMachine_Compartment_destroy(self->__compartment);
    if (self->_state_stack) MealyMachine_FrameVec_destroy(self->_state_stack);
    if (self->_context_stack) MealyMachine_FrameVec_destroy(self->_context_stack);
    free(self);
}

void MealyMachine_i_0(MealyMachine* self) {
    MealyMachine_FrameEvent* __e = MealyMachine_FrameEvent_new("i_0", NULL);
    MealyMachine_FrameContext* __ctx = MealyMachine_FrameContext_new(__e, NULL);
    MealyMachine_FrameVec_push(self->_context_stack, __ctx);
    MealyMachine_kernel(self, __e);
    MealyMachine_FrameContext* __result_ctx = (MealyMachine_FrameContext*)MealyMachine_FrameVec_pop(self->_context_stack);
    MealyMachine_FrameContext_destroy(__result_ctx);
    MealyMachine_FrameEvent_destroy(__e);
}

void MealyMachine_i_1(MealyMachine* self) {
    MealyMachine_FrameEvent* __e = MealyMachine_FrameEvent_new("i_1", NULL);
    MealyMachine_FrameContext* __ctx = MealyMachine_FrameContext_new(__e, NULL);
    MealyMachine_FrameVec_push(self->_context_stack, __ctx);
    MealyMachine_kernel(self, __e);
    MealyMachine_FrameContext* __result_ctx = (MealyMachine_FrameContext*)MealyMachine_FrameVec_pop(self->_context_stack);
    MealyMachine_FrameContext_destroy(__result_ctx);
    MealyMachine_FrameEvent_destroy(__e);
}

static void MealyMachine_state_Q1(MealyMachine* self, MealyMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "i_0") == 0) {
        MealyMachine_emit_output(self, 0);
        MealyMachine_Compartment* __compartment = MealyMachine_Compartment_new("Q1");
        MealyMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MealyMachine_emit_output(self, 1);
        MealyMachine_Compartment* __compartment = MealyMachine_Compartment_new("Q2");
        MealyMachine_transition(self, __compartment);
        return;
    }
}

static void MealyMachine_state_Q2(MealyMachine* self, MealyMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "i_0") == 0) {
        MealyMachine_emit_output(self, 1);
        MealyMachine_Compartment* __compartment = MealyMachine_Compartment_new("Q1");
        MealyMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MealyMachine_emit_output(self, 0);
        MealyMachine_Compartment* __compartment = MealyMachine_Compartment_new("Q2");
        MealyMachine_transition(self, __compartment);
        return;
    }
}

static void MealyMachine_state_Q0(MealyMachine* self, MealyMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "i_0") == 0) {
        MealyMachine_emit_output(self, 0);
        MealyMachine_Compartment* __compartment = MealyMachine_Compartment_new("Q1");
        MealyMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MealyMachine_emit_output(self, 0);
        MealyMachine_Compartment* __compartment = MealyMachine_Compartment_new("Q2");
        MealyMachine_transition(self, __compartment);
        return;
    }
}

void MealyMachine_emit_output(MealyMachine* self, int value) {
                self->last_output = value;
}

int MealyMachine_get_last_output(MealyMachine* self) {
                return self->last_output;
}


int main() {
    printf("TAP version 14\n");
    printf("1..4\n");

    MealyMachine* m = MealyMachine_new();

    // Test sequence: i_0, i_0, i_1, i_0
    MealyMachine_i_0(m);  // Q0 -> Q1, output 0
    if (MealyMachine_get_last_output(m) == 0) {
        printf("ok 1 - mealy i_0 from Q0 outputs 0\n");
    } else {
        printf("not ok 1 - mealy i_0 from Q0 outputs 0 # got %d\n", MealyMachine_get_last_output(m));
    }

    MealyMachine_i_0(m);  // Q1 -> Q1, output 0
    if (MealyMachine_get_last_output(m) == 0) {
        printf("ok 2 - mealy i_0 from Q1 outputs 0\n");
    } else {
        printf("not ok 2 - mealy i_0 from Q1 outputs 0 # got %d\n", MealyMachine_get_last_output(m));
    }

    MealyMachine_i_1(m);  // Q1 -> Q2, output 1
    if (MealyMachine_get_last_output(m) == 1) {
        printf("ok 3 - mealy i_1 from Q1 outputs 1\n");
    } else {
        printf("not ok 3 - mealy i_1 from Q1 outputs 1 # got %d\n", MealyMachine_get_last_output(m));
    }

    MealyMachine_i_0(m);  // Q2 -> Q1, output 1
    if (MealyMachine_get_last_output(m) == 1) {
        printf("ok 4 - mealy i_0 from Q2 outputs 1\n");
    } else {
        printf("not ok 4 - mealy i_0 from Q2 outputs 1 # got %d\n", MealyMachine_get_last_output(m));
    }

    printf("# PASS - Mealy machine outputs depend on state AND input\n");

    MealyMachine_destroy(m);
    return 0;
}

