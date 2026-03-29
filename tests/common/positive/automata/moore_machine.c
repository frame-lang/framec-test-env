
#include <stdio.h>
#include <stdint.h>

// Moore Machine - output depends ONLY on state (output on entry)
// See: https://www.geeksforgeeks.org/mealy-and-moore-machines-in-toc/

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

// ============================================================================
// MooreMachine_FrameDict - String-keyed dictionary
// ============================================================================

typedef struct MooreMachine_FrameDictEntry {
    char* key;
    void* value;
    struct MooreMachine_FrameDictEntry* next;
} MooreMachine_FrameDictEntry;

typedef struct {
    MooreMachine_FrameDictEntry** buckets;
    int bucket_count;
    int size;
} MooreMachine_FrameDict;

static unsigned int MooreMachine_hash_string(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

static MooreMachine_FrameDict* MooreMachine_FrameDict_new(void) {
    MooreMachine_FrameDict* d = malloc(sizeof(MooreMachine_FrameDict));
    d->bucket_count = 16;
    d->buckets = calloc(d->bucket_count, sizeof(MooreMachine_FrameDictEntry*));
    d->size = 0;
    return d;
}

static void MooreMachine_FrameDict_set(MooreMachine_FrameDict* d, const char* key, void* value) {
    unsigned int idx = MooreMachine_hash_string(key) % d->bucket_count;
    MooreMachine_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            entry->value = value;
            return;
        }
        entry = entry->next;
    }
    MooreMachine_FrameDictEntry* new_entry = malloc(sizeof(MooreMachine_FrameDictEntry));
    new_entry->key = strdup(key);
    new_entry->value = value;
    new_entry->next = d->buckets[idx];
    d->buckets[idx] = new_entry;
    d->size++;
}

static void* MooreMachine_FrameDict_get(MooreMachine_FrameDict* d, const char* key) {
    unsigned int idx = MooreMachine_hash_string(key) % d->bucket_count;
    MooreMachine_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return entry->value;
        }
        entry = entry->next;
    }
    return NULL;
}

static int MooreMachine_FrameDict_has(MooreMachine_FrameDict* d, const char* key) {
    unsigned int idx = MooreMachine_hash_string(key) % d->bucket_count;
    MooreMachine_FrameDictEntry* entry = d->buckets[idx];
    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return 1;
        }
        entry = entry->next;
    }
    return 0;
}

static MooreMachine_FrameDict* MooreMachine_FrameDict_copy(MooreMachine_FrameDict* src) {
    MooreMachine_FrameDict* dst = MooreMachine_FrameDict_new();
    for (int i = 0; i < src->bucket_count; i++) {
        MooreMachine_FrameDictEntry* entry = src->buckets[i];
        while (entry) {
            MooreMachine_FrameDict_set(dst, entry->key, entry->value);
            entry = entry->next;
        }
    }
    return dst;
}

