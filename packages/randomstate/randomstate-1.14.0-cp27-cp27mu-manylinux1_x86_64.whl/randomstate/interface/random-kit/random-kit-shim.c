#include "random-kit-shim.h"
#include "random-kit-poly.h"

extern NPY_INLINE uint32_t random_uint32(aug_state *state);

extern NPY_INLINE uint64_t random_uint64(aug_state *state);

extern NPY_INLINE uint64_t random_raw_values(aug_state *state);

extern NPY_INLINE double random_double(aug_state *state);

void set_seed_by_array(aug_state *state, uint32_t *init_key, int key_length) {
  randomkit_init_by_array(state->rng, init_key, key_length);
}

void set_seed(aug_state *state, uint32_t seed) {
  randomkit_seed(state->rng, seed);
}

void entropy_init(aug_state *state) {
  uint32_t seeds[1];
  entropy_fill((void *)seeds, sizeof(seeds));
  set_seed(state, seeds[0]);
}

void jump_state(aug_state *state) { randomkit_jump(state->rng, poly); }