static void MooreMachine_FrameDict_destroy(MooreMachine_FrameDict* d) {
    for (int i = 0; i < d->bucket_count; i++) {
        MooreMachine_FrameDictEntry* entry = d->buckets[i];
        while (entry) {
            MooreMachine_FrameDictEntry* next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    free(d->buckets);
    free(d);
}

// ============================================================================
// MooreMachine_FrameVec - Dynamic array
// ============================================================================

typedef struct {
    void** items;
    int size;
    int capacity;
} MooreMachine_FrameVec;

static MooreMachine_FrameVec* MooreMachine_FrameVec_new(void) {
    MooreMachine_FrameVec* v = malloc(sizeof(MooreMachine_FrameVec));
    v->capacity = 8;
    v->size = 0;
    v->items = malloc(sizeof(void*) * v->capacity);
    return v;
}

static void MooreMachine_FrameVec_push(MooreMachine_FrameVec* v, void* item) {
    if (v->size >= v->capacity) {
        v->capacity *= 2;
        v->items = realloc(v->items, sizeof(void*) * v->capacity);
    }
    v->items[v->size++] = item;
}

static void* MooreMachine_FrameVec_pop(MooreMachine_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[--v->size];
}

static void* MooreMachine_FrameVec_last(MooreMachine_FrameVec* v) {
    if (v->size == 0) return NULL;
    return v->items[v->size - 1];
}

static void* MooreMachine_FrameVec_get(MooreMachine_FrameVec* v, int index) {
    if (index < 0 || index >= v->size) return NULL;
    return v->items[index];
}

static int MooreMachine_FrameVec_size(MooreMachine_FrameVec* v) {
    return v->size;
}

static void MooreMachine_FrameVec_destroy(MooreMachine_FrameVec* v) {
    free(v->items);
    free(v);
}

// ============================================================================
// MooreMachine_FrameEvent - Event routing object
// ============================================================================

typedef struct {
    const char* _message;
    MooreMachine_FrameDict* _parameters;
} MooreMachine_FrameEvent;

static MooreMachine_FrameEvent* MooreMachine_FrameEvent_new(const char* message, MooreMachine_FrameDict* parameters) {
    MooreMachine_FrameEvent* e = malloc(sizeof(MooreMachine_FrameEvent));
    e->_message = message;
    e->_parameters = parameters;
    return e;
}

static void MooreMachine_FrameEvent_destroy(MooreMachine_FrameEvent* e) {
    // Note: _parameters ownership depends on context
    free(e);
}

// ============================================================================
// MooreMachine_FrameContext - Interface call context
// ============================================================================

typedef struct {
    MooreMachine_FrameEvent* event;
    void* _return;
    MooreMachine_FrameDict* _data;
} MooreMachine_FrameContext;

static MooreMachine_FrameContext* MooreMachine_FrameContext_new(MooreMachine_FrameEvent* event, void* default_return) {
    MooreMachine_FrameContext* ctx = malloc(sizeof(MooreMachine_FrameContext));
    ctx->event = event;
    ctx->_return = default_return;
    ctx->_data = MooreMachine_FrameDict_new();
    return ctx;
}

static void MooreMachine_FrameContext_destroy(MooreMachine_FrameContext* ctx) {
    MooreMachine_FrameDict_destroy(ctx->_data);
    free(ctx);
}

// ============================================================================
// MooreMachine_Compartment - State closure
// ============================================================================

typedef struct MooreMachine_Compartment {
    const char* state;
    MooreMachine_FrameDict* state_args;
    MooreMachine_FrameDict* state_vars;
    MooreMachine_FrameDict* enter_args;
    MooreMachine_FrameDict* exit_args;
    MooreMachine_FrameEvent* forward_event;
    struct MooreMachine_Compartment* parent_compartment;
} MooreMachine_Compartment;

static MooreMachine_Compartment* MooreMachine_Compartment_new(const char* state) {
    MooreMachine_Compartment* c = malloc(sizeof(MooreMachine_Compartment));
    c->state = state;
    c->state_args = MooreMachine_FrameDict_new();
    c->state_vars = MooreMachine_FrameDict_new();
    c->enter_args = MooreMachine_FrameDict_new();
    c->exit_args = MooreMachine_FrameDict_new();
    c->forward_event = NULL;
    c->parent_compartment = NULL;
    return c;
}

static MooreMachine_Compartment* MooreMachine_Compartment_copy(MooreMachine_Compartment* src) {
    MooreMachine_Compartment* c = malloc(sizeof(MooreMachine_Compartment));
    c->state = src->state;
    c->state_args = MooreMachine_FrameDict_copy(src->state_args);
    c->state_vars = MooreMachine_FrameDict_copy(src->state_vars);
    c->enter_args = MooreMachine_FrameDict_copy(src->enter_args);
    c->exit_args = MooreMachine_FrameDict_copy(src->exit_args);
    c->forward_event = src->forward_event;  // Shallow copy OK
    c->parent_compartment = src->parent_compartment;
    return c;
}

static void MooreMachine_Compartment_destroy(MooreMachine_Compartment* c) {
    MooreMachine_FrameDict_destroy(c->state_args);
    MooreMachine_FrameDict_destroy(c->state_vars);
    MooreMachine_FrameDict_destroy(c->enter_args);
    MooreMachine_FrameDict_destroy(c->exit_args);
    free(c);
}

// Helper macros for context access
#define MooreMachine_CTX(self) ((MooreMachine_FrameContext*)MooreMachine_FrameVec_last((self)->_context_stack))
#define MooreMachine_PARAM(self, key) MooreMachine_FrameDict_get(MooreMachine_CTX(self)->event->_parameters, key)
#define MooreMachine_RETURN(self) MooreMachine_CTX(self)->_return
#define MooreMachine_DATA(self, key) MooreMachine_FrameDict_get(MooreMachine_CTX(self)->_data, key)
#define MooreMachine_DATA_SET(self, key, val) MooreMachine_FrameDict_set(MooreMachine_CTX(self)->_data, key, val)

// Forward declarations
typedef struct MooreMachine MooreMachine;
static void MooreMachine_kernel(MooreMachine* self, MooreMachine_FrameEvent* __e);
static void MooreMachine_router(MooreMachine* self, MooreMachine_FrameEvent* __e);
static void MooreMachine_transition(MooreMachine* self, MooreMachine_Compartment* next);
static void MooreMachine_state_Q1(MooreMachine* self, MooreMachine_FrameEvent* __e);
static void MooreMachine_state_Q0(MooreMachine* self, MooreMachine_FrameEvent* __e);
static void MooreMachine_state_Q4(MooreMachine* self, MooreMachine_FrameEvent* __e);
static void MooreMachine_state_Q2(MooreMachine* self, MooreMachine_FrameEvent* __e);
static void MooreMachine_state_Q3(MooreMachine* self, MooreMachine_FrameEvent* __e);
void MooreMachine_i_0 (MooreMachine* self);
void MooreMachine_i_1 (MooreMachine* self);
void MooreMachine_set_output (MooreMachine* self, int value);
int MooreMachine_get_output (MooreMachine* self);

struct MooreMachine {
    MooreMachine_FrameVec* _state_stack;
    MooreMachine_Compartment* __compartment;
    MooreMachine_Compartment* __next_compartment;
    MooreMachine_FrameVec* _context_stack;
    int current_output;
};

MooreMachine* MooreMachine_new(void) {
    MooreMachine* self = malloc(sizeof(MooreMachine));
    self->_state_stack = MooreMachine_FrameVec_new();
    self->_context_stack = MooreMachine_FrameVec_new();
    self->__compartment = MooreMachine_Compartment_new("Q0");
    self->__next_compartment = NULL;
    MooreMachine_FrameEvent* __frame_event = MooreMachine_FrameEvent_new("$>", NULL);
    MooreMachine_kernel(self, __frame_event);
    MooreMachine_FrameEvent_destroy(__frame_event);
    return self;
}

static void MooreMachine_kernel(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    // Route event to current state
    MooreMachine_router(self, __e);
    // Process any pending transition
    while (self->__next_compartment != NULL) {
        MooreMachine_Compartment* next_compartment = self->__next_compartment;
        self->__next_compartment = NULL;
        // Exit current state (with exit_args from current compartment)
        MooreMachine_FrameEvent* exit_event = MooreMachine_FrameEvent_new("<$", self->__compartment->exit_args);
        MooreMachine_router(self, exit_event);
        MooreMachine_FrameEvent_destroy(exit_event);
        // Switch to new compartment
        MooreMachine_Compartment_destroy(self->__compartment);
        self->__compartment = next_compartment;
        // Enter new state (or forward event)
        if (next_compartment->forward_event == NULL) {
            MooreMachine_FrameEvent* enter_event = MooreMachine_FrameEvent_new("$>", self->__compartment->enter_args);
            MooreMachine_router(self, enter_event);
            MooreMachine_FrameEvent_destroy(enter_event);
        } else {
            // Forward event to new state
            // Note: forward_event is a borrowed pointer to the caller's __e, do NOT destroy it
            MooreMachine_FrameEvent* forward_event = next_compartment->forward_event;
            next_compartment->forward_event = NULL;
            if (strcmp(forward_event->_message, "$>") == 0) {
                // Forwarding enter event - just send it
                MooreMachine_router(self, forward_event);
            } else {
                // Forwarding other event - send $> first, then forward
                MooreMachine_FrameEvent* enter_event = MooreMachine_FrameEvent_new("$>", self->__compartment->enter_args);
                MooreMachine_router(self, enter_event);
                MooreMachine_FrameEvent_destroy(enter_event);
                MooreMachine_router(self, forward_event);
            }
            // Do NOT destroy forward_event - it's owned by the interface method caller
        }
    }
}

static void MooreMachine_router(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    const char* state_name = self->__compartment->state;
    if (strcmp(state_name, "Q0") == 0) {
        MooreMachine_state_Q0(self, __e);
    } else if (strcmp(state_name, "Q1") == 0) {
        MooreMachine_state_Q1(self, __e);
    } else if (strcmp(state_name, "Q2") == 0) {
        MooreMachine_state_Q2(self, __e);
    } else if (strcmp(state_name, "Q3") == 0) {
        MooreMachine_state_Q3(self, __e);
    } else if (strcmp(state_name, "Q4") == 0) {
        MooreMachine_state_Q4(self, __e);
    }
}

static void MooreMachine_transition(MooreMachine* self, MooreMachine_Compartment* next_compartment) {
    self->__next_compartment = next_compartment;
}

void MooreMachine_destroy(MooreMachine* self) {
    if (self->__compartment) MooreMachine_Compartment_destroy(self->__compartment);
    if (self->_state_stack) MooreMachine_FrameVec_destroy(self->_state_stack);
    if (self->_context_stack) MooreMachine_FrameVec_destroy(self->_context_stack);
    free(self);
}

void MooreMachine_i_0(MooreMachine* self) {
    MooreMachine_FrameEvent* __e = MooreMachine_FrameEvent_new("i_0", NULL);
    MooreMachine_FrameContext* __ctx = MooreMachine_FrameContext_new(__e, NULL);
    MooreMachine_FrameVec_push(self->_context_stack, __ctx);
    MooreMachine_kernel(self, __e);
    MooreMachine_FrameContext* __result_ctx = (MooreMachine_FrameContext*)MooreMachine_FrameVec_pop(self->_context_stack);
    MooreMachine_FrameContext_destroy(__result_ctx);
    MooreMachine_FrameEvent_destroy(__e);
}

void MooreMachine_i_1(MooreMachine* self) {
    MooreMachine_FrameEvent* __e = MooreMachine_FrameEvent_new("i_1", NULL);
    MooreMachine_FrameContext* __ctx = MooreMachine_FrameContext_new(__e, NULL);
    MooreMachine_FrameVec_push(self->_context_stack, __ctx);
    MooreMachine_kernel(self, __e);
    MooreMachine_FrameContext* __result_ctx = (MooreMachine_FrameContext*)MooreMachine_FrameVec_pop(self->_context_stack);
    MooreMachine_FrameContext_destroy(__result_ctx);
    MooreMachine_FrameEvent_destroy(__e);
}

static void MooreMachine_state_Q1(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "$>") == 0) {
        MooreMachine_set_output(self, 0);
    } else if (strcmp(__e->_message, "i_0") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q1");
        MooreMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q3");
        MooreMachine_transition(self, __compartment);
        return;
    }
}

static void MooreMachine_state_Q0(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "$>") == 0) {
        MooreMachine_set_output(self, 0);
    } else if (strcmp(__e->_message, "i_0") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q1");
        MooreMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q2");
        MooreMachine_transition(self, __compartment);
        return;
    }
}

static void MooreMachine_state_Q4(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "$>") == 0) {
        MooreMachine_set_output(self, 1);
    } else if (strcmp(__e->_message, "i_0") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q1");
        MooreMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q3");
        MooreMachine_transition(self, __compartment);
        return;
    }
}

static void MooreMachine_state_Q2(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "$>") == 0) {
        MooreMachine_set_output(self, 0);
    } else if (strcmp(__e->_message, "i_0") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q4");
        MooreMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q2");
        MooreMachine_transition(self, __compartment);
        return;
    }
}

static void MooreMachine_state_Q3(MooreMachine* self, MooreMachine_FrameEvent* __e) {
    if (strcmp(__e->_message, "$>") == 0) {
        MooreMachine_set_output(self, 1);
    } else if (strcmp(__e->_message, "i_0") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q4");
        MooreMachine_transition(self, __compartment);
        return;
    } else if (strcmp(__e->_message, "i_1") == 0) {
        MooreMachine_Compartment* __compartment = MooreMachine_Compartment_new("Q2");
        MooreMachine_transition(self, __compartment);
        return;
    }
}

void MooreMachine_set_output(MooreMachine* self, int value) {
                self->current_output = value;
}

int MooreMachine_get_output(MooreMachine* self) {
                return self->current_output;
}


int main() {
    printf("TAP version 14\n");
    printf("1..5\n");

    MooreMachine* m = MooreMachine_new();

    // Initial state Q0 has output 0
    if (MooreMachine_get_output(m) == 0) {
        printf("ok 1 - moore initial state Q0 has output 0\n");
    } else {
        printf("not ok 1 - moore initial state Q0 has output 0 # got %d\n", MooreMachine_get_output(m));
    }

    // i_0: Q0 -> Q1 (output 0)
    MooreMachine_i_0(m);
    if (MooreMachine_get_output(m) == 0) {
        printf("ok 2 - moore Q1 has output 0\n");
    } else {
        printf("not ok 2 - moore Q1 has output 0 # got %d\n", MooreMachine_get_output(m));
    }

    // i_1: Q1 -> Q3 (output 1)
    MooreMachine_i_1(m);
    if (MooreMachine_get_output(m) == 1) {
        printf("ok 3 - moore Q3 has output 1\n");
    } else {
        printf("not ok 3 - moore Q3 has output 1 # got %d\n", MooreMachine_get_output(m));
    }

    // i_0: Q3 -> Q4 (output 1)
    MooreMachine_i_0(m);
    if (MooreMachine_get_output(m) == 1) {
        printf("ok 4 - moore Q4 has output 1\n");
    } else {
        printf("not ok 4 - moore Q4 has output 1 # got %d\n", MooreMachine_get_output(m));
    }

    // i_0: Q4 -> Q1 (output 0)
    MooreMachine_i_0(m);
    if (MooreMachine_get_output(m) == 0) {
        printf("ok 5 - moore Q1 has output 0 again\n");
    } else {
        printf("not ok 5 - moore Q1 has output 0 again # got %d\n", MooreMachine_get_output(m));
    }

    printf("# PASS - Moore machine outputs depend ONLY on state\n");

    MooreMachine_destroy(m);
    return 0;
}

